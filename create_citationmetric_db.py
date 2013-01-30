from __future__ import division

import csv
from urllib import urlopen
import re
import sqlite3 as dbapi
import time

import numpy as np
from bs4 import BeautifulSoup
import statsmodels.api as sm
import matplotlib.pyplot as plt
import pandas as pd

def import_ecologists(filename):
    """import local file containing a Google Scholar profile in html format"""
    reader = open(filename, 'r')
    datareader = csv.reader(reader, delimiter=',')
    data = []
    for row in datareader:
        data.append(row)
    del data[0]
    return data

def get_Scholarprofile(url):
    """Accesses Google Scholar profile, downloads data for all papers"""
    #refactor this function to just compile the Profile
    pattern=((".*user=(.*)&hl=en"))
    user_id=re.search(pattern, url)
    google_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&view_op=list_works&pagesize=100"
    html_file = urlopen(google_html).read()
    pubs_from_html=extract_paperdata(html_file)
    i=100
    more_papers = True
    while more_papers:
        str_i=str(i)
        iterable_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&pagesize=100&view_op=list_works&cstart=" + str_i
        html_file=urlopen(iterable_html).read()
        temp_pubs=extract_paperdata(html_file)
        if len(temp_pubs) > 0:
            pubs_from_html = np.vstack([pubs_from_html, temp_pubs])
            i += 100
            time.sleep(2)
        else:
            more_papers = False
    return pubs_from_html

def get_institution(url):
    pattern=((".*user=(.*)&hl=en"))
    user_id=re.search(pattern, url)
    google_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&view_op=list_works&pagesize=100"
    html_file = urlopen(google_html).read()    
    bs_object=BeautifulSoup(html_file)
    form = bs_object.find("span", id="cit-affiliation-display")
    affiliation = form.get_text()
    parsed_affiliation =[x.strip() for x in affiliation.split(',')]
    search_patterns = (("(.*[Uu]niv.*)"), ("(.*[Cc]olleg.*)"), ("(.*[Cc]entre.*)"),
                       ("(.*[Cc]enter.*)"), ("(.*[Ii]nstit.*)"))
    for item in parsed_affiliation:
        for pattern in search_patterns:
            institution = re.search(pattern, item)
            if institution:
                return institution.group() 
                
def extract_paperdata(profile_file):
    """parses out paper information from the profile html and outputs numpy array"""
    bs_test=BeautifulSoup(profile_file)
    table = bs_test.find("table", class_="cit-table")
    rows = table.findAll('tr')
    data = [[td.get_text() for td in tr.findAll("td")] for tr in rows]
    del data[0]
    paper_num = len(data)
    data_array = np.array(data)    
    return data_array

def get_citations(paper_data):
    """takes numpy array containing paper info, extracts citation #s and converts to int"""
    citations = paper_data[:,2]
    num_pubs = len(citations)
    int_citations = [int(i) for i in citations if i]
    num_citedpubs = len(int_citations)
    num_zeros = num_pubs-num_citedpubs
    while num_zeros > 0:
        int_citations.append(0)
        num_zeros -= 1
    return int_citations

def get_citation_metrics(citations):
    """calculates citation metrics from publication data numpy array"""
    citations.sort(reverse=True)
    h_index = 0
    for item in citations:
        if item > h_index:
            h_index += 1
    total_citations = sum(citations)
    avg_cites = sum(citations)/len(citations)
    median_cites = np.median(citations)
    return h_index, total_citations, avg_cites, median_cites

def get_existingscientists_fromdb():
    """extracts names of scientists that have already been processed and inserted into
    the database"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    existing_data=cur.execute("SELECT name FROM ecologist_metrics")
    record=cur.fetchone()
    existing_records=[]
    while record:
        existing_records.extend(record)
        record=cur.fetchone()
    return set(existing_records)

def insert_newdata_into_db(ecologist):
    """processes a Google Scholar profile and inserts citation metrics and 
    ecologist info into the SQLite database"""
    GS_profile = get_Scholarprofile(ecologist[1])
    min_year= min(GS_profile[:,4])
    citations = get_citations(GS_profile)
    institution_info= get_institution(ecologist[1])
    h_index, total_citations, avg_cites, median_cites = get_citation_metrics(citations)
    ecologist_data = [ecologist[0], ecologist[4], institution_info, min_year, 
                      len(GS_profile), h_index, total_citations, avg_cites, median_cites]
    con = dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("INSERT INTO ecologist_metrics VALUES(?,?,?,?,?,?,?,?,?)", (ecologist[0], ecologist[4], institution_info, min_year, len(GS_profile),h_index,total_citations,avg_cites, median_cites,))
    con.commit()    
    
"""main code"""
filename_input = "Google_ecology.csv"
ecologists = import_ecologists(filename_input)
processed_ecologists = get_existingscientists_fromdb()
for ecologist in ecologists:
    if ecologist[0] not in processed_ecologists:
        if ecologist[1]:
            insert_newdata_into_db(ecologist)


    
    