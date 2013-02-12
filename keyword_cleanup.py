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
    cur.close()
    con.close()
    return raw_keywords

def notalready_in_database(record):
    """Checks to see if institution has already been processed"""
    processed_data = get_processeddata_fromdb()
    if processed_data:
        userID = record[0]
        keyword = record[1]
        processed = pd.DataFrame(processed_data, columns=['UserID', 'ecologist_keyword'])
        processed_users = set(processed['UserID'])
        processed_keywords = set(processed['ecologist_keyword'])
                             
        if userID not in processed_users:
            return True
        elif keyword not in processed_keywords:
            return True
        else:
            return False
    else:
        return True

def get_processeddata_fromdb():
    """extracts userID and keyword from keyword_link table"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT userID, ecologist_keyword FROM keyword_link")
    record = cur.fetchone()
    processed_data = []
    while record:
        if record:
            list_record = list(record)
            processed_data.append(list_record)
            record = cur.fetchone()
    cur.close()
    con.close()
    return processed_data

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
    dataframe = pd.DataFrame(data, columns=['UserID', 'keyword'])
    unique_keywords = set(dataframe['keyword'])  
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
                break
            else:
                index +=1    
    return keyword_dictionary  

def get_subdiscipline(item, dictionary):
    try:
        subdiscipline = dictionary[item]
        return subdiscipline
    except KeyError:
        return False
        
    
"""main code"""
keyword_data = get_keywords_fromdb()
keyword_set = make_keyword_set(keyword_data)
keyword_dictionary = create_keyword_dictionary(keyword_set)

con=dbapi.connect('citation_metric.sqlite')
cur = con.cursor()
for row in keyword_data:
    not_already_processed = notalready_in_database(row)
    if notalready_in_database:
        subdiscipline = get_subdiscipline(row[1], keyword_dictionary)
        if subdiscipline:
            cur.execute ("INSERT INTO keyword_link VALUES(?,?,?)", (row[0], row[1], subdiscipline))
con.commit()
cur.close()
con.close()

    




        
        

#make_csv("keyword.csv", cleaned_keywords)


