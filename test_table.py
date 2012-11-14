import csv
from urllib import urlopen
from bs4 import BeautifulSoup
import numpy as np
import re

def import_localfile(filename):
    """import local file containing a Google Scholar profile in html format"""
    test_file=open(filename)
    test=test_file.read()
    test_file.close()
    return test

def get_Scholarprofile(url):
    """Accessing googlescholarthrough url and modifying url to display more than default number of pubs"""
    url_all=url+"&view_op=list_works&pagesize=100"
    html = urlopen(url).read() 
    return html

def extract_paperdata(profile_file):
    """parses out paper information from the profile html and outputs numpy array"""
    bs_test=BeautifulSoup(test)
    table = bs_test.find("table", class_="cit-table")
    rows = table.findAll('tr')
    data = [[td.findChildren(text=True) for td in tr.findAll("td")] for tr in rows]
    del data[0]
    paper_num = len(data)
    data_array = np.array(data)    
    return data_array

filename = "test_page.htm"
profile = import_localfile(filename)
publications = extract_paperdata(profile)

#Below this line is imperfect code
citations = publications[:,2]
num_pubs = len(citations)
citations = [int(i[0]) for i in citations if i]
num_citedpubs = len(citations)
num_zeros = num_pubs-num_citedpubs
while num_zeros > 0:
    citations.append(0)
    num_zeros -= 1
    



    
    
    