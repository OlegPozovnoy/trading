import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, \
    GlobalAveragePooling1D, LeakyReLU, LSTM, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from catboost import CatBoostRegressor, Pool
import numpy as np
from losses import CustomCatBoostLoss


# Позиционное кодирование
def positional_encoding(position, d_model):
    angle_rads = get_angles(np.arange(position)[:, np.newaxis],
                            np.arange(d_model)[np.newaxis, :],
                            d_model)
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

    pos_encoding = angle_rads[np.newaxis, ...]
    return tf.cast(pos_encoding, dtype=tf.float32)


def get_angles(pos, i, d_model):
    angle_rates = 1 / np.power(10000, (2 * (i // 2)) / np.float32(d_model))
    return pos * angle_rates


# Трансформерный блок
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0, regularizer=None):
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(x, x)
    x = Dropout(dropout)(x)
    res = x + inputs

    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation="linear", kernel_regularizer=regularizer)(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1], kernel_regularizer=regularizer)(x)
    return x + res


# Модель Transformer
def build_transformer_model(input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout=0,
                            mlp_dropout=0, k=1.0, regularizer=None):
    inputs = Input(shape=input_shape)
    initial_close_input = Input(shape=(1,))

    pos_encoding = positional_encoding(input_shape[0], input_shape[1])
    x = inputs + pos_encoding

    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout, regularizer)

    x = LayerNormalization(epsilon=1e-6)(x)
    x = GlobalAveragePooling1D()(x)
    for dim in mlp_units:
        x = Dense(dim, activation="linear", kernel_regularizer=regularizer)(x)
        x = LeakyReLU(alpha=0.1)(x)
        x = Dropout(mlp_dropout)(x)
    x = Dense(1)(x)

    def transform_predictions(inputs):
        preds, current_close = inputs
        low_diff = k / 10 / tf.exp(preds)
        low_pred = current_close - low_diff
        return tf.concat([low_pred, current_close], axis=1)

    transformed_preds = Lambda(transform_predictions)([x, initial_close_input])

    return Model([inputs, initial_close_input], transformed_preds)


# Модель LSTM
def build_lstm_model(input_shape, units, k, dropout=0.2):
    inputs = Input(shape=input_shape)
    initial_close_input = Input(shape=(1,))

    x = LSTM(units, return_sequences=False)(inputs)
    x = Dropout(dropout)(x)
    x = Dense(1)(x)

    def transform_predictions(inputs):
        preds, current_close = inputs
        low_diff = k / 10 / tf.exp(preds)
        low_pred = current_close - low_diff
        return tf.concat([low_pred, current_close], axis=1)

    transformed_preds = Lambda(transform_predictions)([x, initial_close_input])

    return Model([inputs, initial_close_input], transformed_preds)


# Модель CatBoost с пользовательской функцией потерь
def train_catboost_custom(X_train, y_train, k):
    model = CatBoostRegressor(iterations=500,
                              learning_rate=0.1,
                              depth=6,
                              loss_function=CustomCatBoostLoss(k),  # Использование пользовательской функции потерь
                              verbose=100)
    train_pool = Pool(X_train.reshape(X_train.shape[0], -1), y_train)
    model.fit(train_pool)
    return model
