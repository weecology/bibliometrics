import csv
from urllib import urlopen
from bs4 import BeautifulSoup
import re

def export_to_csv(data, filename):
    """Export a list of lists to a CSV file"""
    output_file = open(filename, 'w')
    datawriter = csv.writer(output_file, delimiter)
    datawriter.writerows(data)
    output_file.close()
    return 

"""Accessing googlescholarthrough url and modifying url to display more than default number of pubs"""
#url = "http://scholar.google.com/citations?hl=en&user=uLElX8AAAAAJ"
#url_all=url+"&view_op=list_works&pagesize=100"
#html = urlopen(url).read()    

test_file=open("yenni_test.htm")
test=test_file.read()
test_file.close()

bs_test=BeautifulSoup(test)
paper_info=bs_test.find_all(id='col-title')


    
    
    
    
    
   
    
 
    
