from __future__ import division

import csv
import re
import sqlite3 as dbapi

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

def get_processedusers_fromdb():
    """extracts names of institutions from institution table of citation_metrics 
    database and returns values as a set"""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    cur.execute("SELECT userID FROM institution_link")
    record = cur.fetchone()
    processed_users = []
    while record:
        if record:
            list_record = list(record)
            processed_users.extend(list_record)
            record = cur.fetchone()   
    cur.close()
    con.close()
    return set(processed_users)

def get_raw_institutions_fromdb():
    """obtains institution name from ecologist table and processes to remove 
    unicode formatting. Returns a list of lists."""
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    existing_data = cur.execute("SELECT userID, institution FROM ecologist_metrics")
    record = cur.fetchone()
    google_institutions = []
    while record:
        if record:
            list_record = list(record)
            google_institutions.append(list_record)
            record = cur.fetchone()
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
        if record[1]:         
            not_in_database = notalready_in_database(record[0], processed_names)
            if not_in_database:
                record_institution = quick_code_strip(record[1])
                if Carnegie_institutions.has_key(record_institution):
                    cur1.execute("INSERT INTO institution_link VALUES(?,?,?,?)", 
                                 (record[0], record_institution, record_institution, 
                                  Carnegie_institutions[record_institution]) )
                else:
                    nomatch = [record[0], record_institution]
                    bad_names.append(nomatch)
    con.commit()
    cur1.close()
    con.close()
    return bad_names

def remove_obvious_foreign_names(bad_names):
    """filters out institute names with general foreign identifiers"""
    patterns = ['Instituto', 'Centre', 'Universidad', 'Universite',
                'Universita', 'Universidade', 'Universit degli', 'Universit de',
                'Australia', 'Czech', 'Finish', 'Malaysia', 'Institut de', 
                'Singapore', 'Netherlands', 'Norweigian', 'African', 
                'KwaZulu-Natal', 'Swedish', 'Universit di', 'Finland']
    new_badnames = []
    
    for i in bad_names:
        pattern_alert = 0
        for p in patterns:
            pattern_match = re.search(p, i[1])
            if pattern_match:
                pattern_alert +=1
        if pattern_alert == 0:
            new_badnames.append(i)
            
    return new_badnames

def make_csv(filename, data):
    """write data to a csv file"""
    writer = open(filename, 'w')
    for row in data:
        print >> writer, row
    writer.close()

def insert_fixed_institutions(fixed_data):
    user_set = get_processedusers_fromdb()
    
    con=dbapi.connect('citation_metric.sqlite')
    cur = con.cursor()
    for row in fixed_data:
        cleaning_user = row[0].replace("u'", "")
        user_ID = cleaning_user.replace("'", "")
        old_institution = row[1].replace("'", "")
        if user_ID not in user_set:
            cur.execute("INSERT INTO institution_link VALUES(?,?,?,?)", 
                                     (user_ID, old_institution, row[2], Carnegie_institutions[row[2]]))
    con.commit()
    cur.close()
    con.close()    
    
"""main code"""
filename = 'Carnegie_Classification_data.csv'
Carnegie_data = import_csv(filename)
Carnegie_institutions = create_institution_type_dictionary(Carnegie_data)

google_institutions = get_raw_institutions_fromdb()
processed_users = get_processedusers_fromdb()
bad_names = apply_first_filter(google_institutions, processed_users)
filtered_badnames = remove_obvious_foreign_names(bad_names)
make_csv('Bad_names.csv', filtered_badnames)

fixed_institutions = import_csv("Badnames_fixed.csv")
insert_fixed_institutions(fixed_institutions)


                 





    




    

    
    