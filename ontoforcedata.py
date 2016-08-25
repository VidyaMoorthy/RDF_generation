import gzip
import xml.etree.cElementTree as ET
import os
import sys
import traceback
import urllib
import re
import pprint
import time
import rdflib
from rdfwriter import Graph, Literal, Namespace, RDF, URIRef
from urlparse import urlparse
from log import *


class Identification(object):
	def __init__(self):
		
		self.article_title = None
		self.pmid= None
		self.first_name= None
		self.family_name= None
		self.initial = None
		self.journal = None
		self.language =None
		


	def parse(self, node):
		#f = "/home/vidya/Desktop/OntoForce/data/utils/old/medline16n0650.xml"
		#xmlFile = ET.parse(f)
		#root = xmlFile.getroot()
		
		
		for each  in node.findall('MedlineCitation'):
			self.pmid.append(each.find('PMID').text.encode('utf-8'))  # this gets the pmid



			for article in each.findall('Article'):
				self.article_title.append(article.find('ArticleTitle').text.encode('utf-8')) # this gets the article title 
				self.language.append(article.find('Language').text.encode('utf-8')) # this gets the language of the article

				for authors in article.findall('AuthorList'):
					for each_author in authors.findall('Author'):
						last_name = each_author.find('LastName')
						print last_name.text.encode('utf-8')
						if last_name :
							self.family_name.append(last_name.text.encode('utf-8'))
							#print self.family_name
							#print last_name.text.encode('utf-8')
						else:
							self.family_name.append("")

						first= each_author.find('ForeName')
						print first.text.encode('utf-8')
						if first:
							self.first_name.append(first.text.encode('utf-8'))
						else:
							self.first_name.append("")
						ini= each_author.find('Initials')
						if ini:
							self.initial.append(ini.text.encode('utf-8'))
						else:
							self.initial.append("")	
				
			
				for journ in article.findall('Journal'):
					journal_title=  journ.find('Title') # this gets the journal title
					if journal_title:
			 			self.journal.append(journal_title.text.encode('utf-8'))
		 			else:
		 				self.journal.append("")
		#print all_first[:30]


	def write_tab(self, output):

		print self.first_name[:10]
		#print self.family_name[:10]
		print self.pmid[:10]


		for wrting in range (0,len(self.pmid)):
			output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(self.pmid[wrting],self.first_name[wrting],self.family_name[wrting],self.initial[wrting],self.article_title[wrting],self.journal[wrting],self.language[wrting]))
			#print output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(self.pmid[wrting],self.first_name[wrting],self.family_name[wrting],self.initial[wrting],self.article_title[wrting],self.journal[wrting],self.language[wrting]))
			
	   
			
	def __unicode__(self):
		return unicode(self.some_field) or u''




def main():
	indir = '/home/vidya/Desktop/OntoForce/data/utils/old/medline16n0650.xml'
	outdir = '/home/vidya/Desktop/OntoForce/data/utils/old/ontoforcedata.text'

	try:
		#for file in os.listdir(indir):
		xmlFile = indir
		f= open(xmlFile, 'rb')
		#unzipedInFile = os.path.basename(xmlFile)
		#outfile = os.path.join(outdir,unzipedInFile+".text")
		fout=open(outdir,'w')
		#g = Graph(fout)
		log("Parsing file: {} ".format(xmlFile))
		start= time.clock()
		xmlFile = ET.parse(f)
		root = xmlFile.getroot()
		log("Parsing xml {}".format(time.clock()-start))
		
		start= time.clock()
		cr = Identification()
		try:
			cr.parse(root)
			try:
				cr.write_tab(fout)
			except:
				error("writing {}: {}".format(cr.pmid, traceback.format_exc()))
		except:
			error("parsing {}: {}".format(cr.pmid, traceback.format_exc()))
		stop = time.clock()
		log("Reading records {}".format(stop-start))
		
		#g.serialize()
		log("Writing {}".format(time.clock()-stop))
	except:
		print traceback.format_exc()

if __name__ == "__main__":
	main()

