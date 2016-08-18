#!/usr/bin/env python3

import os
import time
import datetime
import winsound
import glob
import re
import pickle
import sys
from . import rmagic

#sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts/MyLib')

class build_web_pages(object):
    """
    This module will build the family history web pages:
        Build table of contents html files
         - _generate_toc_web(families_dict, folders_path)
        Build hourglass html file for each person
         - _generate_all_hourglass_webs(family_dict, folders_path)
        Build the web page for each person's artifacts
         - _generate_person_web(family_dict, persons_xml_dict, folders_path)
    """
    def __init__(self, rmagicPath):

        if sys.platform == "win32":
            timer = time.clock
        else:
            timer = time.time
        start_time = stop_time = 0
        start_time = timer()

        os.chdir('C:/Users/pager/PyScripter_Workspace/genweb')
        paths = open('genweb_paths.txt', 'r')
        folders_path = paths.readline()[0:-1]
        #rmagicPath = paths.readline()
        paths.close()

        os.chdir(folders_path)
        dictionaries_path = folders_path + '/___dictionaries'

        self._rmagicPath = rmagicPath
        # _tables keys are:['ChildTable',
        #                   'FamilyTable',
        #                   'NameTable',
        #                   'PersonTable',
        #                   'ownerid_name_table',
        #                   'person_id_person_table',
        #                   'family_id_family_table']
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)
        self._matched_persons = []

        # For each target person in name_table, create a dictionary containing
        # the name_table information for 'target', 'parents', 'children', 'spouses'
        # The key for each target is their long_genwebid
        # families_dict =
        #   'target: name_table_entry for target
        # where the entry for a given person is:
        #       {
        #           'OwnerID': str(name[0]),
        #           'Surname': name[1],
        #           'Given': given,
        #           'Prefix': name[3],
        #           'Suffix': name[4],
        #           'Nickname': name[5],
        #           'IsPrimary': str(name[6]),
        #           'BirthYear': str(name[7]),
        #           'DeathYear': str(name[8]),
        #           'FullName' : FullName
        #       }
        #   'parents': {'mother: name_table_entry for mother,'father: name_table_entry for father}
        #   'spouses' : [{name_table_entry for spouse1},...]
        #   'children' : [{name_table_entry for child1},...]
        # where each name_table entry will have the addition key: 'long_genwebid'
        # and the appropriate value.

        families_dict = {}
        revised_name_table_entry = {}
        revised_name_table = {}

        if os.path.isfile(rmagicPath):
            rmagic_mod_time = os.stat(rmagicPath).st_mtime
        else:
            print("no roots magic mod time ", rmagicPath)
            rmagic_mod_time = 0

        file_name = dictionaries_path + '/aaa_revised_name_table.pikl'
        if os.path.isfile(file_name):
            name_table_pkl_mod_time = os.stat(file_name).st_mtime
        else:
            name_table_pkl_mod_time = 0

        print('line 94 rmagic_mod_time = ', rmagic_mod_time)
        print('line 95 name_table_pkl_mod_time = ', name_table_pkl_mod_time)
        print('line 96 if rmagic_mod_time > name_table_pkl_mod_time then get rmagic tables')

        if rmagic_mod_time > name_table_pkl_mod_time:
            for name_table_entry in self._tables['NameTable']:
                #print('name_table_entry entry = ', str(name_table_entry))
                if name_table_entry['IsPrimary'] == '0':
                    continue

                revised_name_table_entry = self._get_long_genwebid(name_table_entry)

                if revised_name_table_entry == {}:
                    continue

                #print('revised_name_table_entry = ', str(revised_name_table_entry))

                family_dict = self._get_family(revised_name_table_entry)
                """
                 family_dict =
                   'target: name_table_entry for target
                   'parents':
                     {'mother: name_table_entry for mother,
                      'father: name_table_entry for father}
                   'spouses' : [{name_table_entry for spouse1},...]
                   'children' : [{name_table_entry for child1},...]
                 where each name_table entry will also have key: 'long_genwebid'
                 and the appropriate value.
                 The key for each target is their long_genwebid

                where the keys for an individual are:
                    'OwnerID'
                    'Surname'
                    'Given' (a list of the given names)
                    'Prefix'
                    'Suffix'
                    'Nickname'
                    'IsPrimary'
                    'BirthYear'
                    'DeathYear'
                    'FullName'
                """
                if family_dict['target']['OwnerID'] == '17000':
                    print('line 137 - family_dict = ', family_dict)
                    print('line 138 - revised_name_table_entry = ', revised_name_table_entry)

                revised_name_table[revised_name_table_entry['long_genwebid']] = family_dict
            self._save_dictionary(revised_name_table, file_name)
            dict_txt_file = open(file_name + '.dict', 'w')
            dict_txt_file.write('line 137 dict_txt_file: ' + str(revised_name_table))
            dict_txt_file.close()
        else:
            revised_name_table = self._load_dictionary(file_name)

        #----------------------------------------
        # the following lines will load the date of the latest change to any xml file
        # I will use this to avoid re-creating the xml dictionary files if nothing has changed
        """
        file_name_latest_xml_mod = dictionaries_path + '/file_name_latest_xml_mod.dat'
        if os.path.isfile(file_name_latest_xml_mod):
            xml_mod_time = os.stat(file_name_latest_xml_mod).st_mtime
        else:
            xml_mod_time = 1
            f = open(file_name_latest_xml_mod,'w')
            f.close()

        print('line 156 xml_mod_time = ', xml_mod_time)

        file_name_latest_pkl_create = dictionaries_path + '/file_name_latest_pkl_create.dat'
        if os.path.isfile(file_name_latest_pkl_create):
            pkl_create_time = os.stat(file_name_latest_pkl_create).st_mtime
        else:
            pkl_create_time = 0

        print('line 165 pkl_create_time = ', pkl_create_time)
        print('line 166 if pkl_create_time !> xml_mod_time then get_proj_dict_from_xml')

        if pkl_create_time > xml_mod_time:
            refresh_get_proj_dict_from_xml = False
        else:
            refresh_get_proj_dict_from_xml = True
            # I will clear it out first since people may have been changed or deleted
            for f in glob.glob(dictionaries_path + '/*.dic'): os.remove(f)
            for f in glob.glob(dictionaries_path + '/*.pkl'): os.remove(f)
            g = open(file_name_latest_pkl_create,'w')
            g.close()

        """
        refresh_get_proj_dict_from_xml = True
        generate_table_of_contents = True
        generate_hourglass = True
        generate_web_pages = True

        if refresh_get_proj_dict_from_xml:
            self._get_proj_dict_from_xml(folders_path)# saves xml in pickle file

        people_ids = glob.glob("*[0-9][0-9][0-9][0-9]*")

        #----------------------------------------
        print('____________________________________')
        print('The following long genwebids are not found in the RootsMagic database:')
        for person in people_ids:
            if person in revised_name_table:
                families_dict[person] = revised_name_table[person]
                #print('line 193 families_dict = ', str(families_dict))
            else:
                print("line 195 - person not in revised_name_table: person = ", str(person))
        #print('End of list')
        """
        families_dict only contains revised_name_table info for people who have folders
        sample families_dict entry:
        families_dict =
        {'AbdillAliceH1923SmithAgnessF1900':
            {'spouses': [],
             'children': [],
             'target':
                {'BirthYear': '1923',
                 'Nickname': '',
                 'Given': ['Alice', 'H'],
                 'Sex': 'female',
                 'OwnerID': '15390',
                 'IsPrimary': '1',
                 'Suffix': '',
                 'long_genwebid': 'AbdillAliceH1923SmithAgnessF1900',
                 'GenWebID': 'AbdillAliceH1923',
                 'Prefix': '',
                 'DeathYear': '0',
                 'Surname': 'Abdill',
                 'FullName': 'Abdill, Alice H'
                },
             'parents':
                    {'mother': {'BirthYear': '1900', 'Nickname': '',
                     'Given': ['Agness', 'F'], 'Sex': 'female', 'OwnerID': '2596',
                     'IsPrimary': '1', 'Suffix': '', 'long_genwebid': 'SmithAgnessF1900-',
                     'GenWebID': 'SmithAgnessF1900', 'Prefix': '', 'DeathYear': '0',
                     'Surname': 'Smith', 'FullName': 'Smith, Agness F'},

                     'father': {'BirthYear': '1895', 'Nickname': '',
                     'Given': ['Ralph', 'Gilford'], 'Sex': 'male', 'OwnerID': '2595',
                     'IsPrimary': '1', 'Suffix': '',
                     'long_genwebid': 'AbdillRalphG1895WoolworthMaryE1874',
                     'GenWebID': 'AbdillRalphG1895', 'Prefix': '', 'DeathYear': '1960',
                     'Surname': 'Abdill', 'FullName': 'Abdill, Ralph Gilford'}
                    }
            }
        }
        """
        # generating toc web pages
        if generate_table_of_contents:
            self._generate_toc_web(families_dict, folders_path)

        #----------------------------------------

        family_dict = {}
        for long_genwebid in people_ids: # people_ids = list of folder names

            # load the xml info for this person
            current_file = dictionaries_path + '/' + long_genwebid + '.pkl'
            persons_xml_dict = self._load_dictionary(current_file)
            """
            persons_xml_dict =
                {'person_info':		[persons_id,mothers_id],
                 'artifacts_info':
                    {artifact_id: {'type':'picture','title':'title txt here', ...
                    }
                    {artifact_id: {'type':'picture','title':'title txt here',...
                    }
                     ...
                }
            """

            if long_genwebid in families_dict:
                family_dict = families_dict[long_genwebid]
            else:
                print("long_genwebid = ", long_genwebid, "  is not a valid key in families_dict")
                continue
            if generate_web_pages and persons_xml_dict['artifacts_info'] != {}:
                self._generate_person_web2(family_dict, persons_xml_dict, folders_path)

            if generate_hourglass:  # this must come after generate_web_pages -
                                    # don't want hourglass if no web page
                self._generate_all_hourglass_webs(family_dict, folders_path)

        stop_time = timer()
        print('execution time =', int((stop_time - start_time)//60), ' minutes, ',  \
                int((stop_time - start_time)%60), ' seconds or ', \
                (stop_time - start_time), ' seconds total')
        winsound.Beep(500, 1000)
        winsound.Beep(500, 1000)

#--------------------------------------------------__init__

    def _get_long_genwebid(self, tgt_name_table_entry):
        # Given a person's PersonID (AKA OwnerID) generate the long_genwebid
        # The return is the [long_genwebid, revised_tgt_name_table_entry]
        # self._tables keys are:['ChildTable',
        #                        'FamilyTable',
        #                        'NameTable',
        #                        'PersonTable',
        #                        'ownerid_name_table',
        #                        'person_id_person_table',
        #                        'family_id_family_table']
        family_id_family_table = self._tables['family_id_family_table']
        person_id_person_table = self._tables['person_id_person_table']
        ownerid_name_table = self._tables['ownerid_name_table']

        debug = False
        #print('tgt_name_table_entry = ', str(tgt_name_table_entry))
        if tgt_name_table_entry == {}:
            return {}
        if tgt_name_table_entry['OwnerID'] == '':
            debug = True
        """
        where tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear': }

        where revised_tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear':,
                                        'Sex':,
                                        'long_genwebid':
                                      }
        """
        revised_tgt_name_table_entry = tgt_name_table_entry
        if person_id_person_table[tgt_name_table_entry['OwnerID']]['Sex'] == '0':
            person_sex = 'male'
        else:
            person_sex = 'female'
        revised_tgt_name_table_entry['Sex'] = person_sex

        if tgt_name_table_entry['BirthYear'] == '0':
            birth_year = '0000'
        elif len(tgt_name_table_entry['BirthYear']) == 3:
            birth_year = '0' + tgt_name_table_entry['BirthYear']
        else:
            birth_year = tgt_name_table_entry['BirthYear']

        revised_tgt_name_table_entry['BirthYear'] = birth_year

        # create the tgt_short_genweb_id
        tgt_short_genweb_id = tgt_name_table_entry['Surname']

        for given_num in range(len(tgt_name_table_entry['Given'])):
            if given_num == 0  and len(tgt_name_table_entry['Given'][0]) <= 1: #changed from 2 to 1 20160623
                return {}
            if given_num == 0:
                tgt_short_genweb_id = tgt_short_genweb_id + tgt_name_table_entry['Given'][0]
                if debug:
                    print('tgt_short_genweb_id1 = ', tgt_short_genweb_id)
            else:
                if debug:
                    print('given_num = ', given_num)
                if len(tgt_name_table_entry['Given'][given_num]) > 0:
                    tgt_short_genweb_id = tgt_short_genweb_id + \
                                    tgt_name_table_entry['Given'][given_num][0]
                if debug:
                    print('tgt_short_genweb_id2 = ', tgt_short_genweb_id)

        tgt_short_genweb_id = tgt_short_genweb_id.replace('.', '')
        tgt_short_genweb_id = tgt_short_genweb_id.replace(' ', '') + birth_year

        # create the mother_short_genweb_id
        # PersonID ==	OwnerID ==	FatherID ==	MotherID ==	SpouseID ==	ChildID
        # ParentID ==	FamilyID

        owner_id = tgt_name_table_entry['OwnerID']
        #print("tgt_name_table_entry = ", str(tgt_name_table_entry))
        #print('person_id_person_table[', owner_id, '] = ', person_id_person_table[owner_id])
        parent_id = person_id_person_table[owner_id]['ParentID']

        try:
            family_id_family_table_entry = family_id_family_table[parent_id]
        except:
            long_genwebid = tgt_short_genweb_id + '-'
            revised_tgt_name_table_entry['long_genwebid'] = long_genwebid.replace(' ', '')
            return revised_tgt_name_table_entry

        #print("family_id_family_table_entry = ", str(family_id_family_table_entry))
        mother_id = family_id_family_table_entry['MotherID']

        if mother_id != '0': # test for mother else set mother_short_genweb_id = '-'
            try:
                mother_name_table_entry = ownerid_name_table[mother_id]
            except:
                #print('mother_id = ', mother_id)
                long_genwebid = tgt_short_genweb_id + '-'
                revised_tgt_name_table_entry['long_genwebid'] = long_genwebid.replace(' ', '')
                return revised_tgt_name_table_entry
        else:
            long_genwebid = tgt_short_genweb_id + '-'
            revised_tgt_name_table_entry['long_genwebid'] = long_genwebid.replace(' ', '')
            return revised_tgt_name_table_entry

        if mother_name_table_entry['BirthYear'] == '0':
            birth_year = '0000'
        elif len(mother_name_table_entry['BirthYear']) == 3:
            birth_year = '0' + mother_name_table_entry['BirthYear']
        else:
            birth_year = mother_name_table_entry['BirthYear']

        if len(mother_name_table_entry['Surname']) > 2:
            mother_short_genweb_id = mother_name_table_entry['Surname']
        else:
            long_genwebid = tgt_short_genweb_id + '-'
            revised_tgt_name_table_entry['long_genwebid'] = long_genwebid.replace(' ', '')
            return revised_tgt_name_table_entry

        for given_num in range(len(mother_name_table_entry['Given'])):
            if given_num == 0  and len(mother_name_table_entry['Given'][0]) <= 2:
                long_genwebid = tgt_short_genweb_id + '-'
                revised_tgt_name_table_entry['long_genwebid'] = long_genwebid.replace(' ', '')
                return revised_tgt_name_table_entry
            if given_num == 0:
                mother_short_genweb_id = mother_short_genweb_id + \
                                            mother_name_table_entry['Given'][0]
                if debug:
                    print('mother_short_genweb_id1 = ', mother_short_genweb_id)
            else:
                if debug:
                    print('given_num = ', given_num)
                if len(mother_name_table_entry['Given'][given_num]) > 0:
                    mother_short_genweb_id = mother_short_genweb_id + \
                                mother_name_table_entry['Given'][given_num][0]
                if debug:
                    print('mother_short_genweb_id2 = ', mother_short_genweb_id)

        mother_short_genweb_id = mother_short_genweb_id.replace('.', '')
        mother_short_genweb_id = mother_short_genweb_id.replace(' ', '') + birth_year

        long_genwebid = tgt_short_genweb_id + mother_short_genweb_id

        # this will be used to identify any problems with long_genwebid
        tgt_person_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        if not tgt_person_re.fullmatch(tgt_short_genweb_id):
            print('_get_long_genwebid line 304 - problem with tgt_short_genweb_id = ', \
                    tgt_short_genweb_id, '    long_genwebid = ', long_genwebid)
            return {}
        mother_re = re.compile("[-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        if not mother_re.fullmatch(mother_short_genweb_id):
            print('_get_long_genwebid line 308 - problem with mother_short_genweb_id = ', \
                mother_short_genweb_id, '    long_genwebid = ', long_genwebid)
            return {}

        revised_tgt_name_table_entry['long_genwebid'] = long_genwebid
        return revised_tgt_name_table_entry

#-------------------------------------------------- end of get_long_genwebid

    def _get_family(self, revised_tgt_name_table_entry):
        # Given a person's PersonID (AKA OwnerID) generate the long_genwebid
        # The return is the long_genwebid
        # self._tables keys are:['ChildTable',
        #                        'FamilyTable',
        #                        'NameTable',
        #                        'PersonTable',
        #                        'ownerid_name_table',
        #                        'person_id_person_table',
        #                        'family_id_family_table']
        family_id_family_table = self._tables['family_id_family_table']
        person_id_person_table = self._tables['person_id_person_table']
        ownerid_name_table = self._tables['ownerid_name_table']
        child_table = self._tables['ChildTable']
        name_table = self._tables['NameTable']
        person_table = self._tables['PersonTable']
        family_table = self._tables['FamilyTable']
        """
        where revised_tgt_name_table_entry = { 'OwnerID': ,
                                        'Surname': surname,
                                        'Given': given,
                                        'Prefix': ,
                                        'Suffix': ,
                                        'Nickname': ,
                                        'IsPrimary': ,
                                        'BirthYear': ,
                                        'DeathYear':
                                        'Sex':,
                                        'long_genwebid':
                                      }
        """
        # PersonID ==	OwnerID ==	FatherID ==	MotherID ==	SpouseID ==	ChildID
        # ParentID ==	FamilyID

        # MOTHER
        owner_id = revised_tgt_name_table_entry['OwnerID']
        if owner_id =='':
            debug_mother = True
        parent_id = person_id_person_table[owner_id]['ParentID']
        revised_mother_name_table_entry = {}
        try:
            family_id_family_table_entry = family_id_family_table[parent_id]
            mother_id = family_id_family_table_entry['MotherID']
            mother_name_table_entry = ownerid_name_table[mother_id]
            revised_mother_name_table_entry = \
                                self._get_long_genwebid(mother_name_table_entry)
        except:
            revised_mother_name_table_entry = {}

        # FATHER
        revised_father_name_table_entry = {}
        try:
            father_id = family_id_family_table_entry['FatherID']
            father_name_table_entry = ownerid_name_table[father_id]
            revised_father_name_table_entry = \
                                self._get_long_genwebid(father_name_table_entry)
        except:
            revised_father_name_table_entry = {}

        # SPOUSES
        spouses = rmagic.fetch_spouses_from_ID(name_table, \
                                               person_table, \
                                               family_table, \
                                               owner_id)
        """

        Given a target person's PersonID (OwnerID in name_table)
            1. get the person's Sex from the PersonTable by searching the owner_id
            2. fetch the spouse IDs from the family_table
            3. using the spouse IDs fetch the spouse(s) info from the NameTable
        """
        #print('spouses = ', str(spouses))
        revised_spouses = []
        if spouses != []:
            for spouse in spouses:
                if spouse == {}: continue
                revised_spouse = self._get_long_genwebid(spouse)
                if revised_spouse == {}: continue
                revised_spouses.append(revised_spouse)
                #print('revised_spouse = ', revised_spouse)
        """
        """
        # CHILDREN
        children = rmagic.fetch_children_from_ID(child_table, \
                                            name_table, person_table,\
                                            family_table, owner_id)
        """
        Given a target person's PersonID (OwnerID in name_table)
            1. get the person's Sex from the PersonTable by searching the owner_id
            2. fetch the FamilyID from the family_table
            3. using the FamilyID fetch the ChildID for each child in the
                ChildTable
            4. Using the ChildID as the OwnerID get each child's info from
                NameTable
        """
        #print('children = ', str(children))
        revised_children = []
        if len(children) > 0:
            for child in children:
                revised_child = self._get_long_genwebid(child)
                if revised_child == {}: continue
                revised_children.append(revised_child)
                #print('revised_child = ', str(revised_child))

        family_dict = {}
        family_dict['target'] = revised_tgt_name_table_entry
        family_dict['parents'] = {"father": revised_father_name_table_entry, \
                                  "mother": revised_mother_name_table_entry}
        family_dict['spouses'] = revised_spouses
        family_dict['children'] = revised_children
        #print('family_dict = ', family_dict)
        """
         family_dict =
           'target: name_table_entry for target
           'parents': {'mother: name_table_entry for mother,'father: name_table_entry for father}
           'spouses' : [{name_table_entry for spouse1},...]
           'children' : [{name_table_entry for child1},...]
         where each name_table entry will have the addition key: 'long_genwebid'
         and the appropriate value.
         The key for each target is their long_genwebid
        """
        return family_dict

#-------------------------------------------------- end of _get_family

    def _get_mothers_child(self, target_genwebid, targets_mother, folders_path):

        """
        Given the persons short genwebid (person, e.g. PageRobertK1949) and
        the person's mother's short genwebid (persons_mother, e.g., HughsM1925),
        returns the person_facts for for that mother/child pair.
        (This differentiates two people with the same name and birth year.)
        match person facts =
        {'GenWebID': 'AbdillAliceH1923', 'Nickname': '', 'BirthYear': '1923',
         'IsPrimary': '1', 'Given': ['Alice', 'H'], 'Surname': 'Abdill',
         'Sex': 'female', 'Prefix': '', 'FullName': 'Abdill, Alice H',
         'DeathYear': '0', 'Suffix': '', 'OwnerID': '15390'}
        """
        debug = False
        if target_genwebid == 'CoxSusan1785':
            debug = True
        proper_format = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
        chg_to_long_id_file = open(folders_path + '/zzz_xml_file_name_issue.txt', 'a')
        if not proper_format.match(target_genwebid):
            chg_to_long_id_file = open(folders_path + \
                                        '/zzz_xml_file_name_issue.txt', 'a')
            chg_to_long_id_file.write(\
              '_get_mothers_child line 84- mproper format for target genwebid '\
              + target_genwebid + '\n')
            chg_to_long_id_file.close()
            return ''
        else:
            if target_genwebid == 'CoxSusan1785':
                debug = True
            person_id_dict = self._separate_names(target_genwebid)
            person_matches = rmagic.fetch_person_from_name\
                                (self._tables['NameTable'], \
                                self._tables['PersonTable'], person_id_dict)
            if debug: print('\n _get_mothers_child line 105 - person_matches = '\
                , person_matches, '\n\t  for person_id_dict = ', person_id_dict)
            """
            Given a person's 'Surname', 'Given', 'Initial', 'BirthYear' fetch the NameTable entry
            for that person. If there is more than one match, they will all be returned in a list
            The return is of the form:
                [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
                  'Suffix': '', 'BirthYear': '1949','Prefix': '',
                  'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
                  'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
                  'FullName': 'Page, Robert Kenneth'}]
           	where these rootsmagic tags are equivalent ; OwnerID = person_ID
            """
            null_person = {'Surname':'', 'OwnerID':'', 'Nickname': '', \
                  'Suffix': '', 'BirthYear': '', 'Prefix': '', \
                  'DeathYear': '', 'Sex':'', 'GenWebID':'', \
                  'Given': [''], 'IsPrimary': '', 'FullName': ''}

            if len(person_matches) == 0:
                chg_to_long_id_file = open(folders_path + \
                                            '/zzz_xml_file_name_issue.txt', 'a')
                chg_to_long_id_file.write(\
                        '_get_mothers_child line 123- Could not find', + \
                        ' rmagic match for person with target_genwebid = ' \
                        + target_genwebid + '\n')
                chg_to_long_id_file.close()
                return null_person
            elif len(person_matches) >= 1:
                for match_person in person_matches:
                    if debug:
                        chg_to_long_id_file = open(folders_path + \
                                            '/zzz_xml_file_name_issue.txt', 'a')
                        chg_to_long_id_file.write('line 129 _get_mothers_child',\
                            + ' - Multiple matches for rmagic person. Match = ' \
                            + match_person['GenWebID'] + '\n')
                    parents = rmagic.fetch_parents_from_ID(\
                                            self._tables['PersonTable'],\
                                            self._tables['NameTable'],\
                                            self._tables['FamilyTable'],\
                                            match_person['OwnerID'])
                    if debug:
                        print('\n line 135 _get_mothers_child - parents = ', \
                              parents)
                    mother_id_dict = \
                            self._separate_names(parents['Mother']['GenWebID'])
                    if len(mother_id_dict['Given']) == 0 or \
                       len(mother_id_dict['Surname']) == 0:
                        mothers_genwebid = ''
                    else:
                        mothers_genwebid = parents['Mother']['GenWebID']
                    if mothers_genwebid == targets_mother:
                        chg_to_long_id_file.close()
                        return match_person

        chg_to_long_id_file.write(\
            '_get_mothers_child line 173 - Multiple matches not resolved - \n\ttarget_genwebid = ' \
            + target_genwebid)
        chg_to_long_id_file.write('\n\ttargets_mother = ' + targets_mother + '\n')
        chg_to_long_id_file.write('\n\tmothers_genwebid = ' + mothers_genwebid + '\n')
        chg_to_long_id_file.close()
        return null_person
#--------------------------------------------------_get_mothers_child

    def _get_3g_family(self, targets_long_genwebid, folders_path):

        """
        Given the persons long_genwebid (person, e.g.
        PageRobertK1949HughsMarillynM1921) this returns the 3 generation family
        (person, parents, spouses, and children
        3g_family =
        'tgt_person_facts' =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        'tgt_parents' = {
        	'Father': {'Given': [''], \
                        'IsPrimary': '1', 'DeathYear': '', 'Prefix': '', \
                        'BirthYear': '', 'Nickname': '', 'Suffix': '', 'Surname': '', \
                        'OwnerID': '', 'Sex': '', 'GenWebID': '', 'FullName': ''},\

        	'Mother':{'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', 'Suffix': '', \
                        'Surname': '', 'OwnerID': '', 'Sex': '', 'GenWebID': '', \
                        'FullName': ''}}
        'spouseList' =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        'childList' =
			  [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
				'Suffix': '', 'BirthYear': '1949','Prefix': '',
				'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
				'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
				'FullName': 'Page, Robert Kenneth'}]
        """
        debug = False
        if targets_long_genwebid == '':
            debug = True
        three_gen_family = {}
        # this will be used to separate the genwebid (target_person)
        # into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})' \
                                       + '([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")

        # this will be used to separate the target person's
        # id from the mother's id
        # tgt_person_stuff of the form: ['PersondateMotherdate','Persondate','Motherdate']
        try:
            tgt_person_stuff = people_re.findall(targets_long_genwebid)#[0]
        except:
            print('\n _get_3g_family - line 695 targets_long_genwebid = ', \
                                                            targets_long_genwebid)
            print(" couldn't set tgt_person_stuff = people_re.findall(targets_long_genwebid)[0]")
            three_gen_family['tgt_parents'] = {'Father': {'Given': [''], \
                'IsPrimary': '1', 'DeathYear': '', 'Prefix': '', \
                'BirthYear': '', 'Nickname': '', 'Suffix': '', 'Surname': '', \
                'OwnerID': '', 'Sex': '', 'GenWebID': '', 'FullName': ''},\
                'Mother':{'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                'Prefix': '', 'BirthYear': '', 'Nickname': '', 'Suffix': '', \
                'Surname': '', 'OwnerID': '', 'Sex': '', 'GenWebID': '', \
                'FullName': ''}}
            return three_gen_family

        tgt_person_stuff = people_re.findall(targets_long_genwebid)[0]

        tgt_person = tgt_person_stuff[1]
        tgt_persons_mother = tgt_person_stuff[2]
        if tgt_persons_mother == '-':
            name_dict = self._separate_names(tgt_person)
            try:
                tgt_person_facts = three_gen_family['tgt_person_facts'] = \
                    rmagic.fetch_person_from_name(self._tables['NameTable'], \
                    self._tables['PersonTable'], name_dict)[0]
            except:
                tgt_person_facts = three_gen_family['tgt_person_facts'] = \
                    rmagic.fetch_person_from_name(self._tables['NameTable'], \
                    self._tables['PersonTable'], name_dict)

                print('\n _get_3g_family - line 179 tgt_person_facts = ', \
                    tgt_person_facts, '\n name_dict = ', name_dict)
        else:
            tgt_person_facts = self._get_mothers_child(tgt_person, \
                tgt_persons_mother, folders_path)

            three_gen_family['tgt_person_facts'] = tgt_person_facts

        """
        tgt_person_facts =
        [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
            'Suffix': '', 'BirthYear': '1949','Prefix': '',
            'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
            'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
            'FullName': 'Page, Robert Kenneth'}...]
        """
        if debug:
            print('\n _get_3g_family - line 186 \
                three_gen_family[tgt_person_facts] = ', \
                three_gen_family['tgt_person_facts'])
        #add target person's parents
        #Build targets father - possibilities are that:
        #                    - there is no father's name in the person's entry
        #                                   - father's position empty and no link
        #                    - there is a father's name in the person's entry
        #                                   - father's position (if no record, no name available)
        #                    - there is a record for the father
        #                                   - father's position and link
        #                    - there is not a record for the father
        #                                   - no father's position and no link
        # Calls to rmagic.fetch_parents return:
        #
        #        father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
        #                   'Prefix': '', 'BirthYear': '', 'Nickname': '', \
        #                   'Suffix': '', 'Surname': '', 'OwnerID': '',
        #                   'Sex': '', 'GenWebID': '', 'FullName': ''}
        #
        #       mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
        #                   'Prefix': '', 'BirthYear': '', 'Nickname': '', \
        #                   'Suffix': '', 'Surname': '', 'OwnerID': '',
        #                   'Sex': '', 'GenWebID': '', 'FullName': ''}
        #  where return = {'Father': father, 'Mother': mother}
        try:
            three_gen_family['tgt_parents'] = rmagic.fetch_parents_from_ID(\
                                self._tables['PersonTable'],\
                                self._tables['NameTable'],\
                                self._tables['FamilyTable'],\
                                three_gen_family['tgt_person_facts']['OwnerID'])
        except:
            print('\n _get_3g_family - line 222 \
                three_gen_family[tgt_person_facts] = ',\
                str(three_gen_family['tgt_person_facts']), \
                '\n targets_long_genwebid = ', targets_long_genwebid)

            three_gen_family['tgt_parents'] = {'Father': {'Given': [''], \
                'IsPrimary': '1', 'DeathYear': '', 'Prefix': '', \
                'BirthYear': '', 'Nickname': '', 'Suffix': '', 'Surname': '', \
                'OwnerID': '', 'Sex': '', 'GenWebID': '', 'FullName': ''},\
                'Mother':{'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                'Prefix': '', 'BirthYear': '', 'Nickname': '', 'Suffix': '', \
                'Surname': '', 'OwnerID': '', 'Sex': '', 'GenWebID': '', \
                'FullName': ''}}

        if debug:
            print('\n _get_3g_family - line 225 tgt_parents = ', \
            str(three_gen_family['tgt_parents']))

        tgt_fathers_Owner_ID = \
                    three_gen_family['tgt_parents']['Father']['OwnerID']
        if tgt_fathers_Owner_ID != '':
            three_gen_family['tgt_fathers_parents'] = \
                                                rmagic.fetch_parents_from_ID(\
                                                self._tables['PersonTable'],\
                                                self._tables['NameTable'],\
                                                self._tables['FamilyTable'],\
                                                tgt_fathers_Owner_ID)
            if debug:
                print('\n _get_3g_family - line 234 tgt_fathers_parents = ', \
                str(three_gen_family['tgt_fathers_parents']))

        tgt_mothers_Owner_ID = \
                        three_gen_family['tgt_parents']['Mother']['OwnerID']
        if tgt_mothers_Owner_ID != '':
            three_gen_family['tgt_mothers_parents'] = \
                                                rmagic.fetch_parents_from_ID(\
                                                self._tables['PersonTable'],\
                                                self._tables['NameTable'],\
                                                self._tables['FamilyTable'],\
                                                tgt_mothers_Owner_ID)

            if debug:
                print('\n _get_3g_family - line 243 tgt_mothers_parents = ', \
                str(three_gen_family['tgt_mothers_parents']))

        # I now have the target person's spouse's info
        three_gen_family['spouseList'] = rmagic.fetch_spouses_from_ID(\
                            self._tables['NameTable'],\
                            self._tables['PersonTable'],\
                            self._tables['FamilyTable'],\
                            three_gen_family['tgt_person_facts']['OwnerID'])

        if debug:
            print('\n _get_3g_family - line 262 spouselist = ', \
            str(three_gen_family['spouseList']))

        """
        Given a person's PersonID (AKA OwnerID) fetch the spouse's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form spouse =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['spouseList'] is a list of spouse NameTable entries
        """
        #add children
        three_gen_family['childList'] = rmagic.fetch_children_from_ID(\
                                self._tables['ChildTable'],\
                                self._tables['NameTable'],\
                                self._tables['PersonTable'],\
                                self._tables['FamilyTable'],\
                                three_gen_family['tgt_person_facts']['OwnerID'])

        if debug:
            print('\n _get_3g_family - line 240 childList = ', \
            str(three_gen_family['childList']))

        """
        Given a person's PersonID (AKA OwnerID) fetch the children's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form child =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['childList'] is a list of children NameTable entries
        """

        return three_gen_family
#--------------------------------------------------_get_3g_family

    def _save_dictionary(self, dictionary, file_name):
        with open(file_name, "wb") as myFile:
            pickle.dump(dictionary, myFile)
            myFile.close()

    def _load_dictionary(self, file_name):
        if not os.path.isfile(file_name):
            print('_load_dictionary with file_name= ', file_name, '  not found')
            dict = {'person_info':		[],'artifacts_info': {}}
            return dict
        with open(file_name, "rb") as myFile:
            dictionary = pickle.load(myFile)
            myFile.close()
            return dictionary

#-------------------------------------------------- pickle load and save

    def _get_proj_dict_from_xml(self, folders_path):
        """
        Build a dictionary with each person's genwebid as a key. Each person's
        key will be attached to a dictionary containing zero or more artifacts.
        Each artifact will consist of a key (the artifact_id) of the
        form:
        YYYYMMDD##Last_nameFirst_nameMiddle_initialYYYYLast_nameFirst_nameMiddle_initialYYYY
        where the first date in the id is the date of the artifact (birth, death,
        marriage, etc.) followed by the genwebid of the person whose
        folder has "custody" of the artifact which is followed by the genwebid
        of the persons mother. Associated with that artifact key
        is a dictionary of the artifact description. The artifact description
        has a key indicating the type of artifact ('inline','picture','href')
        and the data elements describing the artifact and it's location: 'path',
        'file','folder','title','caption','comment','people','height','mod_dat'
        """
        os.chdir(folders_path)
        dictionaries_path = folders_path + '/___dictionaries'
        if not os.path.isdir(dictionaries_path): os.makedirs(dictionaries_path)
        # I only want folders that have at least a first and last name with a
        # four digit number for the target person and followed by either a "-"
        # or a first and last name with a four digit number for the mother
        folders = glob.glob("*[0-9][0-9][0-9][0-9]*")

        # this will be used to separate the long_genwebid
        # into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")

        # this will be used to ensure that the artifact xml filename has the proper form
        proper_format = re.compile("[+]*[0-9]{10}[A-Za-z']+[A-Z][a-z]*[0-9]{4}([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4})")
        debug = False
        folder_file_contents = []
        person_dict = {}

        for folder in folders: #step through each folder
            person_info = []
            long_genwebid = folder.strip()
            if folder != long_genwebid:
                print('_get_proj_dict_from_xml folder: ', \
                                    folder, '  has some spaces in its name')
                continue
            if folder == '':
                debug = True
            if long_genwebid == '':
                continue
            if debug:
                print('*** _get_proj_dict_from_xml line 355 - \
                    current folder = ', folder, \
                    '\n\t people_re.findall(folder) = ', \
                    people_re.findall(folder))
            # if there is an error in the following line it is probably
            # caused my either and incomplete xml reference or an incorrect
            # folder name (not a long genwebid)
            # person_stuff of the form:
            #               ['PersondateMotherdate','Persondate','Motherdate']
            person_stuff = people_re.findall(folder)[0]
            if len(person_stuff) == 0 or len(person_stuff[0]) < 3:
                print('\n _get_proj_dict_from_xml line 179 long_genwebid = ', \
                    long_genwebid, '   person_stuff = ', person_stuff)
                #dictionary entry will be of the form:
                #                   'AbdillAliceH1923SmithAgnessF1900':{}
                continue

            # persons_id = person_stuff[0][1] and mothers_id = person_stuff[0][2]
            # Create dictionary entry for long_genwebid
            person_dict = {'person_info': [person_stuff[1], person_stuff[2]], \
                'artifacts_info': {}}

            os.chdir(folders_path + '/' + folder)
            #xml files are artifact description files
            xml_file_names = glob.glob('*.xml')
            # if there are no xml files in this person's folder
            if len(xml_file_names) == 0:
                current_file = dictionaries_path + '/' + long_genwebid + '.pkl'
                self._save_dictionary(person_dict, current_file)
                current_file = dictionaries_path + '/' + long_genwebid + '.dic'
                dictionary_file = open(current_file, 'w')
                dictionary_file.write(str(person_dict))
                dictionary_file.close()
                continue                 # move on to the next folder

            artifacts_dictionary = {}
            for xml_file_name in xml_file_names: #step through the xml files
                if xml_file_name == '':
                    debug = True

                # if  xml file name doesn't match the folder name
                if not long_genwebid in xml_file_name:
                    xml_file_name_issue_file = open(folders_path + \
                                        '/zzz_xml_file_name_issue.txt', 'a')
                    xml_file_name_issue_file.write('*****\
                            _get_proj_dict_from_xml file name line 192 ' \
                            + xml_file_name + ' should Not be in ' \
                            + folder + '\n')
                    xml_file_name_issue_file.close()
                    continue

                xml_id = xml_file_name.rstrip('.xml')
                if not proper_format.match(xml_id):
                    xml_file_name_issue_file = open(folders_path \
                                    + '/zzz_xml_file_name_issue.txt', 'a')
                    xml_file_name_issue_file.write('*****\
                        _get_proj_dict_from_xml file name line 199  ' \
                        + folder + '/' + xml_file_name \
                        + ' does not have the proper data format\n')
                    xml_file_name_issue_file.close()
                    continue

                # create a dictionary of xml file contents
                with open(xml_file_name, 'r') as current_xml_file:
                    file_data = []
                    artifact_dictionary = {}

                    # used to create the dictionary of xml file contents
                    tags = ['<path>', '<file>', '<folder>', '<title>',\
                            '<caption>', '<comment>', '<people>',\
                            '<height>', '<mod_date>']
                    types = ['<inline>', '<picture>', '<href>']
                    tags_types = tags + types
                    #extract all data from the current xml file
                    for line in current_xml_file:
                        line = line.lstrip(' ')
                        line = line.replace('<![CDATA[', '')
                        line = line.replace(']]>', '')
                        line = line.replace('\n', '')
                        line = line.replace('\t', '')
                        lc_line = line.lower()
                        #print(line_str)
                        for tag_type in tags_types:
                            if tag_type in lc_line:
                                if tag_type == '':
                                    debug = True

                                # I found it here, I don't want to look for it
                                # again in this xml file
                                tags_types.remove(tag_type)
                                if debug:
                                    print('\n _get_proj_dict_from_xml line 232 \
                                        tags_types = ', tags_types)
                                if tag_type in types:
                                    artifact_dictionary['tag_type'] = \
                                                            tag_type.strip('<>/')
                                    break
                                elif tag_type in tags:
                                    line = line.replace(tag_type, '')
                                    line = line.replace('</'+ tag_type[1:], '')
                                    if tag_type == '<people>':
                                        people_list = []
                                        people_in_artifact = line.split(';')

                                        # person_in_artifact is a long genwebid
                                        for person_in_artifact in people_in_artifact:
                                            person_in_artifact_stripped = person_in_artifact.strip()
                                            if person_in_artifact_stripped == '': continue
                                            # if person_in_artifact_stripped == long_genwebid: continue
                                            # person's artifact is already in their own dictionary entry
                                            if debug: print('\n line 426: person_in_artifact_stripped = ', person_in_artifact_stripped)
                                            # if person doesn't have a folder(i.e. not already in the dictionary
                                            if person_in_artifact_stripped not in folders:
                                                print('\n _get_proj_dict_from_xml line 430 person_in_artifact_stripped = ', person_in_artifact_stripped, ' folder not found')
                                                person_no_folder = open(folders_path + '/zzz_People with no folder.txt', 'a')
                                                person_no_folder.write('person_in_artifact with no folder = ' + person_in_artifact_stripped + '\n')
                                                person_no_folder.write('check the people field of artifact: ' + xml_file_name + '\n')
                                                person_no_folder.write('long_genwebid = ' + long_genwebid + '\n')
                                                person_no_folder.close()
                                                os.makedirs(folders_path + "/" + person_in_artifact_stripped)
                                                # Create entry
                                                try:
                                                    person_stuff = people_re.findall(person_in_artifact_stripped)[0] # of the form: ['PersondateMotherdate', 'Persondate', 'Motherdate']
                                                    overall_dictionary[person_in_artifact_stripped] = {'person_info': [person_stuff[1], person_stuff[2]]}
                                                except:
                                                    print("\n _get_proj_dict_from_xml line 441 person_in_artifact_stripped = ", person_in_artifact_stripped)
                                                    print('\n _get_proj_dict_from_xml line 442 artifact_dictionary = ', artifact_dictionary)
                                                continue
                                            people_list.append(person_in_artifact_stripped)
                                        artifact_dictionary[tag_type.strip('<>/')] = people_list #final list of people
                                        break
                                    else:
                                        artifact_dictionary[tag_type.strip('<>/')] = line
                                        break
                                    pass
                    if debug:
                        print('\n _get_proj_dict_from_xml line 270 \
                                   artifact_dictionary = ', artifact_dictionary)
                    artifacts_dictionary[xml_id] = artifact_dictionary
            person_dict['artifacts_info'] = artifacts_dictionary

            if debug:
                print('_get_proj_dict_from_xml line 291 \
                      long_genwebid = ', long_genwebid, '\n   \
                       person_dict = ', person_dict)
            current_file = dictionaries_path + '/' + long_genwebid + '.pkl'
            self._save_dictionary(person_dict, current_file)
            current_file = dictionaries_path + '/' + long_genwebid + '.dic'
            dictionary_file = open(current_file, 'w')
            dictionary_file.write(str(person_dict))
            dictionary_file.close()

        # assign all artifacts to all of the appropriate people

        os.chdir(folders_path)
        folders = glob.glob("*[0-9][0-9][0-9][0-9]*")

        debug = False

# step through each persons dictionary entry and copy their artifacts into
# the dictionary for each person appearing in that artifact

        for folder in folders: #step through each folder's dictionary
            person_info = []
            long_genwebid = folder.strip()

            current_file = dictionaries_path + '/' + long_genwebid + '.pkl'
            if os.path.exists(current_file):
                person_dict = self._load_dictionary(current_file)
            else: continue

            # no artifact files for this person
            if person_dict['artifacts_info'] == {}: continue

            if debug:
                print('\n line 306: long_genwebid = ', long_genwebid, '\n')
            if debug:
                print('\n line 307: person_dict = ', person_dict, '\n')
            genwebid_artifacts_dict = person_dict['artifacts_info']
            if debug:
                print('\n line 309: genwebid_artifacts_dict = ', \
                    genwebid_artifacts_dict, '\n')
            genwebid_person_info_dict = person_dict['person_info']
            if debug:
                print('\n line 311: genwebid_person_info_dict = ', \
                    genwebid_person_info_dict, '\n')
            genwebid_artifacts_dict_keys = sorted(genwebid_artifacts_dict.keys())
            if debug:
                print('\n line 313: genwebid_artifacts_dict_keys = ', \
                    genwebid_artifacts_dict_keys, '\n')

            for genwebid_artifact_dict_id in genwebid_artifacts_dict:
                if genwebid_artifact_dict_id == '':
                    debug = True
                else:
                    debug = False
                if debug:
                    print('\n \n _get_proj_dict_from_xml line 319 \
                        genwebid_artifact_dict_id = ', genwebid_artifact_dict_id)
                genwebid_artifact_dict = genwebid_artifacts_dict[genwebid_artifact_dict_id]
                genwebid_artifact_dict_people = genwebid_artifacts_dict[genwebid_artifact_dict_id]['people']
                if debug:
                    print('\n  _get_proj_dict_from_xml line 322 \
                        genwebid_artifact_dict_people = ', \
                        genwebid_artifacts_dict[genwebid_artifact_dict_id]['people'])

                for person_in_artifact in genwebid_artifact_dict_people:
                    # if the person has no artifacts assigned
                    if person_in_artifact == '-':
                        not_found_file = open(folders_path + \
                                                '/zzz_PeopleNotFound.txt', 'a')
                        not_found_file.write('++++++++++++++++ ' + \
                            '_get_proj_dict_from_xml line 318 ++++++++++++\n')
                        not_found_file.write('person_in_artifact = ' + \
                            person_in_artifact + '\n genwedid_artifact_dict = ' \
                                + genwedid_artifact_dict + '\n')
                        not_found_file.write('check the people field of ' + \
                                                genwedid_artifact_dict + '\n')
                        not_found_file.write('long_genwebid = ' + long_genwebid + \
                                            '\n genwedid_artifact_dict = ' + \
                                            genwedid_artifact_dict + '\n')
                        not_found_file.close()
                    else:
                        current_file = dictionaries_path + '/' + person_in_artifact + '.pkl'
                        if os.path.exists(current_file):
                            artifact_person_dict = self._load_dictionary(current_file)
                        #add artifact
                        artifact_person_dict['artifacts_info'][genwebid_artifact_dict_id] \
                               = person_dict['artifacts_info'][genwebid_artifact_dict_id]
                        current_file = dictionaries_path + '/' + person_in_artifact + '.pkl'
                        self._save_dictionary(artifact_person_dict, current_file)
                        current_file = dictionaries_path + '/' + person_in_artifact + '.dic'
                        dictionary_file = open(current_file, 'w')
                        dictionary_file.write(str(artifact_person_dict))
                        dictionary_file.close()

                    debug = False
                    pass

        return

#--------------------------------------------------_get_proj_dict_from_xml

    def _separate_names(self, item):
        """given a string that is a concatenation of names with their first
            letters capitalized [e.g. PageRobertK1949], separate them into
            separate words or characters and the date -
            assumes person IDs contain no spaces and every person's ID has
            a date or 0000
            The results are a dictionary with the following keys
            'BirthYear'
            'Surname'
            'Given'
            'Initial'
            'FullName = person['Surname'] + ', ' + person['Given'] + ' ' + person['Initial']'
            """
        if item == '':
            person = {'BirthYear':'', 'Surname':'', 'Given':'', 'Initial':'', 'FullName':''}
            return person
        # extract the date
        debug = False
        if item == "":
            debug = True
        person = {}
        person['BirthYear'] = item.strip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'")
        item = item.strip('0123456789')

        people_re = re.compile(r"([A-Z][a-z]+)")

        names = people_re.split(item)
        names = [x for x in names if x != '']

        if len(names) < 2 and debug:
            print('\n line 402 _separate_names: item = ', item, '\n  names = ', names, '\n')
            person = {'BirthYear':'', 'Surname':'', 'Given':'', 'Initial':'', 'FullName':''}
            return person

        surname_exceptions = ["O'", 'ap', 'de', 'De', 'le', 'Le', 'Mc', 'Mac', 'Van', 'of', 'St']
        givenname_exceptions = ['De']

        person['Surname'] = ''
        person['Given'] = ''
        person['Initial'] = ''

        if names[0] in surname_exceptions:
            person['Surname'] = names[0] + names[1]
            if names[2] in givenname_exceptions:
                person['Given'] = names[2] + names[3]
                if len(names) == 5: person['Initial'] = names[4]
            else:
                person['Given'] = names[2]
                if len(names) == 4: person['Initial'] = names[3]

        else:
            person['Surname'] = names[0]
            if names[1] in givenname_exceptions:
                person['Given'] = names[1] + names[2]
                if len(names) == 4: person['Initial'] = names[3]
            else:
                person['Given'] = names[1]
                if len(names) == 3: person['Initial'] = names[2]

        person['FullName'] = person['Surname'] + ', ' + person['Given'] + ' ' + person['Initial']

        if item != person['Surname'] + person['Given'] + person['Initial']:
            print('item = ', item, ' person full name = ', person['Given'], ' ', \
                                    person['Initial'], ' ', person['Surname'])
        return person
#-------------------------------------------------- _separate_names


    def _generate_toc_web(self, people_info, folders_path):
        """
        This generates the Table of Contents web pages for the whole website.
        people_info for PageRobertK1949HughsMarillynM1925 =
    {'parents':
    	{
    	 'father': {'long_genwebid': 'PageRaymondH1921StadtfeldLucyS1895', ...},

    	 'mother': {'long_genwebid': 'HughsMarillynM1925CorbettVerneI1892', ...}
    	},

    'children':
    	[{'Sex': 'male', 'FullName': 'Page, Marc Allen', 'IsPrimary': '1', ...},
         ...],

    'target':
    	{
    	 'long_genwebid': 'PageRobertK1949HughsMarillynM1925', ...]
    	},

    'spouses':
    	[{'Sex': 'female', 'FullName': 'Hislop, Mickie Louise', ...}]
    }

        where the keys for an individual are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'long_genwebid'
        """
        #print('_generate_toc_web line 447: people_ids = ', people_ids)
        previous_letter = ''
        table_cell_ct = 0
        table_col = 0
        # this will be used to separate the genwebid (target_person)
        # into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")
        #print('people_ids = ', people_ids)
        for target_person in sorted(people_info.keys()): # This is the long_genwebid
            debug = False
            if target_person == 'StoriesPersonal0000-':
                continue

            person_facts = people_info[target_person]['target']
            #print('person_facts = ', person_facts)
            long_genwebid = person_facts['long_genwebid']

            full_given = ''
            given = ''
            birth_year = ''
            death_year = ''

            surname = person_facts['Surname']
            if surname[0:2] == 'de':
                current_letter = surname[0:2]
                debug = False
            else:
                current_letter = surname[0]


            file_name = folders_path + '/' + current_letter + '.html'

            if current_letter != previous_letter:
                if previous_letter != '':
                    f = open(folders_path + '/' + previous_letter + '.html', 'a')
                    f.write('\t\t\t</tr>\n')
                    f.write('\t\t</table>\n')
                    f.close()
                    table_col = 0

                f = open(file_name, 'w')
                f.write('<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >\n')
                f.write('<html>\n')
                f.write('\t<head>\n')
                f.write('\t\t<title>Family History</title>\n')
                f.write('\t\t<link href="./css/index.css" type="text/css" rel="stylesheet">\n')
                f.write('\t\t<link href="./css/alphas.css" type="text/css" rel="stylesheet">\n')
                f.write('\t\t<base target="right_frame">\n')
                f.write('\t</head>\n')
                f.write('\t<body background="./images/back.gif">\n')
                f.write('\t\t<table align="center" cellpadding="0" cellspacing="0" cols="2" width="75%" frame="border" rules="none">\n')
                f.write('\t\t\t<tr>\n')
                f.write('\t\t\t\t<td align="LEFT">\n')
                f.write('\t\t\t\t\t<img src="./images/HeaderPic.jpg" height="75">\n')
                f.write('\t\t\t\t</td>\n')
                f.write('\t\t\t\t<td align="LEFT">\n')
                f.write('\t\t\t\t\t<h2>Individual and Family Web Pages</h2>\n')
                f.write('\t\t\t\t</td>\n')
                f.write('\t\t\t</tr>\n')
                f.write('\t\t</table>\n')
                f.write('\t\t<table align="center" background="./images/back.gif" border cellpadding="8" cellspacing="4" cols="3">\n')
                f.write('\t\t\t<tr>\n')

                table_col = table_col + 1
                f.write('\t\t\t\t<td align="CENTER" valign="BOTTOM">\n')
                f.write('\t\t\t\t\t<p><a name=' + current_letter + '><font size="+3" weight="900">' + current_letter + '</font></a></p>\n')
                f.write('\t\t\t\t</td>\n')

                table_col = table_col + 1
                f.write('\t\t\t\t<td align="CENTER" valign="BOTTOM">\n')
                full_given = ''
                for given in person_facts['Given']:
                    full_given = full_given + ' ' + given
                f.write('\t\t\t\t\t<h5>' + person_facts['Surname'] + ', ' + full_given + '\n')
                f.write('\t\t\t\t\t\t<a href= "./' + target_person + '/index.html"><img src="./images/individual.bmp"></a>\n')
                f.write('\t\t\t\t\t\t<a href= "./' + target_person + '/HourGlass.html"><img src="./images/family.bmp"></a>\n')
                birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
                death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
                f.write('\t\t\t\t\t\t<br>' + birth_year + ' - ' + death_year + '</h5></p>\n')
                f.write('\t\t\t\t</td>\n')

            if current_letter == previous_letter:
                f = open(file_name, 'a')
                table_col = table_col + 1
                f.write('\t\t\t\t<td align="CENTER" valign="BOTTOM">\n')
                full_given = ''
                if debug: print('_generate_toc_web line 718 person_facts = ', person_facts)

                for given_no in range(len(person_facts['Given'])):
                    given = person_facts['Given'][given_no]
                    full_given = full_given + ' ' + given
                f.write('\t\t\t\t\t<h5>' + person_facts['Surname'] + ', ' + full_given + '\n')
                if debug: print('******* _generate_toc_web line 724 person = ', person)
                f.write('\t\t\t\t\t\t<a href= "./' + target_person + '/index.html"><img src="./images/individual.bmp"></a>\n')
                f.write('\t\t\t\t\t\t<a href= "./' + target_person + '/HourGlass.html"><img src="./images/family.bmp"></a>\n')
                birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
                death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
                f.write('\t\t\t\t\t\t<br>' + birth_year + ' - ' + death_year + '</h5></p>\n')
                f.write('\t\t\t\t</td>\n')

            if table_col == 3:
                f.write('\t\t\t</tr>\n')
                f.write('\t\t\t<tr>\n')
                table_col = 0
            previous_letter = current_letter

            f.close()
        return              # return from _generate_toc_web

#-------------------------------------------------- end of _generate_toc_web

    def _last(self, item): # used in _generate_person_web
        return item[-4:]

#--------------------------------------------------

    def _generate_person_web2(self, family_dict, persons_xml_dict, folders_path):
        """
        This is the new version!

        This will create an artifacts html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database.

         family_dict =
           'target: name_table_entry for target
           'parents': {'mother: name_table_entry for mother, 'father: name_table_entry for father}
           'spouses' : [{name_table_entry for spouse1},...]
           'children' : [{name_table_entry for child1},...]
         where each name_table entry will have the addition key: 'long_genwebid'
         and the appropriate value.
         The key for each target is their long_genwebid

        where the keys for an individual are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'long_genwebid'
            'FullName'

        persons_xml_dict =
            {'person_info':		[persons_id,mothers_id],
             'artifacts_info':
                {artifact_id: {'type':'picture', 'title':'title txt here', ...
                }
                {artifact_id: {'type':'picture', 'title':'title txt here',...
                }
                 ...
            }

        """

        debug = False

        person_facts = family_dict['target']
        """
            where the keys for person_facts are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'long_genwebid':
        """

        long_genwebid = person_facts['long_genwebid']

        if long_genwebid == 'PittsGlenF1958BaileyColleen0000':
            debug = True
            print('\n _generate_person_web line 623: persons_xml_dict = ', persons_xml_dict)

        if long_genwebid == 'StoriesPersonal0000-':
            artifact_ids = sorted(persons_xml_dict['artifacts_info'].keys(), key=self._last)
        else:
            artifact_ids = sorted(persons_xml_dict['artifacts_info'].keys())

        #print('long_genwebid = ', long_genwebid, '----- person_facts = ', person_facts)
        folder_path = folders_path + '/' + long_genwebid
        person_folder_path = folders_path + '/' + long_genwebid
        #print('person_folder_path = ', person_folder_path)

        if not os.path.isdir(person_folder_path):
            print('*****_generate_person_web line 670 ' + person_folder_path + '**** created ****')
            os.makedirs(person_folder_path)


        index_html_file = open(person_folder_path + '/index.html', 'w')
        index_html_file.write('<!DOCTYPE html ')
        index_html_file.write('<html>\n')
        index_html_file.write('\t<head>\n')
        index_html_file.write('\t\t<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />\n')
        index_html_file.write('\t\t<title>Family History</title>\n')
        index_html_file.write('\t\t<script type="text/javascript" src="../scripts/ImagePatch.js"></script>\n')
        index_html_file.write('\t\t<link href="../css/individual.css" type="text/css" rel="stylesheet" />\n')
        index_html_file.write('\t\t<style type="text/css">\n')
        index_html_file.write('\t\t/*<![CDATA[*/\n')
        index_html_file.write('\t\tdiv.ReturnToTop {text-align: right}\n')
        index_html_file.write('\t\t/*]]>*/\n')
        index_html_file.write('\t\t</style>\n')
        index_html_file.write('\t</head>\n')
        index_html_file.write('\t<body background="../images/back.gif" onload="patchUpImages()">\n')

        index_html_file.write('\t\t<script>\n')
        index_html_file.write('\t\tfunction playPauseVideo(identifier) {\n')
        index_html_file.write('\t\t\tvar myVideo = document.getElementById(identifier);\n')
        index_html_file.write('\t\t\tif (myVideo.paused)\n')
        index_html_file.write('\t\t\t\tmyVideo.play();\n')
        index_html_file.write('\t\t\telse\n')
        index_html_file.write('\t\t\t\tmyVideo.pause();\n')
        index_html_file.write('\t\t}\n')
        index_html_file.write('\t\tfunction setWidth(identifier, size) {\n')
        index_html_file.write('\t\t\tvar myVideo = document.getElementById(identifier);\n')
        index_html_file.write('\t\t\tmyVideo.width = size;\n')
        index_html_file.write('\t\t}\n')
        index_html_file.write('\t\t</script>\n')

        if long_genwebid == 'StoriesPersonal0000-':
            index_html_file.write('\t\t<h1><a name="Top"></a>Personal Stories from our Ancestors</h1>\n')
            index_html_file.write('\t\t\t\t<a href= "../../index.html"><img src="../images/Home.jpg"></a>\n')
        else:
            nickname = ''
            if len(person_facts['Nickname']) > 1: nickname = ' "'+ person_facts['Nickname'] + '" '

            birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
            death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
            index_html_file.write('\t\t<h1><a name="Top"></a>' + person_facts["FullName"] \
                        + nickname + ' - ' + birth_year + ' - ' + death_year + '</h1>\n')
            index_html_file.write('\t\t<a href= "HourGlass.html"><img src="../images/family.bmp"></a>\n')

        if persons_xml_dict['artifacts_info'] == {}:
            index_html_file.write('\t</body>\n')
            index_html_file.write('</html>\n')
            index_html_file.close()
            return

        artifacts_info = persons_xml_dict['artifacts_info']
        if debug: print('_generate_person_web line 709 artifacts = ', artifacts_info)

        index_tbl_lines = []
        index_tbl_lines.append('\t\t<!-- Index table -->\n')
        index_tbl_lines.append('\t\t<table align="center" border cellpadding="4" cellspacing="4" cols="3">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')

        artifacts_tbl_lines = []
        artifacts_tbl_lines.append('\t\t<!-- Beginning of Content -->\n')
        artifacts_tbl_lines.append('\t\t<!-- artifacts -->\n')
        artifacts_tbl_lines.append('\t\t<p><em><strong>To identify people in a photograph:</em></strong></p>')
        artifacts_tbl_lines.append('\t\t<ul>')
        artifacts_tbl_lines.append('\t\t<li><span style="font-size: 10pt">Click the smiley face next to the photo (the smiley face will change to a black checkmark).</span></li>')
        artifacts_tbl_lines.append('\t\t<li><span style="font-size: 10pt">Center the cross shaped cursor on the photograph and select the person</span></li>')
        artifacts_tbl_lines.append('\t\t<li style="margin-left:2em;font-size: 10pt">a dialogue box will open requesting the name of the person</li>')
        artifacts_tbl_lines.append('\t\t<li style="margin-left:2em;font-size: 10pt">continue selecting and naming people until you are done</li>')
        artifacts_tbl_lines.append('\t\t<li><span style="font-size: 10pt">Select the checkmark</span></li>')
        artifacts_tbl_lines.append('\t\t<li style="margin-left:2em;font-size: 10pt">your default email program will open with an email ready for you to send. </li>')
        artifacts_tbl_lines.append('\t\t<li><span style="font-size: 10pt">Send the email.</span></li>')
        artifacts_tbl_lines.append('\t\t</ul>')
        debug = False
        index_tbl_col = 1
        for artifact in artifact_ids:
            if debug: print('_generate_person_web line 734 artifact = ', artifact)
            artifact_genwebid = artifact.lstrip('+0123456789') #this is the long genwebid
            artifact_folder_path = folders_path + '/' + artifact_genwebid
            # Generate index table
            if index_tbl_col == 1:
                index_tbl_lines.append('\t\t\t<tr>\n')

            index_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')

            if debug:
                print('***************_generate_person_web line 744: artifact = ', artifact)
                print('artifacts[artifact] = ', artifacts_info[artifact])
                print('sorted(artifacts_info[artifact].keys()) = ', \
                                        sorted(artifacts_info[artifact].keys()))
                print('genwebid = ', genwebid, '   persons_xml_dict = ', persons_xml_dict)
            index_tbl_lines.append('\t\t\t\t\t<p><a href="#' \
              + os.path.basename(persons_xml_dict['artifacts_info'][artifact]['file']) + '">' \
              + persons_xml_dict['artifacts_info'][artifact]['title'] + '</a></p>\n')
            index_tbl_lines.append('\t\t\t\t</td>\n')

            if index_tbl_col == 3:
                index_tbl_lines.append('\t\t\t</tr>\n')

            index_tbl_col = index_tbl_col + 1 if index_tbl_col < 3 else 1


            # Generate artifacts table
            if persons_xml_dict['artifacts_info'][artifact]['tag_type'] == 'picture':
                artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(persons_xml_dict['artifacts_info'][artifact]['file']) + '"/>\n')
                artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="2">\n')
                artifacts_tbl_lines.append('\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<H2>' + persons_xml_dict['artifacts_info'][artifact]['title'] + '</H2>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if not os.path.isfile(artifact_folder_path + '/' + artifact + '.jpg') and long_genwebid in artifact: # if  image doesn't exist, note it to be fixed
                    pic_issue_file = open(folders_path + '/zzz_Artifact_picture_issue.txt', 'a')
                    pic_issue_file.write('*****build_web_pages picture Not Found: artifact = ' + artifact + ' for ' + genwebid + '\n')
                    pic_issue_file.close()
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<img src="../' + artifact_genwebid + '/' + artifact + '.jpg' + '" target="Resource Window">\n')
                if os.path.isfile(artifact_folder_path + '/+' + artifact + '.jpg'): # if a hi res image exists, insert a link to it
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<a href="../' + artifact_genwebid + '/+' + artifact + '.jpg' + '" target="Resource Window">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<img src="../images/zoom.jpg' + '" target="Resource Window">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t</a>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if 'caption' in persons_xml_dict['artifacts_info'][artifact]:
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<p>' + persons_xml_dict['artifacts_info'][artifact]["caption"] + '</p>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
                else:
                    f = open(folders_path + '/zzz_Artifact_xml_issue.txt', 'a')
                    f.write('*****_generate_person_web caption Not Found in persons_xml_dict[artifacts_info][artifact] = ' + persons_xml_dict['artifacts_info'][artifact] + '\n')
                    f.close()
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</table>\n')
                artifacts_tbl_lines.append('\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t</table>\n')
                artifacts_tbl_lines.append('\t\t\n')
                artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')
                artifacts_tbl_lines.append('\t\t\n')

            proper_format = re.compile("[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
            if persons_xml_dict['artifacts_info'][artifact]['tag_type'] == 'inline':
                if debug: print('_generate_person_web line 806: Now processing ' + artifact + '.src')
                if os.path.isfile(artifact_folder_path + '/' + artifact + '.src') and proper_format.match(artifact): # if a src exists, insert it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(persons_xml_dict['artifacts_info'][artifact]['file']) + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<H2  style="text-align:center;margin-left:auto;margin-right:auto;">' + persons_xml_dict['artifacts_info'][artifact]['title'] + '</H2>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')
                    artifacts_tbl_lines.append('\t\t\n')
                    artifact_source = open(artifact_folder_path + '/' + artifact + '.src', 'r')
                    for line in artifact_source:
                        artifacts_tbl_lines.append(line)
                    artifact_source.close()
                    artifacts_tbl_lines.append('\t\t\n')
                    artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')
                    artifacts_tbl_lines.append('\t\t\n')
                else:
                    artifact_issue = open(folders_path + '/zzz_Artifact_xml_issue.txt', 'a')
                    artifact_issue.write('*****build_web_pages line 756: ' + artifact_folder_path + '/' + artifact + '.src file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 767: persons_xml_dict[artifacts_info][artifact][file] = ' + persons_xml_dict['artifacts_info'][artifact]['file'] +'\n')
                    artifact_issue.write('*****build_web_pages line 758: persons_xml_dict[artifacts_info][artifact][title] = ' + artifact +'\n')
                    artifact_issue.close()
                    if not proper_format.match(artifact):
                        src_file_name_issue_file = open(folders_path + '/zzz_src_file_name_issue.txt', 'a')
                        src_file_name_issue_file.write('*****_generate_person_web - inline: file name ' + artifact + '.src' + file_name + ' does not have the proper data format\n')
                        src_file_name_issue_file.close()
                    continue


            if persons_xml_dict['artifacts_info'][artifact]['tag_type'] == 'href':
                if debug: print('_generate_person_web line 834: persons_xml_dict[artifacts_info][' + artifact + '] = ', persons_xml_dict['artifacts_info'][artifact])
                html_path = artifact_folder_path + '/' + persons_xml_dict['artifacts_info'][artifact]['folder'] + '/' + persons_xml_dict['artifacts_info'][artifact]['file']
                if debug: print('_generate_person_web line 836: Now processing href = ', html_path)
                if os.path.isfile(artifact_folder_path + '/' + persons_xml_dict['artifacts_info'][artifact]['folder'] + '/' + persons_xml_dict['artifacts_info'][artifact]['file']): # if an html exists, reference it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + persons_xml_dict['artifacts_info'][artifact]['file'] + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t<H2>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t\t<a href="../' + artifact_genwebid + '/' + persons_xml_dict['artifacts_info'][artifact]['folder'] + '/' + persons_xml_dict['artifacts_info'][artifact]['file'] + '" target="_blank"><H2>' + persons_xml_dict['artifacts_info'][artifact]['title'] + '</H2></a>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t</td>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t</tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t</table>\n')
                    artifacts_tbl_lines.append('\t\t\t\t</td>\n')
                    artifacts_tbl_lines.append('\t\t\t</tr>\n')
                    artifacts_tbl_lines.append('\t\t</table>\n')
                    artifacts_tbl_lines.append('\t\t\n')
                    artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')
                    artifacts_tbl_lines.append('\t\t\n')
                else:
                    artifact_issue = open(folders_path + '/zzz_Artifact_xml_issue.txt', 'a')
                    artifact_issue.write('*****build_web_pages line 793: href file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 794:' + artifact_folder_path + '/' + persons_xml_dict['artifacts_info'][artifact]['folder'] + '/' + persons_xml_dict['artifacts_info'][artifact]['file'] +'\n')
                    artifact_issue.close()
                    pass

            pass



        index_tbl_lines.append('\t\t</table>\n')
        for line in index_tbl_lines:
            index_html_file.write(line)

        artifacts_tbl_lines.append('\t</body>\n')
        artifacts_tbl_lines.append('</html>\n')

        for line in artifacts_tbl_lines:
            index_html_file.write(line)
        index_html_file.close()
        pass

        return      # return from _generate_person_web
#-------------------------------------------------- end of _generate_person_web



    def _generate_all_hourglass_webs(self, family_dict, folders_path):
        """
        This is the new one! changing from person to family_dict

         family_dict =
           'target: name_table_entry for target
           'parents':
             {'mother: name_table_entry for mother,
              'father: name_table_entry for father}
           'spouses' : [{name_table_entry for spouse1},...]
           'children' : [{name_table_entry for child1},...]
         where each name_table entry will also have key: 'long_genwebid'
         and the appropriate value.
         The key for each target is their long_genwebid

        where the keys for an individual are:
            'OwnerID'
            'Surname'
            'Given' (a list of the given names)
            'Prefix'
            'Suffix'
            'Nickname'
            'IsPrimary'
            'BirthYear'
            'DeathYear'
            'FullName'

        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID']
        """
        debug = False
        long_genwebid = family_dict['target']['long_genwebid']

        if long_genwebid == '':
            debug = True

        if debug == True: print('line 2599 family_dict = ', family_dict)

        if long_genwebid == '' or long_genwebid == 'StoriesPersonal0000-':
            return
        short_genwebid_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        person_facts = family_dict['target']

        if 'GenWebID' in family_dict['parents']['mother']:
            persons_mother = family_dict['parents']['mother']['GenWebID']
        else:
            persons_mother = '-'

        if persons_mother == '':
            persons_mother = '-'

        hourglass_table = {}

        # Row 1
        hourglass_table['c1r1'] = \
        '    <td align="center "><h2>Parents</h2></td><!--c1r1-->\n'
        hourglass_table['c2r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c2r1-->\n'
        hourglass_table['c3r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c3r1-->\n'
        hourglass_table['c4r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c4r1-->\n'
        hourglass_table['c5r1'] = \
        '    <td align="center "><h2>Person &amp; Spouse</h2></td><!--c5r1-->\n'
        hourglass_table['c6r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c6r1-->\n'
        hourglass_table['c7r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c7r1-->\n'
        hourglass_table['c8r1'] = \
        '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c8r1-->\n'
        hourglass_table['c9r1'] = \
        '    <td align="center "><h2>Children</h2></td><!--c9r1-->\n'

        for row in range(1, 21): #insert start of rows <tr> and end of rows </tr>
            key = 'c0r' + str(row)
            hourglass_table[key] = '  <tr><!--' + key + '-->\n'
            key = 'c10r' + str(row)
            hourglass_table[key] = '  </tr><!--' + key + '-->\n'
        # pre-fill the table with blank info (empty table elements) -
        # these will be the default entries and will be replaced by people,
        # if they exist.
        for column in range(1, 10):
            for row in range(2, 21):
                key = 'c' + str(column) + 'r' + str(row)
                hourglass_table[key] = \
                '    <td align="center "></td><!--' + key + '-->\n'

        if 'GenWebID' not in person_facts: # if person doesn't exist, return
            f = open(folders_path + '/zzz_PeopleNotFound.txt', 'a')
            f.write('*****build_web_pages hourglass table row #1 ****** long_genwebid = \
                        ' + long_genwebid + '\n')
            f.close()
            return
        else:
            # c5r4 target person picture
            if os.path.isfile(folders_path + '/' + long_genwebid \
                                + '/' +  long_genwebid + '.jpg'):
                hourglass_table['c5r4'] = \
                '    <td align="center "><img src="../' + long_genwebid + '/' \
                    + long_genwebid + '.jpg" height="75"></td><!--c5r4-->\n'
            else:
                hourglass_table['c5r4'] = \
                '    <td align="center "><img src="../images/silhouette.jpg" \
                    height="75"></td><!--c5r4-->\n'

            # c5r5 target person name and link
            hourglass_table['c5r5'] = \
            '    <td align="center "><a href=index.html><p>' + \
                person_facts["FullName"] + '</p></a></td><!--c5r5-->\n'

        #add parents (family_dict['parents'])
        #            Build father - possibilities are that:
        #                    - there is no father's name in the person's entry
        #                       - father's position empty and no link
        #                    - there is a father's name in the person's entry
        #                       - father's position (if no record, no name available)
        #                    - there is a record for the father
        #                       - father's position and link
        #                    - there is not a record for the father
        #                       - no father's position and no link
        #Need to do three things here
        # - if I have the person's name, use it
        # - if there is a person_id for the person, use it
        # - if neither, don't use maroon

        # preload the silhouette in case tgt parents have no photo
        hourglass_table['c1r2'] = \
        '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'
        hourglass_table['c1r3'] = \
        '    <td align="center "><p>unknown</p></a></td><!--c1r3-->\n'
        hourglass_table['c2r3'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c2r3-->\n'
        hourglass_table['c3r3'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r3-->\n'
        hourglass_table['c3r4'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r4-->\n'
        hourglass_table['c3r5'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'
        hourglass_table['c4r5'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'
        hourglass_table['c1r6'] = \
        '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'
        hourglass_table['c1r7'] = \
        '    <td align="center "><p>unknown</p></a></td><!--c1r7-->\n'
        hourglass_table['c2r7'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c2r7-->\n'
        hourglass_table['c3r7'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r7-->\n'
        hourglass_table['c3r6'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r6-->\n'
        hourglass_table['c3r5'] = \
        '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

        debug = False
        if long_genwebid == '':
            debug = True
        if person_facts['OwnerID'] == '':
            debug = True

        if debug:
            print('_generate_all_hourglass_webs line 1185 - long_genwebid = ', long_genwebid)
            print('********* person_facts = ', person_facts)
            print('********* family_dict[parents] = ', \
                                family_dict['parents'])
            print('********* len(family_dict[parents]) = ', \
                                len(family_dict['parents']))
#Father
        if 'OwnerID' in family_dict['parents']['father']:
            tgt_fathers_Owner_ID = family_dict['parents']['father']['OwnerID']
            tgt_fathers_parents = rmagic.fetch_parents_from_ID(\
                                                self._tables['PersonTable'],\
                                                self._tables['NameTable'],\
                                                self._tables['FamilyTable'],\
                                                tgt_fathers_Owner_ID)
        else:
            fathers_mother_genwebid = '-'
            father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                        'Suffix': '', 'Surname': '', 'OwnerID': '',
                        'Sex': '', 'GenWebID': '', 'FullName': ''}
            mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                        'Suffix': '', 'Surname': '', 'OwnerID': '',
                        'Sex': '', 'GenWebID': '', 'FullName': ''}
            tgt_fathers_parents = {'Father': father, 'Mother': mother}
        """

        father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}
        mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}

        tgt_fathers_parents = {'Father': father, 'Mother': mother}
        """
        if debug:
            print('_generate_all_hourglass_webs line 2789 - long_genwebid = ', long_genwebid)
            print('********* tgt_fathers_parents = ', tgt_fathers_parents)

        fathers_mother_genwebid = '-'
        if 'GenWebID' not in family_dict['parents']['father'] == '':
            fathers_mother_genwebid = '-'
        elif tgt_fathers_parents['Father']['GenWebID'] != '':
            fathers_mother_genwebid = \
                tgt_fathers_parents['Mother']['GenWebID']

        # handle the case where the fathers_mother_genwebid name is incomplete
        if fathers_mother_genwebid == '' or \
            (not short_genwebid_re.match(fathers_mother_genwebid)):
            fathers_mother_genwebid = '-'

        if 'GenWebID' in family_dict['parents']['father']:  # father exists
            # c1r2 father picture
            if os.path.isfile(folders_path + '/' + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid \
                                + '/' + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid + '.jpg'):
                hourglass_table['c1r2'] = '    <td align="center "><img src="../' \
                                        + family_dict['parents']['father']["GenWebID"] \
                                        + fathers_mother_genwebid + '/' \
                                        + family_dict['parents']['father']["GenWebID"] \
                                        + fathers_mother_genwebid \
                                        + '.jpg" height="75"></td><!--c1r2-->\n'
            else:
                if debug: print(folders_path + '/' + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid \
                                + '/' + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid + '.jpg')
                hourglass_table['c1r2'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'


            # c1r3 target person name and link
            # was: if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Father']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(folders_path + "/" + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid + "/index.html"):
                hourglass_table['c1r3'] = '    <td align="center "><a href=../' \
                        + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid + '/index.html><p>' \
                        + family_dict['parents']['father']['FullName'] + '</p></a></td><!--c1r3-->\n'
            else:
                hourglass_table['c1r3'] = '    <td align="center "><p>' \
                        + family_dict['parents']['father']['FullName'] + '</p></td><!--c1r3-->\n'

            # c2r3 add arrow to select father as new target
            if os.path.isdir(folders_path + "/" + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid):
                hourglass_table['c2r3'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                        + family_dict['parents']['father']['GenWebID'] \
                                + fathers_mother_genwebid \
                                        + '/HourGlass.html><img src=../images/Left_Arrow.gif></a></td><!--c2r3-->\n'
            else:
                hourglass_table['c2r3'] = '    <td align="center " bgcolor="maroon "></td><!--c2r3-->\n'

            # c3r3 add maroon cell
            hourglass_table['c3r3'] = '    <td align="center " bgcolor="maroon "></td><!--c3r3-->\n'

            # c3r4 add maroon cell
            hourglass_table['c3r4'] = '    <td align="center " bgcolor="maroon "></td><!--c3r4-->\n'

            # c3r5 add maroon cell
            hourglass_table['c3r5'] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

            # c4r5 add maroon cell
            hourglass_table['c4r5'] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'

        else:
            pass # don't add any content if father doesn't exist

        if debug:
            print('_generate_all_hourglass_webs line 1255 - long_genwebid= ', long_genwebid)
            print('********* family_dict[parents] = ', family_dict['parents'])
            print('********* len(family_dict[parents]) = ', len(family_dict['parents']))
            print('********* three_gen_family = ', family_dict)
# Mother
        if 'OwnerID' in family_dict['parents']['mother']:
            tgt_mothers_Owner_ID = family_dict['parents']['mother']['OwnerID']
            tgt_mothers_parents = rmagic.fetch_parents_from_ID(\
                                    self._tables['PersonTable'],\
                                    self._tables['NameTable'],\
                                    self._tables['FamilyTable'],\
                                    tgt_mothers_Owner_ID)
        else:
            mothers_mother_genwebid = '-'
            father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                        'Suffix': '', 'Surname': '', 'OwnerID': '',
                        'Sex': '', 'GenWebID': '', 'FullName': ''}
            mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                        'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                        'Suffix': '', 'Surname': '', 'OwnerID': '',
                        'Sex': '', 'GenWebID': '', 'FullName': ''}
            tgt_fathers_parents = {'Father': father, 'Mother': mother}
        """

        father = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}
        mother = {'Given': [''], 'IsPrimary': '1', 'DeathYear': '', \
                    'Prefix': '', 'BirthYear': '', 'Nickname': '', \
                    'Suffix': '', 'Surname': '', 'OwnerID': '',
                    'Sex': '', 'GenWebID': '', 'FullName': ''}

        tgt_fathers_parents = {'Father': father, 'Mother': mother}
        """

        mothers_mother_genwebid = '-'
        if 'GenWebID' not in family_dict['parents']['mother']:
            mothers_mother_genwebid = '-'
        elif 'GenWebID' in tgt_mothers_parents['Mother']:
            mothers_mother_genwebid = tgt_mothers_parents['Mother']['GenWebID']

        # handle the case where the mothers_mother_genwebid name is incomplete
        if mothers_mother_genwebid == '' or (not short_genwebid_re.match(mothers_mother_genwebid)): mothers_mother_genwebid = '-'

        if 'GenWebID' in family_dict['parents']['mother']:  # mother exists
            # c1r6 target person picture
            if os.path.isfile(folders_path + '/' + family_dict['parents']['mother']['GenWebID'] \
                                + mothers_mother_genwebid \
                                + '/' + family_dict['parents']['mother']['GenWebID'] + mothers_mother_genwebid + '.jpg'):
                hourglass_table['c1r6'] = '    <td align="center "><img src="../' \
                                        + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid + '/' \
                                        + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid\
                                        + '.jpg" height="75"></td><!--c1r6-->\n'
            else:
                hourglass_table['c1r6'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'

            # c1r7 target person name and link
            #if os.path.isdir(folders_path + "/" + family_dict['parents']'Mother']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(folders_path + "/" + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid + "/index.html"):
                hourglass_table['c1r7'] = '    <td align="center "><a href=../' \
                        + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid + '/index.html><p>' \
                        + family_dict['parents']['mother']['FullName'] + '</p></a></td><!--c1r7-->\n'
            else:
                hourglass_table['c1r7'] = '    <td align="center "><p>' \
                        + family_dict['parents']['mother']['FullName'] + '</p></td><!--c1r7-->\n'

            if debug:
                print('line 1284 - hourglass_table[c1r7] = ', hourglass_table['c1r7'])

            # c2r7 add arrow to select mother as new target
            if os.path.isdir(folders_path + "/" + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid):
                hourglass_table['c2r7'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                        + family_dict['parents']['mother']["GenWebID"] + mothers_mother_genwebid \
                                        + '/HourGlass.html><img src=../images/Left_Arrow.gif></a></td><!--c2r7-->\n'
            else:
                hourglass_table['c2r7'] = '    <td align="center " bgcolor="maroon "></td><!--c2r7-->\n'

            # c3r7 add maroon cell
            hourglass_table['c3r7'] = '    <td align="center " bgcolor="maroon "></td><!--c3r7-->\n'

            # c3r6 add maroon cell
            hourglass_table['c3r6'] = '    <td align="center " bgcolor="maroon "></td><!--c3r6-->\n'

            # c3r5 add maroon cell
            hourglass_table['c3r5'] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'

            # c4r5 add maroon cell
            hourglass_table['c4r5'] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'

        else:
            pass # don't add any content if mother doesn't exist

# Spouses
        """
        Given a person's PersonID (AKA OwnerID), the NameTable entry for that
        person.
        The form of spouse =
            [{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949', 'Prefix': '',
              'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        spouses is a list of spouse NameTable entries
        """
        spouseList = family_dict['spouses']

        row = 6
        debug = False
        if long_genwebid == '':
            debug = True
        if debug:
            print('********* spouseList = ', spouseList)
            print('********* len(spouseList) = ', len(spouseList))
        for spouse_num in range(len(spouseList)):
            if debug:
                print('********* spouse_num = ', spouse_num)
            if spouseList[spouse_num] == {}: continue
            if not short_genwebid_re.match(spouseList[spouse_num]['GenWebID']):
                continue
            spouse = spouseList[spouse_num]
            if spouse == {}:
                continue

            if debug: print('_generate_all_hourglass_webs line 1345 - spouse_num = ', spouse_num, '       spouse = ', spouse)

            spouses_parents = rmagic.fetch_parents_from_ID(\
                                        self._tables['PersonTable'],\
                                        self._tables['NameTable'],\
                                        self._tables['FamilyTable'],\
                                        spouse['OwnerID'])
            spouses_mothers_genwebid = spouses_parents['Mother']['GenWebID']
            # handle the case where the spouse's mother's name is incomplete
            if spouses_mothers_genwebid == '' or (not short_genwebid_re.match(spouses_mothers_genwebid)): spouses_mothers_genwebid = '-'

            if debug: print('_generate_all_hourglass_webs line 1356 - spouses_mothers_genwebid = ', spouses_mothers_genwebid)

            # c5r6,8,10,12 target person picture
            if len(spouseList[spouse_num]) > 0:
                key = 'c5r' + str(row)
                if debug:
                    print(folders_path + '/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid +'/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid + '.jpg')
                if os.path.isfile(folders_path + '/' + spouseList[spouse_num]['GenWebID']  + spouses_mothers_genwebid \
                                    + '/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid + '.jpg'):
                    hourglass_table[key] = '    <td align="center "><img src="../' \
                                            + spouseList[spouse_num]["GenWebID"] + spouses_mothers_genwebid + '/' \
                                            + spouseList[spouse_num]["GenWebID"] \
                                            + spouses_mothers_genwebid + '.jpg" height="75"></td><!--' + key + '-->\n'
                    if debug:
                        print('hourglass_table[' + key + '] = ', hourglass_table[key])
                else:
                    hourglass_table[key] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--' + key + '-->\n'

                row = row + 1
                # c5r7,9,11,13 target person name and link
                key = 'c5r' + str(row)
                hourglass_table[key] = '    <td align="center "><a href="../' \
                        + spouseList[spouse_num]["GenWebID"]  + spouses_mothers_genwebid + '/index.html"><p>' \
                        + spouseList[spouse_num]["FullName"] + '</p></a></td><!--' + key + '-->\n'

                # c4r7,9,11,13 add arrow to select spouse as new target
                key = 'c4r' + str(row)
                hourglass_table[key] = '    <td align="center"><a href= ../' \
                                        + spouseList[spouse_num]["GenWebID"] + spouses_mothers_genwebid \
                                        + '/HourGlass.html><img src=../images/Right_Arrow_Maroon.gif></a></td><!--' + key + '-->\n'
                if debug:
                    print('hourglass_table[' + key + '] = ', hourglass_table[key])
                row = row + 1

# children
        childList = family_dict['children']
        """
        Given a person's PersonID (AKA OwnerID) fetch the children's NameTable
        entries for that person.
        The fetch_person_from_ID return is of the form child =
            [{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949', 'Prefix': '',
              'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        three_gen_family['childList'] is a list of children NameTable entries
        """

        row = 2
        debug = False
        if long_genwebid == '-':
            debug = True
        if debug:
            print('********* childList = ', childList)
            print('********* len(childList) = ', len(childList))
        for child_num in range(len(childList)):
            if debug:
                print('********* child_num = ', child_num)
            if childList[child_num] == {}:
                continue
            if not short_genwebid_re.match(childList[child_num]['GenWebID']):
                continue

            child = childList[child_num]

            if debug: print('_generate_all_hourglass_webs line 1437 - child_num = ', child_num, '       child = ', child)

            if child == {}:
                continue

            childs_long_genwebid = child['long_genwebid']

            # c9r2, 4, 6, 8, ... 20 target person picture
            if len(childList[child_num]) > 0:
                key = 'c9r' + str(row)
                if debug:
                    print(folders_path + '/' + childs_long_genwebid + '/' + childs_long_genwebid + '.jpg')
                if os.path.isfile(folders_path + '/' + childs_long_genwebid \
                                    + '/' + childs_long_genwebid + '.jpg'):
                    hourglass_table[key] = '    <td align="center "><img src="../' \
                                            + childs_long_genwebid + '/' \
                                            + childs_long_genwebid \
                                            + '.jpg" height="75"></td><!--' + key + '-->\n'
                    if debug:
                        print('hourglass_table[' + key + '] = ', hourglass_table[key])
                else:
                    hourglass_table[key] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--' + key + '-->\n'

                # c7r4, 6, 8, ... 20 add maroon cell
                hourglass_table['c7r4'] = '    <td align="center " bgcolor="maroon "></td><!--c7r4-->\n'
                if row > 2:
                    key = 'c7r' + str(row)
                    hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c7r4, 6, 8, ... 20-->\n'

                row = row + 1
                # c9r3, 5, 7, ... 19 target person name and link
                key = 'c9r' + str(row)
                hourglass_table[key] = '    <td align="center "><a href="../' \
                        + childs_long_genwebid + '/index.html"><p>' \
                        + childList[child_num]["FullName"] + '</p></a></td><!--' + key + '-->\n'

                # c6r3 is always blank
                key = 'c6r3'
                hourglass_table[key] = '    <td align="center"></td><!--c6r3-->\n'

                # c7r3, 5, 7, ... 19 add maroon cell
                key = 'c7r' + str(row)
                hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c7r3, 5, 7, ... 19-->\n'

                # c6r5 add maroon cell
                key = 'c6r5'
                hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c6r5-->\n'
                # c7r5 add maroon cell
                key = 'c7r5'
                hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c7r5-->\n'

                # c8r4, 6, 8, ... 20 add arrow to select child as new target
                key = 'c8r' + str(row)
                hourglass_table[key] = '    <td align="center" bgcolor="maroon"><a href= ../' \
                                        + childs_long_genwebid \
                                        + '/HourGlass.html><img src=../images/Right_Arrow.gif></a></td><!--' + key + '-->\n'
                if debug:
                    print('hourglass_table[' + key + '] = ', hourglass_table[key])
                row = row + 1

        #Build the web page
        #This builds the standard html header I use for the family history files
        #print('person = ', person, '  OwnerID = ', person_facts['OwnerID'])
        #print('person_facts = ', person_facts)
        hourglasshtmlList = []
        hourglasshtmlList.append("<html>\n")
        hourglasshtmlList.append("<head>\n")
        hourglasshtmlList.append('    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />' + "\n")

        #given_names = ''  -------------- not used - delete
        #for names in person_facts['Given']:
        #    given_names = given_names + ' ' + names

        hourglasshtmlList.append('    <title>' + person_facts['FullName'] + '</title>' + "\n")
        hourglasshtmlList.append('    <link href="../css/individual.css" type="text/css" rel="stylesheet" />' + "\n")
        hourglasshtmlList.append('    <style type="text/css">' "\n")
        hourglasshtmlList.append('    /*<![CDATA[*/' + "\n")
        hourglasshtmlList.append(' div.ReturnToTop {text-align: right}' + "\n")
        hourglasshtmlList.append('    /*]]>*/' + "\n")
        hourglasshtmlList.append("    </style>\n")
        hourglasshtmlList.append("</head>\n")
        hourglasshtmlList.append('<body background="../images/back.gif">' + "\n")
        nickname = ''
        if len(person_facts['Nickname']) > 1: nickname = ' "'+ person_facts['Nickname'] + '" '
        buildString = '    <h1><a name="Top"></a>' + person_facts['FullName'] + nickname
        if debug:
            print('\n line 943 _generate_all_hourglass_webs:  person_facts[BirthYear] = ', \
              person_facts["BirthYear"], '     type(person_facts["BirthYear"]) = ', \
              type(person_facts["BirthYear"]))
        if person_facts['BirthYear'] == '': person_facts['BirthYear'] = '????' #if not birth year then pass

        buildString = buildString + ' - ' + person_facts['BirthYear']

        if debug: print('\n line 949 _generate_all_hourglass_webs: person_facts[DeathYear] = ',\
                        person_facts["DeathYear"], \
                        '     type(person_facts["DeathYear"]) = ', \
                        type(person_facts["DeathYear"]))

        if person_facts['DeathYear'] == '0':
            pass
        else:
            buildString = buildString + ' - ' + person_facts['DeathYear']

        buildString = buildString + "</h1>\n"
        hourglasshtmlList.append(buildString)

        if persons_mother == '': persons_mother = '-'
        commentString = '\t\t\t<p><a href="mailto:pagerk@gmail.com?subject=' + long_genwebid + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: left; margin-right: auto" height="20"></a>\n'
        hourglasshtmlList.append(commentString)

        hourglasshtmlList.append('<table border="0" cellspacing="0" cellpadding="0" align="center">\n')
        #add the table to the HourGlass
        for row in range(1, 21):
            for column in range(0, 11):
                key = 'c' + str(column) + 'r' + str(row)
                hourglasshtmlList.append(hourglass_table[key])

        hourglasshtmlList.append('</table>')
        hourglasshtmlList.append('</body>')
        hourglasshtmlList.append('</html>')

        if os.path.isdir(folders_path + '/' + long_genwebid):
            hourglassFile = open(folders_path + '/' + long_genwebid + '/HourGlass.html', 'w')

            for row in hourglasshtmlList:
                hourglassFile.writelines(row)

            hourglassFile.close()
        else:

            folder_not_found = open(folders_path + '/zzz_FolderNotFound.txt', 'a')
            folder_not_found.write('***** _generate_all_hourglass_webs ****** folder = ' + long_genwebid + '\n')
            folder_not_found.write('person_facts[FullName] = ' + person_facts['FullName'] \
                              + '\n person_facts[BirthYear] = ' + person_facts['BirthYear'] \
                              + '\n person_facts[DeathYear] = ' + person_facts['DeathYear'] + '\n')
            folder_not_found.close()
            #[{'Surname': 'Page', 'OwnerID': '1', 'Nickname': 'Bob',
            #  'Suffix': '', 'BirthYear': '1949', 'Prefix': '',
            #  'DeathYear': '0', 'Sex':'male, 'GenWebID':'PageRobertK1949',
            #  'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
            #  'FullName': 'Page, Robert Kenneth'}]
        	# where these rootsmagic tags are equivalent ; OwnerID = person_ID)

        return              # end of _generate_all_hourglass_webs

#--------------------------------------------------

def main():
    # Get the RootsMagic database info
    #rmagicPath = 'C:\\Users\\pager\\PyScripter_Workspace\\genweb\\myfamily.rmgc'
    rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    build_web = build_web_pages(rmagicPath)
    build_web.__init__(rmagicPath)


if __name__ == '__main__':
    main()
