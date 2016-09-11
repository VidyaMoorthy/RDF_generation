
#import gzip
import xml.etree.cElementTree as ET
import os
import sys
import traceback
import urllib
import re
#import pprint
import time

from urlparse import urlparse
from log import *

xml_ns = {'xs': "http://www.orcid.org/ns/orcid"}

class Identification(object):
	def __init__(self):
		self.ORCiDID = None
		self.otherName = None
		self.publications=None
		self.firstName= None
		self.familyName= None
		
		

	def getURI(self):
		return URIRef("http://identifiers.org/orcid/"+self.ORCiDID)
	

	def parse(self, node):
		temp_first = None
		temp_family = None
		self.ORCiDID = node.find('./xs:orcid-profile/xs:orcid-identifier/xs:path',xml_ns).text
		temp_first = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:given-names', xml_ns)
		if temp_first is not None:
			#temp_first = unicode(temp_first, 'utf-8')
			#self.firstName = temp_first
			self.firstName = temp_first.text.encode('utf-8')
			print self.firstName
		temp_family = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:family-name', xml_ns)
		if temp_family is not None:
			self.familyName=temp_family.text.encode('utf-8') 
			print self.familyName
		self.publications = [Publications(elem) for elem in node.findall('./xs:orcid-profile/xs:orcid-activities/xs:orcid-works/xs:orcid-work',xml_ns)]

		alia=[]
		aliases = node.findall('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:other-names/xs:other-name', xml_ns)
		if (aliases != None):
			for alias in aliases:
				txtalia= alias.text.encode('utf-8')
				if "or" in txtalia:
					orsplit = txtalia.split("or")
					for i in orsplit:
						alia.append(i)
				elif "," in txtalia:
					andsplit = txtalia.split(",")
					for j in andsplit:
						alia.append(j)
				else:
					 alia.append(txtalia)
			self.otherName= alia 

		
		

	def write_tab(self, output):


		#print self.publications
		pmid= []
		ORCID_ID = []
		First_name= []
		Last_name = []
		Other_name =[]
		if self.ORCiDID:
			ORCID_ID.append(self.ORCiDID)
			 
			
			if self.publications:
				
				for pub in self.publications:
					pmid = pub.pmid
					if pmid:
						if self.firstName:
							First_name = self.firstName
							#print First_name.encode('utf-8')
						else:
							First_name = ""
						if self.familyName:
							Last_name = self.familyName
						else:
							Last_name = ""
						if self.otherName:
							Other_name = (self.otherName)
							#print Other_name
						else:
							Other_name= [""] 
						output.write("{}\t{}\t{}\t{}\t{}\n".format(pmid,self.ORCiDID,First_name,Last_name,"|".join(Other_name)))
						
			
	def __unicode__(self):
		return unicode(self.some_field) or u''

class Publications(object):
	def __init__(self,node=None):
		self.pmid=None
		self.doi= None
		self.pmc= None
		#
		if node:
			self.parse(node)
			#self.comparePMID()
	def parse(self,node):

		temp_type= node.find('./xs:work-external-identifiers',xml_ns)
		if temp_type:
			idfiers = temp_type.findall('./xs:work-external-identifier',xml_ns)
			if idfiers:
		
					for xem in idfiers:
						type_tmp = xem.find('./xs:work-external-identifier-type',xml_ns).text.encode('utf-8')
						if type_tmp == 'doi':
							self.doi = xem.find('./xs:work-external-identifier-id',xml_ns).text.encode('utf-8')
						if type_tmp == 'pmc':
							self.pmc = xem.find('./xs:work-external-identifier-id',xml_ns).text.encode('utf-8')
						if type_tmp == 'pmid':
							self.pmid = xem.find('./xs:work-external-identifier-id',xml_ns).text



def main():
	indir = sys.argv[1]
	outdir = sys.argv[2]

	try:
		for file in os.listdir(indir):
			xmlFile = file
			f= open(indir+'/'+xmlFile, 'rb')
			#unzipedInFile = os.path.basename(xmlFile)
			#outfile = os.path.join(outdir,unzipedInFile+".text")
			fout=open(outdir,'a')
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
					error("writing {}: {}".format(cr.ORCiDID, traceback.format_exc()))
			except:
				error("parsing {}: {}".format(cr.ORCiDID, traceback.format_exc()))
			stop = time.clock()
			log("Reading records {}".format(stop-start))
			
			#g.serialize()
			log("Writing {}".format(time.clock()-stop))
	except:
		print traceback.format_exc()

if __name__ == "__main__":
	main()

