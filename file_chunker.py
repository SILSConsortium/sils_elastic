#Example Usage:  'sudo python file_chunker.py sql/checkouts.sql checkouts'
#
#The first argument is the path to the SQL you'd like to execute
#Second argument is the name of the folder and filenames that are written.  
#The above example would create a set of files starting with output/checkouts/checkouts1.json

import argparse
import os
import pymssql
import json
from datetime import datetime

#Command line arguments & help text
parser = argparse.ArgumentParser(description='Executes a SQL statement.  The resulting rows from the query are written as JSON objects, one per line, 100,000 per file to the output folder.  These files can then be read by Logstash into ElasticSearch.  Usage:  file_chunker.py sql/query.sql your_output_type_name')
parser.add_argument('i', help='Path to file containing SQL to be executed.')
parser.add_argument('o', help='Name of the output JSON folder and files that are generated, i.e. if "hello" is given the files generated for Logstash will be hello1.json, hello2.json etc.')
args = parser.parse_args()

#Read the SQL file provided by the user as input
with open(args.i, 'r') as in_file:
    sql = in_file.read()

#Store the output name the user supplied
out_file = str(args.o)

#Create the ouput folder if necessary
if not os.path.exists('output'):
    print "Creating output folder..."
    os.makedirs('output')

#Create the output type folder if necessary
if not os.path.exists('output/' + out_file):
    print "Creating output/" + out_file + " folder..."
    os.makedirs('output/' + out_file)


#Connect to the Polaris database
#Connection information is stored in environment variables.
#If you don't use Polaris, you'll have to connect using something other than pymssql!
server = os.environ.get('POLARIS_PROD_DB')
user = os.environ.get('POLARIS_DB_USER')
password = os.environ.get('POLARIS_DB_PW')

print "Connecting to the Polaris database..."
conn = pymssql.connect(server, user, password, "Polaris")
cursor = conn.cursor(as_dict=True)

print "Executing SQL..."
cursor.execute(sql)

#date handling for json formatting, might not be needed
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)

#Chunk it out into files
current_file = 0
while True:
	first_txn = cursor.fetchone()
	if not first_txn:
		break

	current_file += 1
	txn_file = 'output/' + out_file + '/' + out_file + str(current_file) + ".json" 	
	f = open(txn_file,'w')

	first_txn_json = json.dumps(first_txn, default=date_handler)
	f.write(first_txn_json)

	#how many rows do we want to put in the file?
	for x in range(0,100000):
	    txn = cursor.fetchone()
	    if not txn:
	        break

	    f.write('\n') 
	    txn = json.dumps(txn, default=date_handler) #convert to json, using date_handler
	    f.write(txn) 
	f.close()
        print "Output file written successfully"

#close database connection
conn.close()
print "Connection to database closed"
