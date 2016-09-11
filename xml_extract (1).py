# This creates the ttl file

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

xml_ns = {'xs': "http://www.orcid.org/ns/orcid"}
NS = Namespace("http://ns.ontoforce.com/ontologies/person/")
NST = Namespace("http://ns.ontoforce.com/ontologies/person/classes/")
PML= Namespace("http://identifiers.org/pubmed/")
SCP = Namespace("https://www.scopus.com/authid/detail.uri?authorId=")
RSD= Namespace("http://www.researcherid.com/rid/")
DOI = Namespace("http://doi.org/")
Ref= Namespace("http://purl.org/spar/biro/")
PMC = Namespace("http://www.ncbi.nlm.nih.gov/pmc/?term=")
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
        self.firstName= None
        self.familyName= None
        self.country = None
        self.affiliations = None

    def getURI(self):
        return URIRef("http://identifiers.org/orcid/"+self.ORCiDID)
    

    def parse(self, node):
        self.ORCiDID = node.find('./xs:orcid-profile/xs:orcid-identifier/xs:path',xml_ns).text
        self.firstName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:given-names', xml_ns).text.encode('utf-8')
        self.familyName = node.find('./xs:orcid-profile/xs:orcid-bio/xs:personal-details/xs:family-name', xml_ns).text.encode('utf-8')
        self.personName = self.firstName + "  " +self.familyName
        country_temp= node.find('./xs:orcid-profile/xs:orcid-bio/xs:contact-details/xs:address/xs:country',xml_ns)
        if country_temp is not None:
            self.country = country_temp.text.encode('utf-8')
        #print self.country
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
                #print alia
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
                if(type_identifier[iterId]== "ResearcherID"):
                    self.ResearcherID = type_identiValue[iterId]
        
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

        self.affiliations = [Affiliations(ele) for ele in node.findall('./xs:orcid-profile/xs:orcid-activities',xml_ns)]

    def write_ttl(self, g):
        
        if self.ORCiDID:
            g.add((self.getURI(), NS["Name"], Literal(self.personName)))
            g.add((self.getURI(),RDF.type,NST["ORCiDPerson"]))
            if self.firstName:
                g.add((self.getURI(), NS["firstName"], Literal(self.firstName)))
            if self.familyName:
                g.add((self.getURI(), NS["familyName"], Literal(self.familyName)))

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
            if self.country:
                g.add((self.getURI(), NS["Country"], Literal(self.country)))
            if self.affiliations:
                for affilia in self.affiliations:
                    edu_organisation = affilia.edu_organisation
                    edu_role = affilia.edu_role 
                    edu_dpt = affilia.edu_dpt
                    edu_stdate = affilia.edu_stdate
                    edu_endate = affilia.edu_endate
                    if edu_organisation:
                        for yz in range (0,len(edu_organisation)):
                        
                            g.add((self.getURI(),NS["educationalAffiliation"],Literal(edu_organisation[yz])))
                            if edu_role:
                                if edu_role[yz] == "":
                                    "do nothing"
                                else:
                                    g.add((edu_organisation[yz],NS["educationalRole"],Literal(edu_role[yz])))
                            if edu_dpt:
                                if edu_dpt[yz] == "":

                                    "do nothing"
                                else:
                                    g.add((edu_organisation[yz],NS["educationalDepartment"],Literal(edu_dpt[yz])))
                            if edu_stdate:
                                if edu_stdate[yz] == "":
                                    "do nothing"
                                else:
                                    g.add((edu_organisation[yz],NS["educationalStartDate"],Literal(edu_stdate[yz])))

                            if edu_endate:
                                if edu_endate[yz] == "":
                                    "do nothing"
                                else:
                                    g.add((edu_organisation[yz],NS["educationalEndDate"],Literal(edu_endate[yz])))

                    emp_organisation=affilia.emp_organisation
                    emp_role = affilia.emp_role
                    emp_dpt = affilia.emp_dpt
                    emp_stdate = affilia.emp_stdate
                    emp_endate = affilia.emp_endate
                    #print emp_organisation
                    if emp_organisation:
                        for xy in range (0,len(emp_organisation)):
                            #print each
                            g.add((self.getURI(),NS["employAffiliation"],Literal(emp_organisation[xy])))
                            if emp_role:
                                if emp_role[xy] == "":
                                    "do nothing"
                                else:
                                    g.add((emp_organisation[xy],NS["EmployRole"],Literal(emp_role[xy])))
                       
                            if emp_dpt:
                                if emp_dpt[xy] == "":
                                    "do nothing"
                                else:
                                    g.add((emp_organisation[xy],NS["EmployDepartment"],Literal(emp_dpt[xy])))
                        
                            if emp_stdate:
                                if emp_stdate[xy] == "":
                                    "do nothing"
                                else:
                                    g.add((emp_organisation[xy],NS["EmployStartDate"],Literal(emp_stdate[xy])))
                        
                            if emp_endate:
                                if emp_endate[xy] == "":
                                    "do nothing"
                                else:
                                    g.add((emp_organisation[xy],NS["educationalEndDate"],Literal(emp_endate[xy])))

            if self.publications:
                for pub in self.publications:
                    pmid = pub.pmid
                    if pmid:
                        g.add((self.getURI(),NS["isAuthorOf"],PML[pmid]))
            
                        if pub.doi:
                            doi=pub.doi
                            g.add((PML[pmid],Ref["references"], DOI[doi]))
                        if pub.pmc:
                            pmc = pub.pmc
                            g.add((PML[pmid],Ref["PMCreference"], PMC[pmc]))
            
               
            
    def __unicode__(self):
        return unicode(self.some_field) or u''

class Publications(object):
    #peopleID= self.ORCiDID
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

class Affiliations(object):
    def __init__(self,node = None):
        self.edu_dpt = []
        self.edu_role = []
        self.edu_stdate = []
        self.edu_endate = [] 
        self.emp_dpt = []
        self.emp_role = []
        self.emp_stdate = []
        self.emp_endate = [] 
        self.edu_organisation = []
        self.emp_organisation = []
        #edateyr,enmon,enday
        if node:
            self.parse(node)
    def parse(self, node):
        temp = node.find('./xs:affiliations',xml_ns)
        if temp:
            affis_all = temp.findall('./xs:affiliation',xml_ns)
            if affis_all:
                departmnt = None
                role = None
                star_dte =None
                end_dte = None
                for each_affi in affis_all:
                    temp_type = each_affi.find('./xs:type',xml_ns).text.encode('utf-8')
                    #if temp_type == "employment":
                    departt = each_affi.find('./xs:department-name',xml_ns)
                    if departt:
                        departmnt = departt.text.encode('utf-8')
                        #print departmnt
                    rol = each_affi.find('./xs:role-title',xml_ns)
                    if rol is not None:
                        role = rol.text.encode('utf-8')
                    stt_date =each_affi.findall('./xs:start-date',xml_ns)
                    #print departmnt
                    if stt_date is not None:
                        #start_date = []
                        for st_date in stt_date:
                            
                            st_dte = []
                            y= st_date.find('./xs:year',xml_ns)
                            if y is not None:
                                yer = y.text
                                st_dte.append(yer)
                            else:
                                st_dte.append("")
                            mn= st_date.find('./xs:month',xml_ns)
                            if mn is not None:
                                mnth = mn.text
                                st_dte.append(mnth)
                            else:
                                st_dte.append("")
                            d= st_date.find('./xs:day',xml_ns)
                            if d is not None:
                               day = d.text
                               st_dte.append(day)
                            else:
                                st_dte.append("")    
                            
                            star_dte = "|".join(st_dte)

                    end_date =each_affi.findall('./xs:end-date',xml_ns)
                    if end_date is not None:
                        #end_date = []
                        for en_date in end_date:
                            endate = []
                            yer = en_date.find('./xs:year',xml_ns)
                            if yer is not None:
                                year = yer.text
                                endate.append(year)
                                #print year
                            else:
                                endate.append("")
                            month = en_date.find('./xs:month',xml_ns)
                            if month is not None:
                                mont =  month.text
                                endate.append(mont)
                            else:
                               endate.append("")
                            days = en_date.find('./xs:day',xml_ns)
                            if days is not None:
                                dys = days.text
                                endate.append(dys)
                            else:
                                endate.append("")
                            #edateyr,enmon,enday = yr,mont,dys
                            end_dte = "|".join(endate)
                            #print end_dte
                    temp_organisn = each_affi.findall('./xs:organization',xml_ns)
                    affi_organisn= []
                    if temp_organisn is not None:
                        organisatn = []
                        for name in temp_organisn:
                            organ_name = name.find('./xs:name',xml_ns)
                            if organ_name is not None:
                                organisatn.append(organ_name.text.encode('utf-8'))
                                print organ_name.text.encode('utf-8')
                            address = name.findall('./xs:address',xml_ns)
                            if address is not None:
                                for each in address:
                                    city = each.find('./xs:city',xml_ns)
                                    if city is not None:
                                        organisatn.append(city.text.encode('utf-8'))
                                    country = each.find('./xs:country',xml_ns)
                                    if country is not None:
                                        organisatn.append(country.text.encode('utf-8'))
                        affi_organisn = ','.join(organisatn)
                    if temp_type == "education":
                        if affi_organisn is not None:
                            self.edu_organisation.append(affi_organisn)
                        else:
                            self.edu_organisation.append("")
      
                        if departmnt is not None:
                            self.edu_dpt.append(departmnt)
                            #print departmnt
                        else:
                            self.edu_dpt.append("")
                        if role is not None:
                            self.edu_role.append(role)
                        else:
                            self.edu_role.append("")
                        if end_dte is not None :
                            self.edu_endate.append(end_dte)
                            #print end_dte
                        else:
                            self.edu_endate.append("")
                        if star_dte is not None:
                            self.edu_stdate.append(star_dte)
                        else:
                            self.edu_endate.append("")
                    elif temp_type == "employment":
                        if affi_organisn is not None: 
                          self.emp_organisation.append(affi_organisn)
                        else:
                            self.emp_organisation.append("")
                        if departmnt is not None:
                            self.emp_dpt.append(departmnt)
                        else:
                            self.emp_dpt.append("")
                        if role:
                            self.emp_role.append(role)
                        else:
                            self.emp_role.append("")
                        if star_dte:
                            self.emp_stdate.append(star_dte)
                            #print star_dte
                        else:
                            self.emp_stdate.append("")

                        if end_dte:
                            self.emp_endate.append(end_dte)
                        else:
                            self.emp_endate.append("")
        
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

