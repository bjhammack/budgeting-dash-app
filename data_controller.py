import os
from datetime import date
import pandas as pd

class Data(object):
	def __init__(self, user=None):
		users = pd.read_csv(f'data/users.csv')
		self.user = user
		if user:
			self.invoices = pd.read_csv(f'data/invoices.csv')
			self.balances = pd.read_csv(f'data/balances.csv')
			
			self.user = users.loc[users['username'].eq(user)]

			self.invoices['Date'] = pd.to_datetime(self.invoices['Date'])
			self.invoices['year'] = pd.DatetimeIndex(self.invoices['Date']).year
			self.invoices['month'] = pd.DatetimeIndex(self.invoices['Date']).month
			self.invoices['day'] = pd.DatetimeIndex(self.invoices['Date']).day
			self.invoices['Value'] = self.invoices['Value'].astype(float)
			
			self.balances['Funds'] = self.balances['Funds'].astype(float)

			self.current_date = date.today()
			self.current_year = self.current_date.year
			self.current_month = self.current_date.month
			self.current_day = self.current_date.day

			self.user_invoices = self.invoices.loc[self.invoices['user'].eq(user)]
			self.user_balances = self.balances.loc[self.balances['user'].eq(user)]
		else:
			self.users = users

	def display_balances(self):
		df = self.user_balances.loc[:,['Name','Funds']]
		return df

	def display_invoices(self, invoice_type=None):
		if not invoice_type:
			return self.user_invoices[['Date','Value','Name','Category','Type']]
		else:
			df = self.user_invoices.loc[self.user_invoices['Type'].eq(invoice_type.title())][['Date','Value','Name','Category','Type']]
			return df 

	def new_invoice(self, input_dict=None):
		value = round(float(input_dict['value']), 2)
		name = input_dict['name'].title()
		category = input_dict['category'].title()
		invoice_type = input_dict['invoice_type'].title()
		balance = input_dict['balance'].title()
		date = input_dict['date']
		user = input_dict['user']

		if date in (None, '', ' '):
			date = self.current_date

		new_row = {'Date':date, 'Value':value, 'Name':name, 'Category':category, 'Type':invoice_type, 'user':user}
		self.invoices = self.invoices.loc[:].append(new_row, ignore_index=True).sort_values(by=['Date','Category','Name','Value'], ascending=[False,True,True,False])

		self._update_csv('invoices')

		self.update_balance(balance, value, invoice_type, user)

		print(f'New {new_row["Type"]} created.\n\n{new_row["Date"]}, ${new_row["Value"]}, {new_row["Name"]}, {new_row["Category"]}')

	def new_balance(self, input_dict=None):
		name = input_dict['name'].title()
		funds = round(float(input_dict['funds']), 2)
		goal = round(float(input_dict['goal']), 2)
		goal_date = input_dict['goal_date']
		user = input_dict['user']

		new_row = {'Name':name, 'Funds':funds, 'Goal':goal ,'Goal Date':goal_date,'user':user}
		self.balances = self.balances.loc[:].append(new_row, ignore_index=True).sort_values(by=['Name','Funds'])

		self._update_csv('balances')

		print(f'New balance created.\n\n{new_row["Name"]}, ${new_row["Funds"]}')

	def update_balance(self, name=None, new_funds=None, fund_type=None, user=None):
		if fund_type == 'Expense':
			new_funds *= -1

		self.balances.loc[self.balances['Name'].eq(name) & self.balances['user'].eq(user),'Funds'] = self.balances['Funds'] + new_funds

		self._update_csv('balances')

		print(f'\nBalance {name} updated by ${new_funds}.\n')

	def transfer_balance(self, input_dict=None):
		from_balance = input_dict['from_balance']
		to_balance = input_dict['to_balance']
		funds = round(float(input_dict['funds']), 2)
		user = input_dict['user']

		self.balances.loc[self.balances['Name'].eq(from_balance) & self.balances['user'].eq(user), 'Funds'] = self.balances.Funds - funds
		self.balances.loc[self.balances['Name'].eq(to_balance) & self.balances['user'].eq(user), 'Funds'] = self.balances.Funds + funds

		self._update_csv('balances')

		print(f'${funds} transferred from {from_balance} to {to_balance}.')

	def annual_summary(self, invoice_type=None, year=None):
		if not year:
			year = self.current_year

		if not invoice_type:
			invoice_type = 'Expense'

		df = self._pivot_categories('year', int(year), invoice_type)

		return df.reset_index()

	def net_income(self, year=None):
		if not year:
			year = self.current_year

		df = self.user_invoices.loc[self.user_invoices.year.eq(year)]

		df.loc[df.Type.eq('Expense'), 'Value'] = df.Value * -1
		df_gb = df.loc[df.Type.isin(('Expense','Income')), ['month','Value']].groupby(by='month').sum().reset_index()
		df_gb['net'] = 'Net Income'

		df_pivot = df_gb.loc[:].pivot(index='net',columns='month',values='Value')

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
			df = self.user_invoices.loc[self.user_invoices['year'].eq(year) & self.user_invoices['Type'].eq(invoice_type.title())]
			
			summary_df = df.loc[:].sort_values(by=['month','Category']).groupby(by=['month','Category']).sum().reset_index()
			
			summary_df_pivot = summary_df.loc[:].groupby(['Category','month'],as_index=False)['Value'].sum().pivot(index='Category'\
				,columns='month', values='Value').fillna(0.00).reset_index()

			months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Totals']
			cols = ['Category',1,2,3,4,5,6,7,8,9,10,11,12]
			for i in cols:
				if i not in list(summary_df_pivot.columns):
					summary_df_pivot[i] = 0
			
			summary_df_pivot[cols[1:]] = summary_df_pivot.loc[:,cols[1:]].apply(pd.to_numeric, errors='coerce')
			summary_df_pivot = summary_df_pivot.loc[:,cols].rename(columns={1:'Jan',2:'Feb',3:'Mar'\
				,4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})

			summary_df_pivot.loc['Totals']= summary_df_pivot.sum(numeric_only=True, axis=0)
			summary_df_pivot.loc[:,'Totals'] = summary_df_pivot.sum(numeric_only=True, axis=1)
			summary_df_pivot = summary_df_pivot.loc[:].fillna('')
			summary_df_pivot.at['Totals', 'Category'] = 'Totals'
			
			summary_df_pivot[months] = summary_df_pivot[months].apply(pd.to_numeric, errors='coerce').applymap('{:,.2f}'.format)
			
			summary_df_pivot = summary_df_pivot.loc[:].replace('0.00', '--')

			summary_df_pivot.index = summary_df_pivot['Category']
			summary_df_pivot = summary_df_pivot.loc[:].drop(columns=['Category'])

			return summary_df_pivot

	def _update_csv(self,type):
		if type == 'invoices':
			self.invoices[['Date','Value','Name','Category','Type','user']].to_csv(f'data/invoices.csv',index=False)
		elif type == 'balances':
			self.balances[['Name','Funds','Goal','Goal Date','user']].to_csv(f'data/balances.csv',index=False)
		else:
			raise Exception(f'Incorrect date type of {type} was provided.')