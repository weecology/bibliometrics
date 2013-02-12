from __future__ import division

import csv
import re
import sqlite3 as dbapi

import pandas as pd

def get_keywords_fromdb():
    """extracts keywords from ecologist_keywords table of citation_metrics 
    database and returns values"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT keyword FROM ecologist_keywords")
    record = cur.fetchone()
    raw_keywords = []
    while record:
        if record:
            list_record = list(record)
            raw_keywords.extend(list_record)
            record = cur.fetchone()   
    cur.close()
    con.close()
    return raw_keywords

def notalready_in_database(keyword):
    """Checks to see if keyword has already been processed"""
    processed_data = get_processeddata_fromdb()
    if processed_data:
        processed_keywords = set(processed_data)              
        if keyword not in processed_keywords:
            return True
        else:
            return False
    else:
        return True

def get_processeddata_fromdb():
    """returns keywords from keyword_link table as list"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT ecologist_keyword FROM keyword_link")
    record = cur.fetchone()
    processed_data = []
    while record:
        if record:
            list_record = list(record)
            processed_data.extend(list_record)
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
    """returns a set of unique  (and lacking unicode codes) keywords that are in 
    table ecologist_keywords"""
    unique_keywords = set(data)  
    cleaned_keywords = []
    for item in unique_keywords:
        clean_keyword = quick_code_strip(item)
        cleaned_keywords.append(clean_keyword)
    return set(cleaned_keywords)

def create_keyword_dictionary(data):
    """returns a dictionary linking the keyword from the ecologist_keywords table
    with a standardized ecological subdiscipline"""
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
    """checks to see if item is in the dictionary, returns False if missing"""
    subdiscipline = dictionary.get(item, False)
    return subdiscipline      

def insert_keyword_subdiscipline_db_table(data_set, dictionary):
    """inserts new keywords and their subdisipline into the keyword_link table"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    not_in_dictionary = []
    for item in data_set:
        not_already_processed = notalready_in_database(item)
        if notalready_in_database:
            subdiscipline = get_subdiscipline(item, dictionary)
            if subdiscipline:
                cur.execute ("INSERT INTO keyword_link VALUES(?,?)", (item, subdiscipline))
    con.commit()
    cur.close()
    con.close()

"""main code"""
keyword_data = get_keywords_fromdb()
keyword_set = make_keyword_set(keyword_data)
keyword_dictionary = create_keyword_dictionary(keyword_set)
insert_keyword_subdiscipline_db_table(keyword_set, keyword_dictionary) 