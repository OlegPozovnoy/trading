import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        logger_name = record.name
        # Получаем отформатированное сообщение с именем логгера в квадратных скобках
        formatted_msg = f"[{logger_name}] {super().format(record)}"
        return formatted_msg



default_handler = logging.StreamHandler()
default_formatter = CustomFormatter()
default_handler.setFormatter(default_formatter)

root_logger = logging.getLogger()
for logger_name, logger in logging.Logger.manager.loggerDict.items():
    print(logger_name)
    if isinstance(logger, logging.Logger):
        if not logger.handlers:
            # Устанавливаем обработчик по умолчанию для логгера
            logger.addHandler(default_handler)
        else:
            # Если у логгера уже есть обработчики, добавляем форматтер к каждому обработчику
            for handler in logger.handlers:
                handler.setFormatter(default_formatter)
