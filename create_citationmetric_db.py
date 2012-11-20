import csv
from urllib import urlopen
from bs4 import BeautifulSoup
import numpy as np
import re
import sqlite3 as dbapi

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
    """Accesses Google Scholar profile, downloads up to 700 papers""" 
    pattern=((".*user=(.*)&hl=en"))
    user_id=re.search(pattern, url)
    google_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&view_op=list_works&pagesize=100"
    html_file = urlopen(google_html).read()
    pubs_from_html=extract_paperdata(html_file)
    i=100
    while i < 700:
        str_i=str(i)
        iterable_html="http://scholar.google.com/citations?hl=en&user=" + user_id.group(1) + "&pagesize=100&view_op=list_works&cstart=" + str_i
        html_file=urlopen(iterable_html).read()
        temp_pubs=extract_paperdata(html_file)
        if len(temp_pubs) > 0:
            pubs_from_html = np.vstack([pubs_from_html, temp_pubs])
            i += 100
        else:
            return pubs_from_html

def extract_paperdata(profile_file):
    """parses out paper information from the profile html and outputs numpy array"""
    bs_test=BeautifulSoup(profile_file)
    table = bs_test.find("table", class_="cit-table")
    rows = table.findAll('tr')
    data = [[td.findChildren(text=True) for td in tr.findAll("td")] for tr in rows]
    del data[0]
    paper_num = len(data)
    data_array = np.array(data)    
    return data_array

def get_citations(paper_data):
    """takes numpy array containing paper info, extracts citation #s and converts to int"""
    citations = paper_data[:,2]
    num_pubs = len(citations)
    citations = [int(i[0]) for i in citations if i]
    num_citedpubs = len(citations)
    num_zeros = num_pubs-num_citedpubs
    while num_zeros > 0:
        citations.append(0)
        num_zeros -= 1
    return citations

def median(mylist):
    """calculates a median from a list of numbers"""
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

def get_citation_metrics(citations):
    """calculates citation metrics from publication data numpy array"""
    citations.sort(reverse=True)
    h_index = 0
    for item in citations:
        if item > h_index:
            h_index += 1
    total_citations = sum(citations)
    avg_cites = sum(citations)/len(citations)
    median_cites = median(citations)
    if len(citations) > 699:
        limit_exceeded_flag=1
    else:
        limit_exceeded_flag=0
    return h_index, total_citations, avg_cites, median_cites, limit_exceeded_flag

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
    """processes a profile and inserts citation metrics into the SQLite database"""
    GS_profile = get_Scholarprofile(ecologist[1])
    citations = get_citations(GS_profile)
    h_index, total_citations, avg_cites, median_cites, paper_limit = get_citation_metrics(citations)
    ecologist_data = [ecologist[0], ecologist[4], len(GS_profile), h_index, 
                    total_citations, avg_cites, median_cites, paper_limit]
    cur.execute("INSERT INTO ecologist_metrics VALUES(?,?,?,?,?,?,?,?)", (ecologist[0],ecologist[4],len(GS_profile),h_index,total_citations,avg_cites, median_cites, paper_limit,))
    con.commit()    
    
"""main code"""
filename_input = "test_profiles.csv"
ecologists = import_ecologists(filename_input)
processed_ecologists = get_existingscientists_fromdb()
for ecologist in ecologists:
    if ecologist[0] not in processed_ecologists:
        insert_newdata_into_db(ecologist)
        
con.close()


    



    
    
    