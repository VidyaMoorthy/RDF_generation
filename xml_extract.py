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
#import disqover

path = '/home/vidya/Desktop/OntoForce/xml'
xml_ns = {'xs': "http://www.orcid.org/ns/orcid"}
NS = Namespace("http://ns.ontoforce.com/ontologies/person/")
NST = Namespace("http://ns.ontoforce.com/ontologies/person/classes/")
PML= Namespace("http://identifiers.org/pubmed/")
class Identification(object):
    def __init__(self):
        self.ORCiDID = None
        self.personName = None
        self.pmid=None
        #self.firstName = None
        #self.familyName = None
        #self.association = None

    def getURI(self):
        return URIRef("http://identifiers.org/orcid/"+self.ORCiDID)

    def parse(self, node):
        self.ORCiDID = node.find('./xs:orcid-profile/xs:orcid-identifier/xs:path',xml_ns).text
        firstName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:given-names', xml_ns).text
        familyName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:family-name', xml_ns).text
        self.personName = firstName + "  " +familyName
        
        
        PMID=[]
        for_inter= node.findall('./xs:orcid-profile/xs:orcid-activities/xs:orcid-works/xs:orcid-work/xs:work-external-identifiers/xs:work-external-identifier/xs:work-external-identifier-type',xml_ns)
        for_id = node.findall('./xs:orcid-profile/xs:orcid-activities/xs:orcid-works/xs:orcid-work/xs:work-external-identifiers/xs:work-external-identifier/xs:work-external-identifier-id',xml_ns)
        temp_pmid=[]
        type_pmid=[]
        for iteratn in for_inter:
            type_pmid.append(iteratn.text)
        for id_iter in for_id:
            temp_pmid.append(id_iter.text)

        #if (len(type_pmid) != 0) and (len(temp_pmid) != 0):
            
        for slctg_pmid in range (0,len(temp_pmid)):
            #PMID.append(type_pmid[slctg_pmid])
                
           if (type_pmid[slctg_pmid] == "pmid"):
                   #PMID.append("12345")
                PMID.append(temp_pmid[slctg_pmid])
        #for x in (for_inter):
        #    PMID.append(type_pmid)

        self.pmid= PMID

    def write_ttl(self, g):
        print self.ORCiDID
        print self.pmid
        if self.ORCiDID:
            g.add((self.getURI(), NS["Name"], Literal(self.personName)))
            g.add((self.getURI(),RDF.type,NST["ORCiDPerson"]))

            if self.pmid:
                for x in range (0,len(self.pmid)):
                    g.add((self.getURI(),NS["PMIDID"], Literal(self.pmid[x])))
                    g.add((self.getURI(),NS["PMIDLINK"], PML(self.pmid[x])))
                    #g.add((self.getURI(),RDF.type,NST["PMID"]))
            
    def __unicode__(self):
        return unicode(self.some_field) or u''


def main():
    indir = sys.argv[1]
    outdir = sys.argv[2]

    try:
        for file in os.listdir(indir):
            xmlFile = file
            f = open(indir+'/'+xmlFile, 'rb')
            unzipedInFile = os.path.basename(xmlFile)
            outfile = os.path.join(outdir,unzipedInFile+".ttl")
            fout=open(outfile,"w")
            g = Graph(fout)
            log("Parsing file: {} ".format(xmlFile))
            start= time.clock()
            outdir = ET.parse(f)
            root = outdir.getroot()
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
        #print "File: "+unzipedInFile
        print traceback.format_exc()

if __name__ == "__main__":
    #for file in select_files_in_folder(sys.argv[1], 'xml'):
    main()

