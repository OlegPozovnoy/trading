import pandas as pd
import sql.get_table

query = """
select * 
	from public.orders_auto oa
left join
	(select * from
	(SELECT row_number() over(PARTITION BY d.code order by order_id desc) as last_order, d.*
		FROM public.deorders d) d
	where last_order = 1) orders
on oa.code = orders.code
inner join public.futquotes fq 
on oa.code = fq.code 

"""

s = pd.DataFrame(sql.get_table.exec_query(query))
print(s)