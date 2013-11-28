#------------------------------------------------------------------------------
# Name:        build_family_from_rm
# Purpose:      given a surname, given name, and date of birth, create a data
#               structure with the household
#
# Author:      pagerk
#
# Created:     14/09/2013
# revised:     4/10/2013 - for fetch persons, added else for the not found case
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------


import logging


def fetch_rm_tables(rm_db):
    """Read the RootsMagic database table and return
        roots_magic_db{'NameTable':name_table,'PersonTable':person_table\
                        'ChildTable':child_table, 'FamilyTable':family_table}
        where each table is a list of the table rows
        where each row is a dict for that row.
    """
    import sys
    sys.path.append('C:\\Users\\pagerk\\PyScripter_Workspace\\Python3Scripts\\MyLib')
    import os, time
    import sqlite3
    import pickle
    from sqlite3_rm_tools import merge, fetchone, fetchall, loadfamily, \
        personString
    from separate_on_caps import separate_on_caps


    #f = open('pickle_rm_db.pkl', 'rb')
    #roots_magic_db = pickle.load(f)

    try:
        connection = sqlite3.connect(rm_db)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print('connection= sqlite3.connect(rm_db) where rm_db =', rm_db)
        raise

    try:
        cursor = connection.cursor()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print('cursor= connection.cursor()')
        raise

    try:
        cursor.execute("SELECT OwnerID, Surname, Given, Prefix, Suffix, \
                                Nickname, IsPrimary, BirthYear, DeathYear \
                                FROM NameTable")
        name_tab = cursor.fetchall()

        # Process NameTable
        name_dict = {}
        name_table = []
        for name in name_tab:
            given = name[2].split(' ')
            name_dict = {'OwnerID': str(name[0]), 'Surname': name[1],
                         'Given': given, 'Prefix': name[3], 'Suffix': name[4],
                         'Nickname': name[5], 'IsPrimary': str(name[6]),
                         'BirthYear': str(name[7]), 'DeathYear': str(name[8])}
            name_table.append(name_dict)

        # Process PersonTable
        cursor.execute("SELECT PersonID,Sex,ParentID,\
                        SpouseID FROM PersonTable")
        person_tab = cursor.fetchall()
        person_dict = {}
        person_table = []
        for person in person_tab:
            person_dict = {'PersonID': str(person[0]), 'Sex': str(person[1]),
                           'ParentID': str(person[2]),
                           'SpouseID': str(person[3])}
            person_table.append(person_dict)

        # Process ChildTable
        cursor.execute("SELECT ChildID,FamilyID,ChildOrder FROM ChildTable")
        child_tab = cursor.fetchall()
        child_dict = {}
        child_table = []
        for child in child_tab:
            child_dict = {'ChildID': str(child[0]), 'FamilyID': str(child[1]),
                          'ChildOrder': str(child[2])}
            child_table.append(child_dict)

        # Process FamilyTable
        cursor.execute("SELECT FamilyID,FatherID,MotherID,\
                       ChildID FROM FamilyTable")
        family_tab = cursor.fetchall()
        family_dict = {}
        family_table = []
        for family in family_tab:
            family_dict = {'FamilyID': str(family[0]),
                           'FatherID': str(family[1]),
                           'MotherID': str(family[2]),
                           'ChildID': str(family[3])}
            family_table.append(family_dict)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    cursor.close()
    connection.close()

    roots_magic_db = {'NameTable': name_table, 'PersonTable': person_table,
                      'ChildTable': child_table, 'FamilyTable': family_table}
    f = open('pickle_rm_db.pkl', 'wb')
    pickle.dump(roots_magic_db, f)
    f.close()

    return roots_magic_db


def fetch_person_from_name(name_table, name_dict):
    """ Given a person's 'Surname', 'Given', 'BirthYear' fetch the NameTable
        entry for that person. If there is more than one match,
        they will all be returned
    """
    import string

    person = {}
    person_matches = []
    for person in name_table:
        #print('fetch_person_from_name .... person =', person)
        #if person['BirthYear'] == '1892' and person['Surname'] == 'Page':
        #    print('fetch_person_from_name rm:   surname = ',person['Surname'],
        # '--- given = ', person['Given'][0], person['BirthYear'],
        #  person['IsPrimary'])
        #    print('fetch_person_from_name srch:   surname = ',
        # name_dict['Surname'], '  fetch_person_from_name: --- given = ',
        # name_dict['Given'], ' --- date = ', name_dict['BirthYear'])
        if person['Surname'].replace(' ', '') == name_dict['Surname']\
                and int(person['BirthYear']) == int(name_dict['BirthYear'])\
                and person['IsPrimary'] == '1':
            #print('person[Given] = ', person['Given'])
            #print('name_dict[Given] = ', name_dict['Given'])
            person_matches.append(person)
            #print('fetch_person_from_name person_matches = ',person_matches)

    #if person_matches == []:
        #print('fetch_person_from_name')
        #print('person not found:', name_dict)
    return person_matches


def fetch_person_from_fuzzy_name(name_table, name_dict, year_error=2):
    """ Given a person's 'Surname', 'Given', 'BirthYear' fetch the NameTable
        entry for that person. If there is more than one match,
        they will all be returned
    """
    import string
    from metaphone import dm

    person = {}
    person_matches = []
    for person in name_table:
        person_sur = dm(person['Surname'].replace(' ', ''))[0]
        name_dict_sur = dm(name_dict['Surname'])[0]
        person_given = dm(person['Given'][0])[0]
        name_dict_given = dm(name_dict['Given'])[0]
        birth_error = abs(int(person['BirthYear']) -
                          int(name_dict['BirthYear']))
        if person_sur == name_dict_sur\
                and person_given == name_dict_given\
                and birth_error <= year_error\
                and person['IsPrimary'] == '1':
            #print('person[Given] = ', person['Given'])
            #print('name_dict[Given] = ', name_dict['Given'])
            #print('person_sur = ', person_sur, '  name_dict_sur = ',\
            # name_dict_sur)
            #print('person_given = ', person_given, '  name_dict_given = ',
            # name_dict_given)
            person_matches.append(person)
            #print('fetch_person_from_name person_matches = ',person_matches)

    #if person_matches == []:
        #print('fetch_person_from_name')
        #print('person not found:', name_dict)
    return person_matches


def fetch_person_from_ID(name_table, id):
    """ Given a person's PersonID (AKA OwnerID) fetch the NameTable entry for
        that person.
    """
    import string

    person = {}

    for person in name_table:
        if person['OwnerID'] == id and person['IsPrimary'] == '1':
            return person
    else:
        print('fetch_person_from_ID')
        print('person not found:', id)
        return person


def fetch_parents_from_ID(person_table, name_table, family_table, person_ID):
    """ Given a target person's PersonID (OwnerID in name_table)
        1. fetch the ParentID (FamilyID in family_table) from the person_table
        2. using the ParentID as the Family_ID fetch the FatherID & MotherID
           from the Family_Table
        3. using the FatherID & MotherID as the name_table OwnerID fetch the
           parents from the NameTable
    """
    import string

    person = {}

    for person in person_table:
        if person['PersonID'] == person_ID:
            parent_ID = person['ParentID']
            for family in family_table:
                if parent_ID == family['FamilyID']:
                    father_ID = family['FatherID']
                    mother_ID = family['MotherID']

    try:
        father = fetch_person_from_ID(name_table, father_ID)
    except:
        father = {}

    try:
        mother = fetch_person_from_ID(name_table, mother_ID)
    except:
        mother = {}

    parents = {'Father': father, 'Mother': mother}

    return parents


def fetch_spouses_from_ID(name_table, person_table, family_table, person_ID):
    """ Given a target person's PersonID (OwnerID in name_table)
        1. get the person's Sex from the PersonTable by searching the personID
        2. fetch the spouse IDs from the family_table
        3. using the spouse IDs fetch the spouse(s) info from the NameTable
    """
    import string

    male = '0'
    female = '1'
    spouses = []
    person = {}

    for person in person_table:
        if person['PersonID'] == person_ID:
            sex = person['Sex']
            for family in family_table:
                if (sex == male) and (family['FatherID'] == person_ID):
                    spouse_id = family['MotherID']
                    for name in name_table:
                        if spouse_id == name['OwnerID'] and \
                                name['IsPrimary'] == '1':
                            #print('fetch_spouses_from_ID------- spouse \
                            # name = ', name)
                            spouses.append(fetch_person_from_ID(name_table,
                                           spouse_id))
                elif (sex == female) and (family['MotherID'] == person_ID):
                    spouse_id = family['FatherID']
                    for name in name_table:
                        if spouse_id == name['OwnerID']:
                            spouses.append(fetch_person_from_ID(name_table,
                                           spouse_id))

    return spouses


def fetch_children_from_ID(child_table, name_table, person_table,
                           family_table, person_ID):
    """ Given a target person's PersonID (OwnerID in name_table)
        1. get the person's Sex from the PersonTable by searching the personID
        2. fetch the FamilyID from the family_table
        3. using the FamilyID fetch the ChildID for each child in the
            ChildTable
        4. Using the ChildID as the OwnerID get each child's info from
            NameTable
    """
    import string

    male = '0'
    female = '1'
    children = []
    family_id = ''

    for person in person_table:
        if person['PersonID'] == person_ID:
            sex = person['Sex']
            for family in family_table:
                if (sex == male) and (family['FatherID'] == person_ID):
                    family_id = family['FamilyID']
                    for child in child_table:
                        if family_id == child['FamilyID']:
                            children.append(fetch_person_from_ID(name_table,
                                            child['ChildID']))

                elif (sex == female) and (family['MotherID'] == person_ID):
                    family_id = family['FamilyID']
                    for child in child_table:
                        if family_id == child['FamilyID']:
                            children.append(fetch_person_from_ID(name_table,
                                            child['ChildID']))
    #print('fetch_children_from_ID------- children = ', children)
    return children


def fetch_family_from_parent(surname, given_name, birth_year):

    rm_db = 'C:\\Users\\pagerk\\PyScripter_Workspace\\Python3Scripts\\MyLib\\myfamily.rmgc'
    tables = fetch_rm_tables(rm_db)

    # Find the target person in the NameTable
    name_dict = {'Surname': surname, 'Given': given_name,
                 'BirthYear': birth_year}
    persons = fetch_person_from_name(tables['NameTable'], name_dict)

    #print('_______________persons\n',persons)

    # Find the parents in the FamilyTable from the ParentID (AKA FamilyID)
    parents = []
    for person in persons:
        parents.append(fetch_parents_from_ID(tables['PersonTable'],
                                             tables['NameTable'],
                                             tables['FamilyTable'],
                                             person['OwnerID']))

    # find the spouse(s) for the target person
    spouses = []
    for person in persons:
        spouses.append(fetch_spouses_from_ID(tables['NameTable'],
                                             tables['PersonTable'],
                                             tables['FamilyTable'],
                                             person['OwnerID']))

    #print('_______________spouses\n',spouses)

    # find the children in the ChildTable by getting the FamilyID from the
    # ParentTable and then getting the children from the ChildTable
    children = []
    for person in persons:
        children.append(fetch_children_from_ID(tables['ChildTable'],
                                               tables['NameTable'],
                                               tables['PersonTable'],
                                               tables['FamilyTable'],
                                               person['OwnerID']))

    family = {'target': persons, 'parents': parents,
              'spouses': spouses, 'children': children}

    return family

if __name__ == '__main__':

    rm_db = 'C:\\Dropbox\\RootsMagic Database\\myfamily.rmgc'
    tables = fetch_rm_tables(rm_db)

    given_name = []
    # Find the target person in the NameTable
    surname = 'Page'
    given_name.append('')
    birth_year = '1949'
    #name_dict = {'Surname':surname, 'Given':given_name,
    #             'BirthYear':birth_year}
    name_dict = {'Surname': 'Page', 'Given': 'Raymond', 'BirthYear': '1921'}
    persons = fetch_person_from_name(tables['NameTable'], name_dict)

    #print('_______________persons\n',persons)

    # Find the parents in the FamilyTable from the ParentID (AKA FamilyID)
    parents = []
    for person in persons:
        parents.append(fetch_parents_from_ID(tables['PersonTable'],
                                             tables['NameTable'],
                                             tables['FamilyTable'],
                                             person['OwnerID']))

    #print('main_______________parents\n',parents)

    # find the spouse(s) for the target person
    spouses = []
    for person in persons:
        spouses.append(fetch_spouses_from_ID(tables['NameTable'],
                                             tables['PersonTable'],
                                             tables['FamilyTable'],
                                             person['OwnerID']))

    #print('_______________spouses\n',spouses)

    # find the children in the ChildTable by getting the FamilyID from the
    # ParentTable and then getting the children from the ChildTable
    children = []
    for person in persons:
        children.append(fetch_children_from_ID(tables['ChildTable'],
                                               tables['NameTable'],
                                               tables['PersonTable'],
                                               tables['FamilyTable'],
                                               person['OwnerID']))

    #print('_______________children\n',children)
