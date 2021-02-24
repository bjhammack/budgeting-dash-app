import os
from datetime import date
import pandas as pd
import numpy as np
import sqlite3

class Data(object):
	def __init__(self, user=None, password=None, db='data/dash_suite.db'):
		self.db = db
		self.conn = None
		self.cursor = None
		self.init_db_connection()

		self.next_invoice_id = int(self.cursor.execute('SELECT max(id) FROM invoices').fetchall()[0][0] + 1)
		self.next_balance_id = int(self.cursor.execute('SELECT max(id) FROM balances').fetchall()[0][0] + 1)
		self.next_user_id = int(self.cursor.execute('SELECT max(id) FROM users').fetchall()[0][0] + 1)

		self.user = user
		self.users = pd.read_sql_query(f"SELECT * FROM users", self.conn)

		invoice_sql = f'''
					SELECT i.*
					FROM invoices i
					LEFT JOIN users u
						ON i.user_id = u.id
					WHERE u.username = '{user}'
					AND u.password = '{password}'
		'''
		balance_sql = f'''
					SELECT b.*
					FROM balances b
					LEFT JOIN users u
						ON b.user_id = u.id
					WHERE u.username = '{user}'
					AND u.password = '{password}'
		'''
		self.invoices = pd.read_sql_query(invoice_sql, self.conn).sort_values(by=['date','category','value'], ascending=False)
		self.balances = pd.read_sql_query(balance_sql, self.conn).sort_values(by='name')
		
		self.user = self.users.loc[self.users['username'].eq(self.user)&self.users['password'].eq(password)]

		self.invoices['date'] = pd.to_datetime(self.invoices['date'])
		self.invoices['year'] = pd.DatetimeIndex(self.invoices['date']).year
		self.invoices['month'] = pd.DatetimeIndex(self.invoices['date']).month
		self.invoices['day'] = pd.DatetimeIndex(self.invoices['date']).day
		self.invoices['value'] = self.invoices['value'].astype(float)
		
		self.balances['funds'] = self.balances['funds'].astype(float)

		self.current_date = date.today()
		self.current_year = self.current_date.year
		self.current_month = self.current_date.month
		self.current_day = self.current_date.day

		self.conn.close()

	def init_db_connection(self):
		try:
			self.conn = sqlite3.connect(self.db)
		except Error as e:
			raise e
		finally:
			if self.conn:
				self.cursor = self.conn.cursor()

	def display_balances(self):
		df = self.balances.loc[:,['name','funds','goal','goal_date']]
		return df

	def display_invoices(self, invoice_type=None):
		if not invoice_type:
			return self.invoices[['date','value','name','category','type']]
		else:
			df = self.invoices.loc[self.invoices['type'].eq(invoice_type.title())][['date','value','name','category','type']]
			return df 

	def new_invoice(self, input_dict=None, is_transfer=False):
		self.init_db_connection()

		value = round(float(input_dict['value']), 2)
		name = input_dict['name'].title()
		category = input_dict['category'].title()
		invoice_type = input_dict['invoice_type'].title()
		balance = input_dict['balance'].title()
		balance_id = int(self.balances.loc[self.balances['name'].eq(balance)]['id'].iloc[0])
		date = input_dict['date']
		user = input_dict['user']
		if date in (None, '', ' '):
			date = self.current_date
		
		if is_transfer:
			to_balance_id = int(self.balances.loc[self.balances['name'].eq(input_dict['to_balance'].title())]['id'].iloc[0])
		else:
			to_balance_id = 'NULL'
		
		insert_sql = f"INSERT INTO invoices VALUES({self.next_invoice_id},'{name}',{value},'{date}'\
					,'{category}','{invoice_type}',{self.user['id'].iloc[0]},{balance_id},{to_balance_id})"
		
		self.cursor.execute(insert_sql)
		self.conn.commit()

		self.next_invoice_id += 1

		if is_transfer:
			self.update_balance(balance, value, 'Expense')
			self.update_balance(input_dict['to_balance'].title(), abs(value), 'Income')	
		else:
			self.update_balance(balance, value, invoice_type)

		self.conn.close()

	def update_balance(self, name=None, new_funds=None, fund_type=None):
		if fund_type == 'Expense':
			new_funds *= -1

		update_sql = f'''
			UPDATE balances
			SET funds = funds + {int(new_funds)}
			WHERE id = {int(self.balances.loc[self.balances.name.eq(name)]['id'].iloc[0])}
		'''
		self.cursor.execute(update_sql)
		self.conn.commit()

	def new_balance(self, input_dict=None):
		self.init_db_connection()

		name = input_dict['name'].title()
		funds = round(float(input_dict['funds']), 2)
		goal = round(float(input_dict['goal']), 2)
		goal_date = input_dict['goal_date']
		if goal_date in (None, '', ' '):
			goal_date = ''
		user = input_dict['user']

		insert_sql = f"INSERT INTO balances VALUES({self.next_balance_id},'{name}',{funds},{goal},'{goal_date}',{self.user['id'].iloc[0]})"
		self.cursor.execute(insert_sql)
		self.conn.commit()

		self.next_balance_id += 1

		self.conn.close()

	def edit_balance(self, input_dict):
		self.init_db_connection()

		cname = input_dict['cname']
		cfunds = input_dict['cfunds']
		cgoal = input_dict['cgoal']
		cgoal_date = input_dict['cgoal_date']
		name = input_dict['name']
		funds = input_dict['funds']
		goal = input_dict['goal']
		goal_date = input_dict['goal_date']
		user = input_dict['user']

		balance_id = self.balances.loc[self.balances['name'].eq(cname) & self.balances['user_id'].eq(self.user['id'].iloc[0])]['id'].iloc[0]

		update_sql = f'''
			UPDATE balances
			SET name = '{name}', funds = {funds}, goal = {goal}, goal_date = '{goal_date}'
			WHERE id = {balance_id};
		'''
		self.cursor.execute(update_sql)
		self.conn.commit()
		self.conn.close()
	
	def annual_summary(self, invoice_type=None, year=None):
		if not year:
			year = self.current_year

		if not invoice_type:
			invoice_type = 'Expense'

		df = self._pivot_categories('year', int(year), invoice_type)

		return df.reset_index()

	def projection_summary(self, invoice_type=None, year=None):
		month_cols = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
		df = self.annual_summary()
		df = df.loc[:].replace('--','0.0')

		for col in month_cols+['Totals']:
			df.loc[:,col] = df.loc[:,col].str.replace(',','')
		
		df.loc[:,month_cols] = df.loc[:,month_cols].astype(float)
		
		for i in range(1,len(month_cols)+1):
			if i > int(self.current_month):
				df.iloc[:,i] = df.iloc[:,1:i].mean(axis=1)
			elif i == int(self.current_month):
				df.iloc[:,i] = df.iloc[:,1:i].mean(axis=1) + abs(df.iloc[:,1:i+1].mean(axis=1) - df.iloc[:,i])

		df.loc[:,'Totals'] = df.iloc[:,1:13].sum(axis=1)
		df.loc[:] = df.loc[:].replace(0,'--')
		df.loc[:,month_cols+['Totals']] = df.loc[:,month_cols+['Totals']].round(2)

		return df

	def net_income(self, year=None):
		if not year:
			year = self.current_year

		df = self.invoices.loc[self.invoices.year.eq(year)]

		df.loc[df.type.eq('Expense'), 'value'] = df.value * -1
		df_gb = df.loc[df.type.isin(('Expense','Income')), ['month','value']].groupby(by='month').sum().reset_index()
		df_gb['net'] = 'Net Income'

		df_pivot = df_gb.loc[:].pivot(index='net',columns='month',values='value')

		cols = [1,2,3,4,5,6,7,8,9,10,11,12]
		for i in cols:
			if i not in list(df_pivot.columns):
				df_pivot[i] = ''

		df_pivot = df_pivot.replace('','--')

		df_pivot = df_pivot.loc[:][cols].rename(columns={1:'Jan',2:'Feb',3:'Mar'\
				,4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})

		df_pivot.loc[:,'Totals']= df_pivot.loc[:].sum(numeric_only=True, axis=1)

		return df_pivot.round(2)

	def _pivot_categories(self, by='year', year=None, invoice_type='expense', month=None):
		if by == 'year':
			df = self.invoices.loc[self.invoices['year'].eq(year) & self.invoices['type'].eq(invoice_type.title())]
			
			summary_df = df.loc[:].sort_values(by=['month','category']).groupby(by=['month','category']).sum().reset_index()
			
			summary_df_pivot = summary_df.loc[:].groupby(['category','month'],as_index=False)['value'].sum().pivot(index='category'\
				,columns='month', values='value').fillna(0.00).reset_index()

			months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Totals']
			cols = ['category',1,2,3,4,5,6,7,8,9,10,11,12]
			for i in cols:
				if i not in list(summary_df_pivot.columns):
					summary_df_pivot[i] = 0
			
			summary_df_pivot[cols[1:]] = summary_df_pivot.loc[:,cols[1:]].apply(pd.to_numeric, errors='coerce')
			summary_df_pivot = summary_df_pivot.loc[:,cols].rename(columns={1:'Jan',2:'Feb',3:'Mar'\
				,4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})

			summary_df_pivot.loc['Totals']= summary_df_pivot.sum(numeric_only=True, axis=0)
			summary_df_pivot.loc[:,'Totals'] = summary_df_pivot.sum(numeric_only=True, axis=1)
			summary_df_pivot = summary_df_pivot.loc[:].fillna('')
			summary_df_pivot.at['Totals', 'category'] = 'Totals'
			
			summary_df_pivot[months] = summary_df_pivot[months].apply(pd.to_numeric, errors='coerce').applymap('{:,.2f}'.format)
			
			summary_df_pivot = summary_df_pivot.loc[:].replace('0.00', '--')

			summary_df_pivot.index = summary_df_pivot['category']
			summary_df_pivot = summary_df_pivot.loc[:].drop(columns=['category'])

			return summary_df_pivot