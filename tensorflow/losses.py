import tensorflow as tf
import numpy as np


# Вычисление стандартного отклонения k
def calculate_k(initial_close_train, y_train):
    return tf.math.reduce_std(initial_close_train - y_train[:, 0]).numpy()


# Определение функции потерь для тренировки
def custom_loss_low_train(y_true, y_pred, k):
    low_true, close_true = y_true[:, 0], y_true[:, 1]
    low_pred, current_close = y_pred[:, 0], y_pred[:, 1]

    low_loss = tf.where(low_pred < low_true,
                        (close_true - current_close) + tf.square(low_true - low_pred) / tf.square(k),
                        low_pred - current_close)

    total_loss = tf.reduce_mean(low_loss)

    return total_loss


# Определение функции потерь для валидации
def custom_loss_low_val(y_true, y_pred):
    low_true, close_true = y_true[:, 0], y_true[:, 1]
    low_pred, current_close = y_pred[:, 0], y_pred[:, 1]

    low_loss = tf.where(low_pred < low_true,
                        (close_true - current_close),
                        low_pred - current_close)

    total_loss = tf.reduce_mean(low_loss)

    return total_loss


# Определение функции потерь для CatBoost
class CustomCatBoostLoss:
    def __init__(self, k):
        self.k = k

    def calc_ders_range(self, approxes, targets, weights):
        assert len(approxes) == len(targets)
        if weights is None:
            weights = np.ones_like(targets)

        ders = []
        for approx, target, weight in zip(approxes, targets, weights):
            low_true, close_true, current_close = target
            low_pred = approx

            if low_pred < low_true:
                loss = (close_true - current_close) + (low_true - low_pred) ** 2 / self.k ** 2
                gradient = -2 * (low_true - low_pred) / self.k ** 2
                hessian = 2 / self.k ** 2
            else:
                loss = low_pred - current_close
                gradient = 1
                hessian = 0

            ders.append((weight * gradient, weight * hessian))

        return ders
