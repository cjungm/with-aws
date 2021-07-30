from pyhive import hive
import pandas as pd

conn = hive.Connection(host="localhost", port=10000, username="hadoop")

cursor = conn.cursor()
cursor.execute("SELECT * FROM mall_customers")
datas = cursor.fetchall()
columns = datas.pop(0)
data_dict = {}

for col in columns:
    data_dict[col]=[]

for values in datas:
    for idx, value in enumerate(values):
        value=value.strip().replace("\r","")
        if value.isdecimal():
            data_dict[columns[idx]].append(int(value))
        else:
            data_dict[columns[idx]].append(value)

pandas_df = pd.DataFrame(data_dict)
pandas_df.head()
sort_df = pandas_df.sort_values(by=['Spending Score (1-100)'], axis=0)
sort_df.to_csv(
    path_or_buf='/home/hadoop/df_from_python.csv',
    sep=',',
    na_rep='NaN',
    float_format='%.2f',
    header=True,
    index=False
)