import datetime
import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from tools.utils import sync_timed

load_dotenv(find_dotenv('../my.env', True))

client = OpenAI(api_key=os.environ['openai_key'])

#<option value="gpt-4-turbo">gpt-4-turbo</option> ---
#<option value="gpt-4o">gpt-4o</option>
#<option value="gpt-3.5-turbo">gpt-3.5-turbo</option>


@sync_timed()
def get_gpt_action(text, model='gpt-3.5-turbo'):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ],
        temperature=0,
    )
    return completion.choices[0].message
