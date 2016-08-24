# RDF_generation
Generating the xml extracts into rdf.


## generatetext.py
This file reads the xml file and generates the text file with required data
The text file has:
1) pmid
2) orcid ID
3) First name
4) Last name
5) Other name


## testDB

This file reads the text file and builds the datbase of orcid profile.
database name: ORCIDPROFILE
schema: ORCIDschema
Table: orcidprofile
columns: pmid,orcidid,firstname,lastname,othername
Composite primary key : pmid, orcidid

