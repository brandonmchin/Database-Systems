#!/usr/bin/python

import sys
import csv
import MySQLdb
from datetime import datetime, timedelta

#######################################################################################################################
# 												GLOBAL FUNCTIONS
#######################################################################################################################

def get_expired(cursor):
	# read from BROKER and get all the contracts that expired
	#
	# return: list of the contract numbers that expired

	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')   # get string version of current datetime
	now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')    # convert string to datetime format
	expired = []
	sql = "select contract_num, trade_type, due_time from BROKER"
	cursor.execute(sql)
	results = cursor.fetchall()		# list of lists
	for row in results:
		contract_num = int(row[0])
		trade_type = row[1]
		due_time = row[2]
		if trade_type == 'long': 	# trader is short selling
			if now > due_time: 		# contract is expired
				expired.append(contract_num)
	return expired

def get_trade_price(cursor, trading_symbol, trade_date):
	# read from STOCK_TRADE and get the trade_price for the given trading_symbol and trade_date
	#
	# return: trade_price

	# search for price of stock after 3 months, if not found, search the price of the previous date
	print "SEARCHING FOR DATE...", trade_date
	while(True):
		sql = "select TRADE_PRICE, TRADE_SIZE from STOCK_TRADE where TRADING_SYMBOL = '%s' and TRADE_DATE = '%s' limit 1" % (trading_symbol, trade_date)
		cursor.execute(sql)
		results = cursor.fetchall()

		if len(results) > 0:
			for row in results:
				trade_price = float(row[0])
				trade_size = int(row[1])
				print "FOUND, PRICE:", trade_price
				break
			break
		else:
			trade_date = trade_date + timedelta(days=-1)
			print "NOT FOUND, SEARCHING FOR PREVIOUS DATE...", trade_date

	return trade_price, trade_size		


def is_margin_call(cursor, trading_symbol, trade_price, start_date, due_date):
	# determine if a margin call was made
	#
	# return: boolean, true if margin call was made, false otherwise

	# if the price of stock drops below this rate at any point, issue a margin call
	maintenance_margin_rate = 0.25 
	maintenance_margin = maintenance_margin_rate * trade_price

	sql = "select TRADE_PRICE from STOCK_TRADE where TRADING_SYMBOL = '%s' and TRADE_DATE >= '%s' and TRADE_DATE <= '%s'" \
			% (trading_symbol, start_date, due_date)
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		price = float(row[0])
		if price <= maintenance_margin:
			print "MARGIN CALL MADE AT PRICE:", price
			return True
	print "NO MARGIN CALL MADE."
	return False


def trader_profit(cursor, expired):
	# calculate the profit of traders whose contracts have expired
	#
	# return: list of trader_id and their net profit

	margin = 0.3				# 30% trader down payment requirement

	profits = []
	for contract in expired:
		print "\nEXPIRED CONTRACT:", contract
		sql = "select * from BROKER where contract_num = %d" % contract
		cursor.execute(sql)
		row = cursor.fetchone()
		contract_num = row[0]
		trader_id = row[1]
		trade_type = row[2]
		trading_symbol = row[3]
		start_date = row[4].date()
		due_date = row[5].date() 		# convert time to date
		# get the price and size of stock at the start of contract
		trade_price, trade_size = get_trade_price(cursor, trading_symbol, start_date) 
		new_trade_price, n = get_trade_price(cursor, trading_symbol, due_date)	 	# get the price of stock after 3 months
		delta = new_trade_price - trade_price 		# calculate the change in stock price over 3 months	

		loan = trade_price * trade_size * (1 - margin) 	# broker covers the remaining 70%
		fee = float(row[6]) * loan	 	# broker fee trader must pay to take out the loan, equal to rate * loan	
		down_pay = (margin * trade_price * trade_size) + fee 	# initial trader down payment plus the fee

		# determine if a margin call was made
		margin_call = is_margin_call(cursor, trading_symbol, trade_price, start_date, due_date)

		margin_call_rate = 0.2  	# if a margin call is made, trader must pay an additional 20% the original loan
		if margin_call:
			margin_call_price = loan * margin_call_rate 
		else:
			margin_call_price = 0.0	

		print "ADDITIONAL PAYMENT:", margin_call_price

		profit = ((trade_price + delta) * trade_size) - down_pay - loan - margin_call_price
		profits.append((contract_num, trader_id, profit)) 			# append a tuple
	
	return profits

def update(cursor):
	# update each trader's balance with their new profit

	expired = get_expired(cursor)
	profits = trader_profit(cursor, expired)
	for contract_num, trader_id, profit in profits:
		print "\nID: %d | Profit: %f" % (trader_id, profit) 	# print the profits of all traders whose contracts expired
		sql = "update BROKER set net_profit = %f where contract_num = %d" % (profit, contract_num) 	# update net profit in BROKER
		cursor.execute(sql)
		print "UPDATED BROKER CONTRACT NET PROFIT"

		sql = "update TRADER set balance = balance + %f where trader_id = %d" % (profit, trader_id) # update balance in TRADER
		cursor.execute(sql)
		print "UPDATED TRADER BALANCE"

########################################################################################################################
# 												MAIN
########################################################################################################################

if __name__=='__main__':
	if len(sys.argv) < 3:
		sys.stderr.write('USAGE: python %s <USERNAME> <PASSWORD>\n' % sys.argv[0])
		sys.exit(1)

	user = sys.argv[1]
	passwd = sys.argv[2]

	# open server connection 
	conn = MySQLdb.connect(host='localhost', user=user, passwd=passwd, db='S16336team3')

	cursor = conn.cursor()

	# add the profits of each contract and the balances of each trader 
	try: 
		update(cursor)
		conn.commit() 		# commit changes to the database
	except:
		conn.rollback() 	# revert changes in case of error