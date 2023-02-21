import pandas as pd
import sql.get_table

s = pd.DataFrame(sql.get_table.get_table("public.futquotes"))
print(s)