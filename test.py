import pandas as pd
import sql.get_table

query_fut = "select distinct code from public.futquotes"

query_sec = "select distinct code from public.secquotes"

fut_list = [x[0] for x in sql.get_table.exec_query(query_fut)]
sec_list = [x[0] for x in sql.get_table.exec_query(query_sec)]

setting = f"""
config = {{
    "equities": {{
      "classCode" : "TQBR",
        "secCodes" : {sec_list}
    }},
    "futures":{{
        "classCode": "SPBFUT",
        "secCodes": {fut_list}
    }}
}}
"""

f = open("./Examples/Bars_upd_config.py", "w")
# f is the File Handler
f.write(setting)
print(setting)
