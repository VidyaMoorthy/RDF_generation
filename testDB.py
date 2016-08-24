import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import re
import sys


def main():

	try:
		con = psycopg2.connect("dbname='ORCIDPROFILE' user='postgres' host='localhost' password='vidbha@nov14'")
	except:
		print "I am unable to connect to the database"

	cur = con.cursor()
	cur.execute("CREATE TABLE orcidprofileTrail (pmid integer , orcidid serial PRIMARY KEY, firstname varchar,lastname varchar, othername varchar);")
	with open('/home/vidya/Desktop/OntoForce/data/utils/old/trail.text') as f:
		content = f.readlines()
		for eachline in content:
			#pmid ,orcidId, first_name, last_name,other_name = re.findall("\[(.*?)\]", eachline)
			pmid ,orcidId, first_name, last_name,other_name = eachline.split("\t")


			#pmidint = [[int(y) for y in x] for x in pmid]
			#print pmidint
			
			#x= int(pmid)
			#print (pmid)
			#print (orcidId)
			#print first_name
			#print (other_name)
			#sys.exit()
			cur.execute("INSERT INTO orcidprofileTrail (pmid, orcidid,firstname,lastname,othername) VALUES (%s,%s,%s,%s,%s)", (pmid,orcidId,first_name, last_name,other_name ))
			#cur.execute("INSERT INTO orcidprofileTrail VALUES (pmid,orcidId,first_name, last_name,other_name )")
			con.commit()
			sys.exit

			#insertData(pmid ,orcidId, first_name, last_name)
main()

