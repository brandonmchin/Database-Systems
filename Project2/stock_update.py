#!/usr/bin/python

import sys
import csv
import MySQLdb
from datetime import datetime, date

def update(tr_date, tr_time):
	# update old dates to be present day
	try:
		tr_date = tr_date.replace(year = tr_date.year + 11)
	except:
		tr_date = tr_date + (date(tr_date.year + 11, 1, 1) - date(tr_date.year, 1, 1))

	try:
		tr_time = tr_time.replace(year = tr_time.year + 11)
	except:
		tr_time = tr_time + (datetime(tr_time.year + 11, 1, 1) - datetime(tr_time.year, 1, 1))

	return tr_date, tr_time


if __name__=='__main__':
	if len(sys.argv) < 3:
		sys.stderr.write('USAGE: python %s <USERNAME> <PASSWORD>\n' % sys.argv[0])
		sys.exit(1)

	user = sys.argv[1]
	passwd = sys.argv[2]

	# open server connection 
	conn = MySQLdb.connect(host='localhost', user=user, passwd=passwd, db='S16336bchin')

	cursor = conn.cursor()

	cursor.execute("drop table if exists STOCK_TRADE")
	cursor.execute("create table STOCK_TRADE like stockmarket.STOCK_TRADE")

	with open('/space/public/database/stockmarket_benchmark/Data/STOCK_TRADE.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')

		print "PROCESSING..."
		count = 0
		total = 5775442.0		# total rows to process
		for row in reader:

			# display progress
			progress = round((count * 100 / total), 3)
			sys.stdout.write('\r' + str(progress) + ' %')
			sys.stdout.flush()

			# if count > 10000:
			# 	break				# only process the first 10000 rows

			instrument_id = int(row[0])  	
			trade_date = datetime.strptime(row[1], '%Y-%m-%d').date()  			
			trade_seq_nbr = int(row[2])	
			trade_symbol = row[3]  			
			trade_time = datetime.strptime(row[4][:-4], '%Y-%m-%d %H:%M:%S')  			
			trade_price = float(row[5])	
			trade_size = int(row[6]) 

			trade_date, trade_time = update(trade_date, trade_time)

			sql = "insert STOCK_TRADE values ('%d','%s','%d','%s','%s','%19.4f','%d')" % \
					(instrument_id, trade_date, trade_seq_nbr, trade_symbol, trade_time, trade_price, trade_size)

			try:
				cursor.execute(sql)
				conn.commit()
			except:
				conn.rollback()
				print "\nFAILED"
				break

			count += 1
	
		print "\nFINISHED"


	conn.close()