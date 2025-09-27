import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sql.get_table
from tensorflow.keras.callbacks import LambdaCallback
from losses import custom_loss_low_train, custom_loss_low_val, calculate_k
from models import build_transformer_model, build_lstm_model, train_catboost_custom

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
                if group[['close', 'high', 'low', 'volume']].iloc[i-lookback:i].isnull().values.any():
                    continue  # пропускаем, если есть NaN значения
                X.append(group[['close', 'high', 'low', 'volume']].iloc[i-lookback:i].values.astype(np.float32))
                low = group['low'].iloc[i + 1:i + 6].min()    # минимальное значение low за следующие 5 минут
                close = group['close'].iloc[i + 5]            # значение close через 5 минут
                y.append([low, close, group['close'].iloc[i - 1]])  # добавляем последнее известное значение закрытия
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
k = calculate_k(initial_close_train, y_train)
print("Calculated standard deviation k:", k)

# Компиляция и тренировка модели
def compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val, k):
    model.compile(
        loss=lambda y_true, y_pred: custom_loss_low_train(y_true, y_pred, k),
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    )

    # Вывод информации о модели
    model.summary()

    # Callback для вывода значений ошибок на каждой эпохе
    print_callback_low = LambdaCallback(on_epoch_end=lambda epoch, logs: print(f"Epoch {epoch+1}: loss = {logs['loss']}, val_loss = {logs.get('val_loss', 'N/A')}"))

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
    model = build_lstm_model(input_shape=X_train.shape[1:], units=64, k=k, dropout=0.2)
    model = compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val, k)
    model.save('lstm_stock_prediction.h5')
elif model_type == 'catboost':
    model = train_catboost_custom(X_train, y_train, k)
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
    model = compile_and_train_model(model, X_train, y_train, initial_close_train, X_val, y_val, initial_close_val, k)
    model.save('transformer_stock_prediction_low.h5')
