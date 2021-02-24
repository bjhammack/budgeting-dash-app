import pandas as pd
import sqlite3

class Database(object):
	def __init__(self, db='dash_suite.db', user='ALL'):
		self.conn = sqlite3.connect(db)
		self.cursor = self.conn.cursor()

	def create_empty_table(self, table_name, column_dtype_dict):
		drop_table_sql = f'DROP TABLE IF EXISTS {table_name}'
		self.cursor.execute(drop_table_sql)

		column_dtype_str = ', '.join([f'{k} {v}' for k,v in column_dtype_dict.items()])

		create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name}({column_dtype_str})'

		self.cursor.execute(create_table_sql)

	def insert_df(self, df, table_name, append=False):
		if append:
			if_exists = 'append'
		else:
			if_exists = 'replace'
		df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)

	def close(self):
		self.conn.close()