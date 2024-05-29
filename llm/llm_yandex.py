import os

import requests
from dotenv import load_dotenv, find_dotenv

from llm import get_prompt
from tools.utils import sync_timed

load_dotenv(find_dotenv('../my.env', True))

#yandexgpt
#yandexgpt-lite
@sync_timed()
def get_yandex_action(text, model='yandexgpt'):
    prompt = {
        "modelUri": f"gpt://{os.environ['YaGPTFolder']}/{model}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.0,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты умный ассистент"
            },
            {
                "role": "user",
                "text": get_prompt(text)
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {os.environ['YaGPTKey']}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    return response.text
