import gzip
import xml.etree.cElementTree as ET
import os
import sys
import traceback
import urllib
import re
import pprint
import time
from urlparse import urlparse
#from log import *
#sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace'
from log import *

reload(sys) 
sys.setdefaultencoding('utf8')

class Identification(object):

	def __init__(self):
		self.pmid= []
		

	def parse(self, node,article_speci, author_speci):
		mesh_stopwords=[]
		
		title_stopwords = []
		with open('/home/vidya/Desktop/OntoForce/data/utils/old/data_processing/stopwords/mesh_stopword.text') as f:
			for line in f.readlines():
				words = line.split()
				for x in words:
					mesh_stopwords.append(x)
		
		
		with open('/home/vidya/Desktop/OntoForce/data/utils/old/data_processing/stopwords/title_stopwords.text') as q:
			for line in q.readlines():
				wrds = line.split()
				for y in wrds:
					title_stopwords.append(y)	

		self.temp_pmid = None
		for each  in node.findall('MedlineCitation'):
			#self.pmid.append(each.find('PMID').text.encode('utf-8'))  # this gets the pmid
			self.temp_pmid= each.find('PMID').text.encode('utf-8')
			self.article_title = []
			self.author_first_name= []
			self.author_family_name= []
			self.author_initial = []
			self.author_suffix = []
			self.journal = []
			self.language =[]
			self.meshID = []
			self.author = []
			self.author_postion = []
			self.author_affiliation = []
			self.article_affiliation = []			


			# temporary variables 
			self.temp_lan = None
			self.temp_meshid = []
			self.temp_article = []
			self.temp_journal = None

			for meshes in each.findall('MeshHeadingList'):
		 				#print meshes
		 				temp_mesh = []
		 				for each_mesh in meshes.findall('MeshHeading'):
		 					descrip = each_mesh.find('DescriptorName')
		 					#descrip = DescriptorName.attrib
		 					if descrip is not None:
		 						#if descrip.attrib["UI"] not in mesh_stopwords:
		 						temp_mesh.append(descrip.attrib["UI"])
							qulifier = each_mesh.find('QualifierName')
							if qulifier is not None:
								#if qulifier.attrib["UI"] not in mesh_stopwords:
								temp_mesh.append(qulifier.attrib["UI"])
						meshwords = ([word for word in temp_mesh if word not in mesh_stopwords])
						#self.temp_meshid  = temp_mesh
						self.temp_meshid = meshwords
						print meshwords
						#print mesh_stopwords
			for article in each.findall('Article'):
				before_split = article.find('ArticleTitle').text.encode('utf-8') # this gets the article title 
				after_split = before_split.split()
				for each_word in after_split:
					if each_word not in title_stopwords:
						self.temp_article.append(each_word)
				self.temp_lan = (article.find('Language').text.encode('utf-8'))# this gets the language of the article

				for journ in article.findall('Journal'):
						journal_title=  journ.find('Title') # this gets the journal title
						#if journal_title:
						self.temp_journal = journal_title.text.encode('utf-8')
			 	
				self.author = [Author(elem) for elem in article.findall('AuthorList')]   
				if self.author:
					for auth in self.author:
						self.author_first_name = auth.first_name
						self.author_family_name = auth.family_name
						self.author_initial = auth.initial
						self.author_postion = auth.position
						self.author_affiliation = auth.affiliation_author
						self.article_affiliation = auth.affiliation_article
						self.author_suffix = auth.suffix
					self.meshID = self.temp_meshid
					self.article_title = self.temp_article
					self.pmid = self.temp_pmid
					self.language = self.temp_lan
					self.journal = self.temp_journal

			if self.pmid:		

				article_speci.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(self.pmid,"|".join(self.article_title),self.language,self.journal,"|".join(self.article_affiliation),"|".join(self.meshID)))
				#print "|".join(self.article_title)
				for x in range(0,len(self.author_family_name)):
					author_speci.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(self.pmid,self.author_first_name[x],self.author_family_name[x],self.author_initial[x],self.author_suffix[x],self.author_postion[x],"|".join(self.author_affiliation[x])))
					
	   
			
	def __unicode__(self):
		return unicode(self.some_field) or u''

class Author(object):
 	
	def __init__(self,node=None):
		self.family_name = []

		self.first_name = []
		self.initial = []
		self.temp_affiliation = []
		self.position = []
		self.suffix = []
		self.affiliation_author = []
		self.affiliation_article = []
		if node:
			self.parse(node)

	def parse(self,node):
		affiliation_stopwords = []
		with open('/home/vidya/Desktop/OntoForce/data/utils/old/data_processing/stopwords/affi_stopwords.text') as q:
			for line in q.readlines():
				aff_words = line.split()
				for afw in aff_words:
					affiliation_stopwords.append(afw)

		psition = []
		aff_temp =[]
		

		for pos,each_author in enumerate(node.findall('Author')):
			last_name = each_author.find('LastName')
			self.position.append(pos)
			psition.append(pos)
			#print last_name.text.encode('utf-8')
			if last_name is not None:
				#print last_name.text.encode('utf-8')
				self.family_name.append(last_name.text.encode('utf-8'))
			else:
				self.family_name.append("")

			first= each_author.find('ForeName')
			#print first.text.encode('utf-8')
			if first is not None:
				self.first_name.append(first.text.encode('utf-8'))
			else:
				self.first_name.append("")

			ini= each_author.find('Initials')
			if ini is not None:
				self.initial.append(ini.text.encode('utf-8'))
			else:
				self.initial.append("")	

			suffi = each_author.find('Suffix')
			if suffi is not None:
				self.suffix.append(suffi.text.encode('utf-8'))
			else:
				self.suffix.append("")


			for affili in each_author.findall('AffiliationInfo'):
				affiliatn = None
				affiliatn = affili.find('Affiliation')
				if affiliatn is not None:
					afflia = affiliatn.text.encode('utf-8')
					temp_affi = afflia.split()
					for af in temp_affi:
						if af not in affiliation_stopwords:
							aff_temp.append(af)

		if (len(psition) == len(aff_temp)):
			self.affiliation_author = aff_temp
			self.affiliation_article = ""
		else:
			self.affiliation_article =aff_temp
			for x in range(0,len(psition)):
				self.affiliation_author.append("") 


def main():
	indir = sys.argv[1]
	article_specific = sys.argv[2]
	author_specific = sys.argv[3]


	try:
		xmlFile = gzip.open(indir, 'rb')
		article_specific_data=open(article_specific,'a')
		author_specific_data = open(author_specific,'a')

		log("Parsing file: {} ".format(xmlFile))
		start= time.clock()
		xmlFile = ET.parse(xmlFile)
		root = xmlFile.getroot()
		log("Parsing xml {}".format(time.clock()-start))
		
		start= time.clock()
		cr = Identification()
		try:
			article_specific_data.write("{}\t{}\t{}\t{}\t{}\t{}\n".format('PMID','ARTICLE_TITLE','LANGUAGE','JOURNAL_NAME','ARTICLE_AFFILIATION','MESHID'))
			author_specific_data.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("PMID","FIRST_NAME","FAMILY_NAME","INITIAL","SUFFIX","POSITION","AUTHOR AFFILIATION"))
			cr.parse(root,article_specific_data,author_specific_data)
		except:
			error("parsing {}: {}".format(cr.pmid, traceback.format_exc()))
		stop = time.clock()
		log("Reading records {}".format(stop-start))
		
		log("Writing {}".format(time.clock()-stop))
	except:
		print traceback.format_exc()

if __name__ == "__main__":
	main()

