import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, Add, Lambda, \
    GlobalAveragePooling1D, LeakyReLU, LSTM
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import LambdaCallback
from tensorflow.keras.regularizers import l2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sql.get_table  # Добавлен импорт для sql.get_table
from catboost import CatBoostRegressor, Pool

# Выбор модели: 'lstm', 'catboost', 'transformer'
model_type = 'lstm'

# Получение данных из базы данных PostgreSQL
query = """SELECT high, low, close, volume, DATE(datetime) as date
           FROM public.df_all_candles_t_arch 
           WHERE security = 'MXM4' 
           ORDER BY datetime asc"""
df = sql.get_table.query_to_df(query)


# Пример подготовки данных (убираем open)
def prepare_data(df, lookback=15):
    X, y, initial_close = [], [], []
    grouped = df.groupby('date')
    for name, group in grouped:
        group = group.reset_index(drop=True)
        if len(group) > lookback + 5:
            for i in range(lookback, len(group) - 5):
                if group[['close', 'high', 'low', 'volume']].iloc[i - lookback:i].isnull().values.any():
                    continue  # пропускаем, если есть NaN значения
                X.append(group[['close', 'high', 'low', 'volume']].iloc[i - lookback:i].values.astype(np.float32))
                low = group['low'].iloc[i + 1:i + 6].min()  # минимальное значение low за следующие 5 минут
                close = group['close'].iloc[i + 5]  # значение close через 5 минут
                y.append([low, close])
                initial_close.append(group['close'].iloc[i - 1])  # добавляем последнее известное значение закрытия
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32), np.array(initial_close, dtype=np.float32)


# Подготовка данных
X, y, initial_close = prepare_data(df)

# Нормализация данных
X_mean = np.mean(X, axis=(0, 1))
X_std = np.std(X, axis=(0, 1))
X = (X - X_mean) / X_std

# Разделение данных на тренировочные и валидационные наборы по последним 2 дням
df_dates = df['date'].unique()
train_dates = df_dates[:-2]
val_dates = df_dates[-2:]

train_mask = df['date'].isin(train_dates)
val_mask = df['date'].isin(val_dates)

X_train, y_train, initial_close_train = prepare_data(df[df['date'].isin(train_dates)])
X_val, y_val, initial_close_val = prepare_data(df[df['date'].isin(val_dates)])

# Нормализация данных
X_train = (X_train - X_mean) / X_std
X_val = (X_val - X_mean) / X_std

# Проверка данных на наличие NaN и их формы
print("Train Data Shape:", X_train.shape, y_train.shape, initial_close_train.shape)
print("Validation Data Shape:", X_val.shape, y_val.shape, initial_close_val.shape)
print("NaNs in Train Data:", np.isnan(X_train).sum(), np.isnan(y_train).sum(), np.isnan(initial_close_train).sum())
print("NaNs in Validation Data:", np.isnan(X_val).sum(), np.isnan(y_val).sum(), np.isnan(initial_close_val).sum())

# Вычисление стандартного отклонения k один раз перед обучением
k = tf.math.reduce_std(initial_close_train - y_train[:, 0]).numpy()
print("Calculated standard deviation k:", k)


# Позиционное кодирование
def positional_encoding(position, d_model):
    angle_rads = get_angles(np.arange(position)[:, np.newaxis],
                            np.arange(d_model)[np.newaxis, :],
                            d_model)
    # apply sin to even indices in the array; 2i
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
    # apply cos to odd indices in the array; 2i+1
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])

    pos_encoding = angle_rads[np.newaxis, ...]
    return tf.cast(pos_encoding, dtype=tf.float32)


def get_angles(pos, i, d_model):
    angle_rates = 1 / np.power(10000, (2 * (i // 2)) / np.float32(d_model))
    return pos * angle_rates


# Создание улучшенной модели для Transformer
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0, regularizer=None):
    # Normalization and Attention
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout)(x, x)
    x = Dropout(dropout)(x)
    res = x + inputs

    # Feed Forward Part
    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation="linear", kernel_regularizer=regularizer)(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1], kernel_regularizer=regularizer)(x)
    return x + res


def build_transformer_model(input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout=0,
                            mlp_dropout=0, k=1.0, regularizer=None):
    inputs = Input(shape=input_shape)
    initial_close_input = Input(shape=(1,))  # вход для последнего известного значения закрытия

    # Позиционное кодирование
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
    x = Dense(1)(x)  # 1 значение: log(low - current_close)

    # Преобразуем выходные значения для получения необходимых разностей
    def transform_predictions(inputs):
        preds, current_close = inputs
        low_diff = k / 10 / tf.exp(preds)  # k / 10 / exp(preds)
        low_pred = current_close - low_diff
        # print("preds shape:", preds.shape, "current_close shape:", current_close.shape)
        # print("low_diff shape:", low_diff.shape, "low_pred shape:", low_pred.shape)
        return tf.concat([low_pred, current_close], axis=1)

    transformed_preds = Lambda(transform_predictions)([x, initial_close_input])

    # Добавим вывод размерностей
    # print("transformed_preds shape:", transformed_preds.shape)
    # print("initial_close_input shape:", initial_close_input.shape)

    return Model([inputs, initial_close_input], transformed_preds)


# Создание модели LSTM
def build_lstm_model(input_shape, units, dropout=0.2):
    inputs = Input(shape=input_shape)
    initial_close_input = Input(shape=(1,))

    x = LSTM(units, return_sequences=False)(inputs)
    x = Dropout(dropout)(x)
    x = Dense(1)(x)  # 1 значение: log(low - current_close)

    # Преобразуем выходные значения для получения необходимых разностей
    def transform_predictions(inputs):
        preds, current_close = inputs
        low_diff = k / 10 / tf.exp(preds)
        low_pred = current_close - low_diff
        return tf.concat([low_pred, current_close], axis=1)

    transformed_preds = Lambda(transform_predictions)([x, initial_close_input])

    return Model([inputs, initial_close_input], transformed_preds)


# Создание модели CatBoost
def train_catboost(X_train, y_train):
    model = CatBoostRegressor(iterations=500,
                              learning_rate=0.1,
                              depth=6,
                              loss_function='RMSE',
                              verbose=100)
    train_pool = Pool(X_train.reshape(X_train.shape[0], -1), y_train[:, 0])
    model.fit(train_pool)
    return model


# Определение функции потерь для low
def custom_loss_low(y_true, y_pred):
    # print("y_true shape:", y_true.shape, "y_pred shape:", y_pred.shape)
    low_true, close_true = y_true[:, 0], y_true[:, 1]
    low_pred, current_close = y_pred[:, 0], y_pred[:, 1]

    loss_1 = (close_true - current_close) / 10
    loss_2 = tf.square(low_true - low_pred) / tf.square(k)

    total_loss = tf.reduce_mean(loss_1 + loss_2)

    # Отладочный вывод для предсказаний и лоссов
    # tf.print("low_true:", low_true)
    # tf.print("low_pred:", low_pred)
    # tf.print("close_true:", close_true)
    # tf.print("current_close:", current_close)
    # tf.print("loss_1:", loss_1)
    # tf.print("loss_2:", loss_2)
    # tf.print("total_loss:", total_loss)

    return total_loss


# Компиляция и тренировка модели
def compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val):
    model.compile(
        loss=custom_loss_low,
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    )

    # Вывод информации о модели
    model.summary()

    # Callback для вывода значений ошибок на каждой эпохе
    print_callback_low = LambdaCallback(on_epoch_end=lambda epoch, logs: print(
        f"Epoch {epoch + 1}: loss = {logs['loss']}, val_loss = {logs['val_loss']}"))

    # Обучение модели и сохранение истории
    history = model.fit(
        [X_train, initial_close_train], y_train,
        epochs=50,
        batch_size=32,  # увеличен размер батча
        validation_data=([X_val, initial_close_val], y_val),
        callbacks=[print_callback_low]
    )

    # Построение графика лосса
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

    return model


# Выбор модели
if model_type == 'lstm':
    model = build_lstm_model(input_shape=X_train.shape[1:], units=64, dropout=0.2)
    model = compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val)
    model.save('lstm_stock_prediction.h5')
elif model_type == 'catboost':
    model = train_catboost(X_train, y_train)
    print("CatBoost model trained and saved.")
else:
    model = build_transformer_model(
        input_shape=X_train.shape[1:],
        head_size=64,
        num_heads=4,
        ff_dim=128,
        num_transformer_blocks=3,
        mlp_units=[128, 64],
        dropout=0.1,
        mlp_dropout=0.1,
        k=k,
        regularizer=l2(1e-4)
    )
    model = compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val)
    model.save('transformer_stock_prediction_low.h5')
