from __future__ import division

import csv
import re
import sqlite3 as dbapi

def get_keywords_fromdb():
    """extracts names of institutions from institution table of citation_metrics 
    database and returns values as a set"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT userID, keyword FROM ecologist_keywords")
    record = cur.fetchone()
    processed_keywords = []
    while record:
        if record:
            list_record = list(record)
            processed_users.extend(list_record)
            record = cur.fetchone()   
    cur.close()
    con.close()
    return processed_users

keyword_data = get_keywords_fromdb()