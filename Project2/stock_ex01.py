#!/usr/bin/python

# This program will establish a connection to the stockmarket database and execute the SQL command "SHOW TABLES"

import sys
import MySQLdb

def connect(user, passwd):
	# open server connection 
	# your host (usually localhost), your username, your password, name of the database
	db = MySQLdb.connect(host='localhost', user=user, passwd=passwd, db='stockmarket')

	# a cursor object allows us to execute queries 
	cursor = db.cursor()

	# execute SQL command
	cursor.execute("SHOW TABLES")

	# print the first element of all the rows 
	for row in cursor.fetchall():
		print row[0]

	# disconnect from server
	db.close()

if __name__=='__main__':
	if len(sys.argv) < 3:
        sys.stderr.write('USAGE: python %s <USERNAME> <PASSWORD>\n' % sys.argv[0])
        sys.exit(1)

	user = sys.argv[1]
	passwd = sys.argv[2]
	connect(user, passwd)