from __future__ import division

import csv
from urllib import urlopen
import re
import sqlite3 as dbapi
import time

import numpy as np
from bs4 import BeautifulSoup

def import_ecologists(filename):
    """import local file containing a Google Scholar profile in html format"""
    reader = open(filename, 'r')
    datareader = csv.reader(reader, delimiter=',')
    data = []
    for row in datareader:
        data.append(row)
    del data[0]
    return data

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

def notalready_in_database(ecologist, processed_ecologists):
    """Checked to see if ecologist has already been processed and whether html
    address exists for that ecolosist"""
    if ecologist[0] not in processed_ecologists:
        if ecologist[1]:
            return True
        else:
            return False
    else:
        return False

def access_profile_page(url, i):
    """access Google Scholar Profile page and is designed to be used in an iterative
    fashion. i allows main code to keep asscessing profile if papers > 100"""
    #ask Ethan how to modify this so that if no i, then str_i set to 0
    str_i = str(i)
    pattern=((".*user=(.*)&hl=en"))
    user_id=re.search(pattern, url)
    google_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&pagesize=100&view_op=list_works&cstart=" + str_i
    html_file = urlopen(google_html).read()
    return html_file

def processing_pubs(first_page, counter, url):
    """extracts paper data from Google Scholar profile"""
    pubs_from_html=extract_paperdata(first_page)
    counter = 100
    more_papers = True
    while more_papers:
        html_page = access_profile_page(url, counter)
        temp_pubs=extract_paperdata(html_page)
        if len(temp_pubs) > 0:
            pubs_from_html = np.vstack([pubs_from_html, temp_pubs])
            counter += 100
            time.sleep(2)
        else:
            more_papers = False
    return pubs_from_html      

def get_institution(first_profile_page):
    bs_object=BeautifulSoup(first_profile_page)
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

def get_min_year(pub_data):
    years = pub_data[:,4]
    int_years = [int(i) for i in years if i]
    min_year = min(int_years)
    return min_year
    
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

def get_pub_metrics(pub_data):
    citations = get_citations(pub_data)
    first_year = get_min_year(pub_data)
    h_index, total_citations, avg_cites, median_cites = get_citation_metrics(citations)
    return first_year, h_index, total_citations, avg_cites, median_cites
    
def insert_newdata_into_db(pub_data, ecologist, institution):
    """processes publication data and inserts citation metrics and 
    ecologist info into the SQLite database"""
    first_year, h_index, total_citations, avg_cites, median_cites = get_pub_metrics(pub_data)
    con = dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("INSERT INTO ecologist_metrics VALUES(?,?,?,?,?,?,?,?,?,?)", (ecologist[0], ecologist[4], institution, ecologist[2], first_year, len(pub_data),h_index,total_citations,avg_cites, median_cites,))
    con.commit()     
    
"""main code"""
filename_input = "Google_test.csv"
ecologists = import_ecologists(filename_input)
processed_ecologists = get_existingscientists_fromdb()
for ecologist in ecologists:
    not_in_database = notalready_in_database(ecologist, processed_ecologists)
    if not_in_database:
        url = ecologist[1]
        i = 0
        first_html_page = access_profile_page(url, i)
        pubs_data = processing_pubs(first_html_page, i, url)
        institution = get_institution(first_html_page)
        #add keyword scraping here
        insert_newdata_into_db(pubs_data, ecologist, institution)


    
    