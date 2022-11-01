import pandas as pd
import pymysql
from datetime import datetime

file = "stock_symbols.csv"

df=pd.read_csv(file, sep=",")

conn = pymysql.connect(
    read_default_file="my.cnf",
    cursorclass=pymysql.cursors.DictCursor
)

with conn:
    with conn.cursor() as cursor:
        for i in range(len(df)):
            sql = "select symbol from stock_stock where symbol=%s"
            cursor.execute(sql, (df.iloc[i, 0]))
            result = cursor.fetchone()
            if not result:
                sql = "insert into stock_stock (symbol, full_name, currency, last_check) values(%s, %s, 'INR', %s)"
                cursor.execute(sql, (df.iloc[i, 0], df.iloc[i, 1], datetime.now()))
                print("inserting: ", df.iloc[i, 0])
    conn.commit()