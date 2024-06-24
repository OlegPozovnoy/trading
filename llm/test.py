import llm
from llm.input import TEXT1
from llm.llm_gpt import get_gpt_action
from llm.llm_yandex import get_yandex_action

#<option value="gpt-4-turbo">gpt-4-turbo</option> ---
#<option value="gpt-4o">gpt-4o</option>
#<option value="gpt-3.5-turbo">gpt-3.5-turbo</option>

inference = False

text = (llm.get_prompt(llm.input.TEXT, inference))
res = get_gpt_action(text, model='gpt-3.5-turbo')
print(res.content)
#print(get_yandex_action(text))
