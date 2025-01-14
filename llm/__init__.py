import datetime


def get_prompt(text :str, inference: bool = True) -> str:
    return f"""
    Дан текст автора. Автор-управляющий инвестфондом. Ответь в формате 
    "купить [список акций]" или "продать [список акций]" 
    если автор собирается или уже в интервале +- 5 минут до/после написания поста купить акции или продать акции
    или в тексте есть явное упоминание о том что в ближайшие несколько дней выйдет хороший (тогда формат с купить...) или плохой (тогда формат с продать ...) отчёт компании.
    Если в тексте есть явное упоминание что в ближайшие несколько дней будет решение о выплате дивидендов - то формат с купить.
    Если ты считаешь что автор собирается купить, но вне интервала +- 5 минут до/после написания поста - ответь в формате
    "долгосрочно купить [список акций]" или "долгострочно продать [список акций]"  
    во всех остальных случаях ответь "информация". Будь готов ответить на вопрос, какому из критериев соответствует выбранный формат ответа.
    После ответа в формате дай вероятность с которой ты уверен в выбранном ответе и комментарий по какому из перечисленных критериев и почему выбран этот вариант
    {'.' if not inference else ', но не добавляй это в ответ' }.
    Дата написания текста: {datetime.datetime.now()}. Сам текст: '{text}'
    """

 #Строго соблюдай формат ответа.
