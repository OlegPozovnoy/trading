import llm
from llm.input import  TEXT1
from llm.llm_gpt import get_gpt_action
from llm.llm_yandex import get_yandex_action

print(get_gpt_action(llm.input.TEXT3))
#print(get_yandex_action(llm.input.TEXT3))