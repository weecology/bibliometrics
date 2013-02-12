from __future__ import division

import csv
import re
import sqlite3 as dbapi

import pandas as pd

def get_keywords_fromdb():
    """extracts names of institutions from institution table of citation_metrics 
    database and returns values as a set"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT userID, keyword FROM ecologist_keywords")
    record = cur.fetchone()
    raw_keywords = []
    while record:
        if record:
            list_record = list(record)
            raw_keywords.append(list_record)
            record = cur.fetchone()   
    dataframe = pd.DataFrame(raw_keywords, columns=['UserID', 'keyword'])
    cur.close()
    con.close()
    return dataframe

def make_csv(filename, data):
    """write data to a csv file"""
    writer = open(filename, 'w')
    for row in data:
        print >> writer, row
    writer.close()

def quick_code_strip(record):
    """strips unicode formatting by ignoring errors during decoding unicode"""
    decoded = record.encode('utf-8')
    unicoded = unicode(decoded, errors = 'ignore')
    stringed = str(unicoded)
    return stringed

def make_keyword_set(data):
    unique_keywords = set(data['keyword'])  
    cleaned_keywords = []
    for item in unique_keywords:
        clean_keyword = quick_code_strip(item)
        cleaned_keywords.append(clean_keyword)
    return cleaned_keywords

def create_keyword_dictionary(data):
    keyword_dictionary = {}
    for item in keyword_set:
        ecology_patterns = (('.*[Cc]ommunity\s[Ee]cology.*'), 
                            ('.*[Ee]cosystem\s[Ee]cology.*'), 
                            ('.*[Pp]opulation\s[Ee]cology].*'),
                            ('.*[Pp]hysiological\s[Ee]cology.*'),
                            ('.*[Bb]ehavioral\s[Ee]cology.*'), 
                            ('.*[Bb]ehavioural\s[Ee]cology.*'),
                            ('.*[Ee]volutionary\s[Ee]cology.*'),
                            ('.*[Tt]heoretical\s[Ee]cology.*'),
                            ('.*[Ll]andscape\s[Ee]cology.*'),
                            ('.*[Mm]acroecology.*'), 
                            ('.*[Pp]aleoecology.*'), 
                            ('.*[Cc]onservation\s[Bb]iology.*'))
        ecology_keyword = ['Community Ecology','Ecosystem Ecology', 
                           'Population Ecology', 'Physiological Ecology', 
                           'Behavioral Ecology', 'Behavioural Ecology', 
                           'Evolutionary Ecology', 'Theoretical Ecology',
                           'Landscape Ecology', 'Macroecology', 'Paleoecology', 
                           'Conservation Biology']
        index = 0
        for p in ecology_patterns:
            pattern_match = re.search(p, item)
            if pattern_match:
                keyword_dictionary[item] = ecology_keyword[index]
                print(item, keyword_dictionary[item])
                break
            else:
                index +=1    
    return keyword_dictionary  

"""main code"""
keyword_data = get_keywords_fromdb()
keyword_set = make_keyword_set(keyword_data)
keyword_dictionary = create_keyword_dictionary(keyword_set)



        
        

#make_csv("keyword.csv", cleaned_keywords)


