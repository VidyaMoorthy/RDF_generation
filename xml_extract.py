import gzip
import xml.etree.cElementTree as ET
import os
import sys
import traceback
import urllib
import re
import pprint
import time
from rdfwriter import Graph, Literal, Namespace, RDF, URIRef
from log import *

xml_ns = {'xs': "http://www.orcid.org/ns/orcid"}
NS = Namespace("http://ns.ontoforce.com/ontologies/person/")
NST = Namespace("http://ns.ontoforce.com/ontologies/person/classes/")
PML= Namespace("http://identifiers.org/pubmed/")
SCP = Namespace("https://www.scopus.com/authid/detail.uri?authorId=")
RSD= Namespace("http://www.researcherid.com/rid/")
class Identification(object):
    def __init__(self):
        self.ORCiDID = None
        self.personName = None
        self.otherName = None
        self.linkedIN = None
        self.googleScholar= None
        self.twitter = None
        self.scopus = None
        self.ResearcherID= None
        self.publications=None
        

    def getURI(self):
        return URIRef("http://identifiers.org/orcid/"+self.ORCiDID)

    def parse(self, node):
        self.ORCiDID = node.find('./xs:orcid-profile/xs:orcid-identifier/xs:path',xml_ns).text
        firstName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:given-names', xml_ns).text.encode('utf-8')
        familyName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:family-name', xml_ns).text.encode('utf-8')
        self.personName = firstName + "  " +familyName

        alia=[]
        aliases = node.findall('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:other-names/xs:other-name', xml_ns)
        if (aliases != None):
            for alias in aliases:
                alia.append(alias.text)
            self.otherName= alia

        peopleIndtifier= node.findall('./xs:orcid-profile/xs:orcid-bio/xs:researcher-urls/xs:researcher-url/xs:url-name', xml_ns)
        peoplIdenValue= node.findall('./xs:orcid-profile/xs:orcid-bio/xs:researcher-urls/xs:researcher-url/xs:url', xml_ns)
        if(peopleIndtifier):

            type_identifier=[]
            type_identiValue=[]
            for iterIdenti in peopleIndtifier:
                type_identifier.append(iterIdenti.text)
            for iterValue in peoplIdenValue:
                type_identiValue.append(iterValue.text)

            for iterId in range(0,len(type_identifier)):
                if (type_identifier[iterId]== "LinkedIn"):
                    self.linkedIN = type_identiValue[iterId]
                if (type_identifier[iterId]== "Google Scholar"):
                    self.googleScholar = type_identiValue[iterId]
                if (type_identifier[iterId]== "Twitter"):
                    self.twitter = type_identiValue[iterId]
                if (type_identifier[iterId]== "Scopus Author ID"):
                    self.scopus = type_identiValue[iterId]
        
        PeopleIdentity=node.findall('./xs:orcid-profile/xs:orcid-bio/xs:external-identifiers/xs:external-identifier/xs:external-id-common-name', xml_ns)
        PeopleIDValue=node.findall('./xs:orcid-profile/xs:orcid-bio/xs:external-identifiers/xs:external-identifier/xs:external-id-reference', xml_ns)
        if(PeopleIdentity):
            type_identfr=[]
            type_idenValue=[]
            for loopID in PeopleIdentity:
                type_identfr.append(loopID.text)
            for loopVal in PeopleIDValue:
                type_idenValue.append(loopVal.text)

            for iterate in range(0,len(type_identfr)):
                if (type_identfr[iterate]== "LinkedIn"):
                    self.linkedIN = type_idenValue[iterate]
                if (type_identfr[iterate]== "Google Scholar"):
                    self.googleScholar = type_idenValue[iterate]
                if (type_identfr[iterate]== "Twitter"):
                    self.twitter = type_idenValue[iterate]
                if(type_identfr[iterate]== "ResearcherID"):
                    self.ResearcherID = type_idenValue[iterate]
                if(type_identfr[iterate]== "Scopus Author ID"):
                    self.scopus = type_idenValue[iterate]
        self.publications = [Publications(elem) for elem in node.findall('./xs:orcid-profile/xs:orcid-activities/xs:orcid-works/xs:orcid-work',xml_ns)]   



    def write_ttl(self, g):
        #print self.ORCiDID
        #print self.publications
        if self.ORCiDID:
            g.add((self.getURI(), NS["Name"], Literal(self.personName)))
            g.add((self.getURI(),RDF.type,NST["ORCiDPerson"]))

            if self.otherName:
                for othernames in range(0,len(self.otherName)):
                    g.add((self.getURI(), NS["OtherName"], Literal(self.otherName[othernames])))

            if self.linkedIN:
                g.add((self.getURI(), NS["linkedIN"], Literal(self.linkedIN)))
            if self.googleScholar:
                g.add((self.getURI(), NS["GooGleScholar"], Literal(self.googleScholar)))
            if self.twitter:
                g.add((self.getURI(), NS["Twitter"], Literal(self.twitter)))
            if self.ResearcherID:
                g.add((self.getURI(), NS["ResearcherID"], Literal(self.ResearcherID)))
                g.add((self.getURI(), NS["ResearcherIDLink"], RSD[self.ResearcherID]))
            if self.scopus:
                g.add((self.getURI(), NS["ScopusID"], SCP[self.scopus]))
            if self.publications:
                for pub in self.publications:
                    pmid = pub.pmid
                    if pmid:
                        g.add((self.getURI(), NS["PMIDID"], Literal(pmid)))
                        g.add((self.getURI(),NS["PMIDLINK"], PML[pmid]))
            
                        if pub.doi:
                            doi=pub.doi
                            g.add((PML[pmid],NS["PMIDhasDOI"], Literal(doi)))
               
            
    def __unicode__(self):
        return unicode(self.some_field) or u''

class Publications(object):
    #peopleID= self.ORCiDID
    def __init__(self,node=None):
        self.pmid=None
        self.doi= None
        if node:
            self.parse(node)

    def parse(self,node):

        temp_type= node.find('./xs:work-external-identifiers',xml_ns)
        if temp_type:
            idfiers = temp_type.findall('./xs:work-external-identifier',xml_ns)
            if idfiers:
        
                    for xem in idfiers:
                        type_tmp = xem.find('./xs:work-external-identifier-type',xml_ns).text
                        if type_tmp == 'doi':
                            self.doi = xem.find('./xs:work-external-identifier-id',xml_ns).text
                        if type_tmp == 'pmid':
                            self.pmid = xem.find('./xs:work-external-identifier-id',xml_ns).text 


        

def select_files_in_folder(dir, ext):
    for file in os.listdir(dir):
        if file.endswith('.%s' % ext):
            yield os.path.join(dir, file)

def main():
    indir = sys.argv[1]
    outdir = sys.argv[2]

    try:
        for file in os.listdir(indir):
            xmlFile = file
            f= open(indir+'/'+xmlFile, 'rb')
            unzipedInFile = os.path.basename(xmlFile)
            outfile = os.path.join(outdir,unzipedInFile+".ttl")
            fout=open(outfile,"w")
            g = Graph(fout)
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
                    cr.write_ttl(g)
                except:
                    error("writing {}: {}".format(cr.ORCiDID, traceback.format_exc()))
            except:
                error("parsing {}: {}".format(cr.ORCiDID, traceback.format_exc()))
            stop = time.clock()
            log("Reading records {}".format(stop-start))
            
            g.serialize()
            log("Writing {}".format(time.clock()-stop))
    except:
        print traceback.format_exc()

if __name__ == "__main__":
    main()

