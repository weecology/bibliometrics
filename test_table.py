import csv
from urllib import urlopen
from bs4 import BeautifulSoup
import re

"""Accessing googlescholarthrough url and modifying url to display more than default number of pubs"""
#url = "http://scholar.google.com/citations?hl=en&user=uLElX8AAAAAJ"
#url_all=url+"&view_op=list_works&pagesize=100"
#html = urlopen(url).read()    

"""Opening a test file locally"""
test_file=open("test_page.htm")
test=test_file.read()
test_file.close()

"""Extract the citation table from the user page and parsing into units all grouped by paper"""
bs_test=BeautifulSoup(test)
table = bs_test.find("table", class_="cit-table")
rows = table.findAll('tr')
data = [[td.findChildren(text=True) for td in tr.findAll("td")] for tr in rows]

for paper in data:
    del paper[3]
    del paper[0]
    print paper