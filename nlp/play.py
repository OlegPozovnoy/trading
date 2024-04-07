from nlp.mongo_tools import deactivate_channel

deact_list = [
'GBEanalytix'
,'yivashchenko'
,'invest_fynbos'
,'ltrinvestment'
,'rynok_znania'
,'INVESTR_RU'
,'Sharqtradein'
,'Rusbafet_vip'
,'trekinvest'
]


for item in deact_list:
    deactivate_channel(item)