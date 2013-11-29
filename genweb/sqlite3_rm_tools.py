#!/usr/bin/env python3

#-------------------------------------------------------------------------------
# Name:        sqlite3_rm_tools
# Purpose:     Extracts people and families from the rootsmagic database
#
# Author:      Marc Page
#
# Created:     24/07/2013
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sqlite3
import sys

#Set the following to try to resolve the error
#  RuntimeError: maximum recursion depth exceeded in comparison
sys.setrecursionlimit(8000)


def merge(cursor, rowItems):
    """ Internal tool to convert an sqlite3 row into a dict
        IN: cursor        The sqlite3 cursor which just did an
                            execute("select") or the like
        IN: rowItems    The result from cursor.fetchone() or one of
                            the items from cursor.fetchall()
        OUT:             A dict with the column headers as the keys
                            for the values in rowItems
    """
    row= {}
    for item in zip(cursor.description,rowItems):
        row[item[0][0]]= item[1]
    return row

def fetchone(cursor):
    """ Alternate interface for cursor.fetchone() that returns
            a dict instead of a list of tuples
        IN: cursor        The sqlite3 cursor which just did an
                            execute("select") or the like
        OUT:            None of no more items, or a dict with columns
                            as keys and row values as values
    """
    hasRow= cursor.fetchone()
    if hasRow:
        return merge(cursor, hasRow)
    return None

def fetchall(cursor, key= None):
    """ Alternate interface for cursor.fetchall() that returns either a list or
            dict of dict of instead of a list of list of tuples
        IN: cursor            The sqlite3 cursor which just did an
                                execute("select") or the like
        IN: key (optional)    None or not set, return a list of dict of values.
                            If a str, it must exactly match (case-sensitive) one
                                    of the columns "select"ed
                                if not an exception will be raised.
                            In the case of key being set, the result will be a
                                dict of dict of values, where the first level
                                dict key is the value of the "key" column.
        OUT:                No more values returns empty array or list
                                (see key for which).
                            If key is set, a dict of dict of values is
                                returned (see key for more info)
                            If key is not set, a list of dict of values is
                                returned
    """
    data= [merge(cursor,x) for x in cursor.fetchall()]
    if key:
        results= {}
        for item in data:
            if key not in item:
                raise SyntaxError("Key column not found: "+key)
            if item[key] in results:
                raise SyntaxError("Not unique: Key: "+str(key)+\
                                    " Non-Unique-Value: "+str(item[key]))
            results[item[key]]= item
        data= results
    return data

def missingKey(item, key):
    if key not in item:
        return "[missing]"
    return item[key]

def dumpSimpleTable(family):
    for NameID in family['NameTable']:
        name= family['NameTable'][NameID]
        print(NameID,"\t","OwnerID",name['OwnerID'],"\t",\
              name['Surname'].encode('utf8'),name['Given'].encode('utf8'),\
              name['BirthYear'])
    print("PersonTable")
    for PersonID in family['PersonTable']:
        person= family['PersonTable'][PersonID]
        print(PersonID,"\t","ParentID",person['ParentID'],"\t","SpouseID",\
               person['SpouseID'],"\t","ChildID",missingKey(person,'ChildID'))
    print("FamilyTable")
    for FamilyID in family['FamilyTable']:
        fam= family['FamilyTable'][FamilyID]
        print(FamilyID,"\t","FatherID",fam['FatherID'],"\t","MotherID",\
              fam['MotherID'],"\t","ChildID",fam['ChildID'])
    print("ChildTable")
    for RecID in family['ChildTable']:
        child= family['ChildTable'][RecID]
        print(RecID,"\t","ChildID",child['ChildID'],"\t","FamilyID",child['FamilyID'])

def loadfamily(cursor):
    """ Example of how to use fetchone() and fetchall()
        Loads entire tables into a dictionary, where the tables
            are the top-level keys.
        In some cases where there is, for instance, FatherID, Father key
            is added that is the dict of the father's NameTable entry

        NameTable
            NameID - rowid
            OwnerID - PersonTable.PersonID
        FamilyTable
            FamilyID - rowid
            FatherID - PersonTable.PersonID
            MotherID - PersonTable.PersonID
            ChildID - PersonTable.PersonID
        PersonTable
            PersonID - rowid
            ParentID - PersonTable.PersonID
            SpouseID - PersonTable.PersonID
            ChildID - PersonTable.PersonID
        ChildTable
            RecID - rowid
            ChildID - PersonTable.PersonID
            FamilyID - FamilyTable.FamilyID
    """

    # Load NameTable, FamilyTable, PersonTable and ChildTable
    family= {}
    cursor.execute("""select "NameID","OwnerID","Surname","Given","Prefix",\
                    "BirthYear","DeathYear" from 'NameTable'""")
    family['NameTable']= fetchall(cursor, key= 'NameID')
    cursor.execute("""select "FamilyID","FatherID","MotherID","ChildID" \
                        from 'FamilyTable'""")
    family['FamilyTable']= fetchall(cursor, key='FamilyID')
    cursor.execute("""select "PersonID","ParentID","SpouseID","ChildID" \
                        from 'PersonTable'""")
    family['PersonTable']= fetchall(cursor, key='PersonID')
    cursor.execute("""select "RecID","ChildID","FamilyID" from 'ChildTable'""")
    family['ChildTable']= fetchall(cursor, key='RecID')

    # Attach name to the "owning" Person in PersonTable
    for NameID in family['NameTable']:
        name= family['NameTable'][NameID]
        if name['OwnerID'] not in family['PersonTable']:
            raise SyntaxError(str(name['OwnerID'])+\
                                    " OwnerID not a key in PersonTable")
        family['PersonTable'][name['OwnerID']]['Name']= name

    # Turn IDs into references to the Person (assuming it is a PersonID)
    for FamilyID in family['FamilyTable']:
        familyInfo= family['FamilyTable'][FamilyID]
        (child, father, mother)= (None, None, None)
        if familyInfo['ChildID'] in family['PersonTable']:
            child= family['PersonTable'][familyInfo['ChildID']]
            familyInfo['Child']= child
        if familyInfo['MotherID'] in family['PersonTable']:
            mother= family['PersonTable'][familyInfo['MotherID']]
            familyInfo['Mother']= mother
        if familyInfo['FatherID'] in family['PersonTable']:
            father= family['PersonTable'][familyInfo['FatherID']]
            familyInfo['Father']= father
        if child and mother:
            child['Mother']= mother
            if 'Children' not in mother:
                mother['Children']= []
            if child not in mother['Children']:
                mother['Children'].append(child)
        if child and father:
            child['Father']= father
            if 'Children' not in father:
                father['Children']= []
            if child not in father['Children']:
                father['Children'].append(child)
        if mother and father:
            if 'Spouse' not in mother:
                mother['Spouse']= []
            if 'Spouse' not in father:
                father['Spouse']= []
            if father not in mother['Spouse']:
                mother['Spouse'].append(father)
            if mother not in father['Spouse']:
                father['Spouse'].append(mother)

    # Turn IDs into references to the Person (assuming it is a PersonID)
    for RecID in family['ChildTable']:
        (ChildID,FamilyID)= (family['ChildTable'][RecID]['ChildID'],\
                              family['ChildTable'][RecID]['FamilyID'])
        FatherID= family['FamilyTable'][FamilyID]['FatherID']
        MotherID= family['FamilyTable'][FamilyID]['MotherID']
        child= None
        father= None
        mother= None
        if ChildID in family['PersonTable']:
            child= family['PersonTable'][ChildID]
        if FatherID in family['PersonTable']:
            father= family['PersonTable'][FatherID]
        if MotherID in family['PersonTable']:
            mother= family['PersonTable'][MotherID]
        if child and mother:
            child['Mother']= mother
            if 'Children' not in mother:
                mother['Children']= []
            if child not in mother['Children']:
                mother['Children'].append(child)
        if child and father:
            child['Father']= father
            if 'Children' not in father:
                father['Children']= []
            if child not in father['Children']:
                father['Children'].append(child)
        if mother and father:
            if 'Spouse' not in mother:
                mother['Spouse']= []
            if 'Spouse' not in father:
                father['Spouse']= []
            if father not in mother['Spouse']:
                mother['Spouse'].append(father)
            if mother not in father['Spouse']:
                father['Spouse'].append(mother)
    return family

def personString(person):
    if 'Name' in person:
        person= person['Name']
        print('person = ', person)
    birthYear= str(person['BirthYear'])
    if birthYear == "0":
        birthYear= ""
    result= " ".join((person['Surname'],person['Given'],birthYear))
    return result.encode('utf8')


if __name__ == "__main__":
    connection= sqlite3.connect('TestDatabase.rmgc')
    #connection= sqlite3.connect('myfamily.rmgc')
    cursor= connection.cursor()
    family= loadfamily(cursor)
    cursor.close()
    connection.close()

    # print entire family hierarchy
    #pprint.PrettyPrinter(indent=2).pprint(family)
    #dumpSimpleTable(family) # simplier table, see adjacent file for example output

    # find the PersonID of Surname Page (list of PersonID,
    #   which is the key for the PersonTable)
    surnamePageIDs= [x for x in list(family['PersonTable'].keys()) \
                         if family['PersonTable'][x]['Name']['Surname']=='Page']

    # turn list of PersonID of Surname Page into list of PersonTable rows
    #    with Surname Page (list of dict)
    surnamePage= [family['PersonTable'][x] for x in surnamePageIDs]

    # Sort the list by birth year (youngest first: "reverse=True")
    surnamePage.sort(key=lambda x:x['Name']['BirthYear'], reverse= True)

    # print out the list of pages by birthyear (for full database,
    #   the depth of printing is too much)
    # pprint.PrettyPrinter(indent=2).pprint(surnamePage)
    """
    # ensure unique SURNAME-INITIAL-YEAR
    people= {}
    for PersonID in family['PersonTable']:
        name= family['PersonTable'][PersonID]['Name']
        key= name['Surname']
        if len(name['Given']) > 0:
            key+=name['Given'][0]
        if name['BirthYear'] > 0:
            key+= str(name['BirthYear'])
        if key in people:
            print("NOT UNIQUE:",key,"=",personString(name),"&",personString(people[key]))
        people[key]= name
    """
    # ensure unique SURNAME-GIVEN-YEAR
    people= {}
    for PersonID in family['PersonTable']:
        name= family['PersonTable'][PersonID]['Name']
        key= name['Surname']
        if len(name['Given']) > 0:
            given_1 = name['Given'].partition(' ')
            given_2 = given_1[2]
            key+=given_1[0]
            if len(given_2) > 0:
                key+= given_2[0]
        if name['BirthYear'] > 0:
            key+= str(name['BirthYear'])
        if key in people:
            print("NOT UNIQUE:",key,"=",personString(name),"&",\
                                        personString(people[key]))
        people[key]= name

    # Go through each person in surnamePage and print direct family relationships
    for page in surnamePage:
        print(personString(page))
        if 'Mother' in page:
            print("\t","Mother",personString(page['Mother']))
        if 'Father' in page:
            print("\t","Father",personString(page['Father']))
        if 'Spouse' in page:
            for spouse in page['Spouse']:
                print("\t","Spouse",personString(spouse))
        if 'Children' in page:
            print("\t""Children")
            children= page['Children']
            children.sort(key=lambda x:x['Name']['BirthYear'])
            for child in page['Children']:
                print("\t\t",personString(child))
