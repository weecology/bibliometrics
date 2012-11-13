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

author_pubs=get_pubinfo(test)
bs_test=BeautifulSoup(test)
paper_info=bs_test.find_all(id='col-title')


title_pattern=(('.*>([A-Za-z].+)<.*"cit-gray">(.*)</span><br/>.*"cit-gray">(.*)</span>.*'))
pattest=(('<td id="col-title"><a class="cit-dark-large-link" href="/citations?view_op=view_citation&amp;hl=en&amp;user=DUQgBw4AAAAJ&amp;citation_for_view=DUQgBw4AAAAJ:u5HHmVD_uO8C">Strong self-limitation promotes the persistence of rare species</a><br/><span class="cit-gray">G Yenni, PB Adler, SKM Ernest</span><br/><span class="cit-gray">Ecology 93 (3), 456-461</span></td>'))
paper_title=re.search(title_pattern, pattest)   
if paper_title:
    print paper_title.group(1)
    print paper_title.group(2)
    print paper_title.group(3)
else:
    print "try again"
    
   
    
 
    
