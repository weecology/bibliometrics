from __future__ import division

import csv
import re
import sqlite3 as dbapi

import numpy as np
import pandas as pd

def import_csv(filename):
    """reads in csv file and returns list of lists"""
    infile = open(filename, "rb")
    datareader = csv.reader(infile)
    data = []
    for row in datareader:
        data.append(row)
    del data[0]
    return data  

def create_institution_type_dictionary(data):
    """creates dictionary of institution name and institution type from the 
    Carnegie file"""
    institution_type_dict = {}
    for row in Carnegie_data:
        Institution = row[1]
        Inst_type = int(row[4])
        institution_type_dict[Institution] = Inst_type 
    return institution_type_dict

def get_processedinstitutions_fromdb():
    """extracts names of institutions from institution table of citation_metrics 
    database and returns values as a set"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT google_institution FROM institution_link")
    record = cur.fetchone()
    processed_institutions = []
    while record:
        if record:
            list_record = list(record)
            processed_institutions.extend(list_record)
            record = cur.fetchone()    
    cur.close()
    con.close()
    return set(processed_institutions)

def get_raw_institutions_fromdb():
    """obtains institution name from ecologist table and processes to remove unicode
    formatting. Returns a list of lists."""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    existing_data = cur.execute("SELECT institution FROM ecologist_metrics")
    record = cur.fetchone()
    google_institutions = []
    while record:
        if record:
            list_record = list(record)
            google_institutions.extend(list_record)
            record = cur.fetchone()
    record_institution = [quick_code_strip(record) for record in google_institutions if record]
    cur.close()
    con.close()
    return google_institutions

def notalready_in_database(record, processed_data):
    """Checks to see if institution has already been processed"""
    if record not in processed_data:
        return True
    else:
        return False

def quick_code_strip(record):
    """strips unicode formatting by ignoring errors during decoding unicode"""
    decoded = record.encode('utf-8')
    unicoded = unicode(decoded, errors = 'ignore')
    stringed = str(unicoded)
    return stringed

def apply_first_filter(raw_names, processed_names):
    """This first filter assesses whether the institution name from the 
    ecologist table matches institution names in the Carnegie data. If yes, then
    institution name and carnegie institution type into the institution table.
    Returns list of institution names that did not match carnegie list"""
    bad_names = []
    con=dbapi.connect('citation_metric.sqlite')
    cur1 = con.cursor()
    
    for record in raw_names:
        if record:
            record_institution = quick_code_strip(record)
            not_in_database = notalready_in_database(record_institution, processed_names)
            if not_in_database:
                if Carnegie_institutions.has_key(record_institution):
                    cur1.execute("INSERT INTO institution_link VALUES(?,?,?)", (record_institution, record_institution, Carnegie_institutions[record_institution]) )
                else:
                    bad_names.append(record_institution)
    con.commit()
    return bad_names

"""main code"""
filename = 'Carnegie_Classification_data.csv'
Carnegie_data = import_csv(filename)
Carnegie_institutions = create_institution_type_dictionary(Carnegie_data)

google_institutions = get_raw_institutions_fromdb()
processed_institutions = get_processedinstitutions_fromdb()
bad_names = apply_first_filter(google_institutions, processed_institutions)


    




    

    
    