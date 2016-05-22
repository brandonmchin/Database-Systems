#!/usr/bin/python

# This program will read from the STOCK_TRADE csv file and print the first row

import csv

if __name__=='__main__':
	with open('/space/public/database/stockmarket_benchmark/Data/STOCK_TRADE.csv', 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			print row
			break

		# if we would like o print the next two rows, iterate through reader using the method next()
		for i in range(2):
			print reader.next()