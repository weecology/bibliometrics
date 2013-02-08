from __future__ import division

import csv
import re
import sqlite3 as dbapi

import numpy as np
import pandas as pd

def import_csv(filename):
    infile = open(filename, "rb")
    datareader = csv.reader(infile)
    data = []
    for row in datareader:
        data.append(row)
    del data[0]
    return data  

def create_institution_type_dictionary(data):
    institution_type_dict = {}
    for row in Carnegie_data:
        Institution = row[1]
        Inst_type = int(row[4])
        institution_type_dict[Institution] = Inst_type 
    return institution_type_dict


filename = 'Carnegie_Classification_data.csv'
Carnegie_data = import_csv(filename)
Carnegie_institutions = create_institution_type_dictionary(Carnegie_data)


    

    
    