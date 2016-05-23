#!/usr/bin/env python3

import os
import datetime
import time
import string
import winsound
import glob
import re
import pickle
from . import rmagic

import sys
#sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts/MyLib')

class build_web_pages(object):

    def __init__(self, rmagicPath):

        if sys.platform == "win32":
            timer = time.clock
        else:
            timer = time.time
        t0 = t1 = 0
        t0 = timer()

        os.chdir('C:/Users/pager/PyScripter_Workspace/genweb')
        paths = open('genweb_paths.txt', 'r')
        folders_path =  paths.readline()
        #rmagicPath = paths.readline()
        paths.close()


        self._rmagicPath = rmagicPath
        # _tables keys are: ['ChildTable', 'FamilyTable', 'NameTable', 'PersonTable']
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)
        self._matched_persons = []

        debug = False
        generate_Table_of_Contents = True
        generate_hourglass = True
        refresh_get_proj_dict_from_xml = True
        generate_web_pages = True

        folders_path = 'C:/Family_History/FamilyHistoryWeb/Individual_Web_Pages'
        os.chdir(folders_path)
        dictionaries_path = folders_path + '/___dictionaries'
        if refresh_get_proj_dict_from_xml == True:
            self._get_proj_dict_from_xml(folders_path)

        people_ids = glob.glob("*[0-9][0-9][0-9][0-9]*")

        #generating toc web pages
        if generate_Table_of_Contents:
            self._generate_toc_web(people_ids,folders_path)

        people_re = \
            re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")

        person_dict = {}
        for person in people_ids:# person is long_genwebid
            #if not("AdsitWilliamS1925" in person): continue

            # person_stuff of the form:
            #       ['PersondateMotherdate','Persondate','Motherdate']

            if person != person.strip():
                print('_init_ folder: ', folder, ' has some spaces in its name')
                continue

            person_stuff = people_re.findall(person)[0]
            if len(person_stuff) >= 3:
                file = dictionaries_path + '/' + person + '.pkl'
                person_dict = self._load_dictionary(file)
                """
                person_dict =
                    {'person_info':		[persons_id,mothers_id],
                     'artifacts_info':
                                        {artifact_id: {'type':'picture','title':'title txt here', ...
    				                    }
                                        {artifact_id: {'type':'picture','title':'title txt here',...
                                        }
    			                         ...
                    }
                """
                if debug == True:
                    print('__init__ **** person_dict = ', person_dict)

                if generate_web_pages:
                    self._generate_person_web(person, person_dict, folders_path)

                if generate_hourglass:  # this must come after generate_web_pages - don't want hourglass if no web page
                    self._generate_all_hourglass_webs(person, folders_path)

        t1 = timer()
        print('execution time =' , int((t1 - t0)//60), ' minutes, ',  int((t1 - t0)%60), ' seconds or ', (t1 - t0), ' seconds total')
        winsound.Beep(500,1000)
        winsound.Beep(500,1000)
#--------------------------------------------------__init__

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
        chg_to_long_id_file = open(folders_path + '/zzz_xml_file_name_issue.txt','a')
        if not proper_format.match(target_genwebid):
            chg_to_long_id_file = open(folders_path + \
                                        '/zzz_xml_file_name_issue.txt','a')
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
            null_person = {'Surname':'','OwnerID':'','Nickname': '',\
                  'Suffix': '', 'BirthYear': '','Prefix': '',\
                  'DeathYear': '', 'Sex':'','GenWebID':'',\
                  'Given': [''], 'IsPrimary': '', 'FullName': ''}

            if len(person_matches) == 0:
                chg_to_long_id_file = open(folders_path + \
                                            '/zzz_xml_file_name_issue.txt','a')
                chg_to_long_id_file.write(\
                  '_get_mothers_child line 123- Could not find rmagic match for person with target_genwebid = ' \
                        + target_genwebid + '\n')
                chg_to_long_id_file.close()
                return null_person
            elif len(person_matches) >= 1:
                for match_person in person_matches:
                    if debug:
                        chg_to_long_id_file = open(folders_path + \
                                            '/zzz_xml_file_name_issue.txt','a')
                        chg_to_long_id_file.write('line 129 _get_mothers_child - Multiple matches for rmagic person. Match = ' \
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
                    if len(mother_id_dict['Given'])  == 0 or \
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
        Given the persons short long_genwebid (person, e.g.
        PageRobertK1949HughsMarillynM1921) this returns the 3 generation family
        (person, parents, spouses, and children
        3g_family =
        !!! I need to decide the form of the return   {}
        """
        debug = False
        if targets_long_genwebid == '':
            debug = True
        three_gen_family = {}
        # this will be used to separate the genwebid (target_person)
        # into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")

        # this will be used to separate the target person's
        # id from the mother's id
        # tgt_person_stuff of the form: ['PersondateMotherdate','Persondate','Motherdate']
        tgt_person_stuff = people_re.findall(targets_long_genwebid)[0]
        if debug: print('\n _get_3g_family - line 168 tgt_person_stuff = ', \
                                                            tgt_person_stuff)
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

    def _save_dictionary(self, dictionary, file):
        with open(file, "wb") as myFile:
            pickle.dump(dictionary, myFile)
            myFile.close()

    def _load_dictionary(self, file):
        #print('_load_dictionary with file = ', file)
        with open(file, "rb") as myFile:
            dict = pickle.load(myFile)
            myFile.close()
            return dict

#-------------------------------------------------- pickle load and save

    def _get_proj_dict_from_xml(self,folders_path):
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
            person_dict = {'person_info': [person_stuff[1],person_stuff[2]], \
                'artifacts_info': {}}

            os.chdir(folders_path + '/' + folder)
            #xml files are artifact description files
            xml_file_names = glob.glob('*.xml')
            # if there are no xml files in this person's folder
            if len(xml_file_names)  == 0:
                file = dictionaries_path + '/' + long_genwebid + '.pkl'
                self._save_dictionary(person_dict, file)
                file = dictionaries_path + '/' + long_genwebid + '.dic'
                dictionary_file = open(file,'w')
                dictionary_file.write(str(person_dict))
                dictionary_file.close()
                continue                 # move on to the next folder

            artifacts_dictionary = {}
            for xml_file_name in xml_file_names: #step through the xml files
                if xml_file_name == '':
                    debug = True

                # if  xml file name doesn't match the folder name
                if not (long_genwebid in xml_file_name):
                    xml_file_name_issue_file = open(folders_path + \
                                        '/zzz_xml_file_name_issue.txt','a')
                    xml_file_name_issue_file.write('*****\
                            _get_proj_dict_from_xml file name line 192 ' \
                            + xml_file_name + ' should Not be in ' \
                            + folder + '\n')
                    xml_file_name_issue_file.close()
                    continue

                xml_id = xml_file_name.rstrip('.xml')
                if not proper_format.match(xml_id):
                    xml_file_name_issue_file = open(folders_path \
                                    + '/zzz_xml_file_name_issue.txt','a')
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
                    tags = ['<path>','<file>','<folder>','<title>',\
                            '<caption>','<comment>','<people>',\
                            '<height>','<mod_date>']
                    types = ['<inline>','<picture>','<href>']
                    tags_types = tags + types
                    #extract all data from the current xml file
                    for line in current_xml_file:
                        line = line.lstrip(' ')
                        line = line.replace('<![CDATA[','')
                        line = line.replace(']]>','')
                        line = line.replace('\n','')
                        line = line.replace('\t','')
                        lc_line = line.lower()
                        #print(line_str)
                        for type in tags_types:
                            if type in lc_line:
                                if type == '':
                                    debug = True

                                # I found it here, I don't want to look for it
                                # again in this xml file
                                tags_types.remove(type)
                                if debug:
                                    print('\n _get_proj_dict_from_xml line 232 \
                                        tags_types = ', tags_types)
                                if type in types:
                                    artifact_dictionary['type'] = \
                                                            type.strip('<>/')
                                    break
                                elif type in tags:
                                    line = line.replace(type,'')
                                    line = line.replace('</'+ type[1:],'')
                                    if type == '<people>':
                                        people_list = []
                                        people_in_artifact = line.split(';')

                                        # person_in_artifact is a long genwebid
                                        for person_in_artifact in people_in_artifact:
                                            person_in_artifact_stripped = person_in_artifact.strip()
                                            if person_in_artifact_stripped == '': continue
                                            #if person_in_artifact_stripped == long_genwebid: continue # person's artifact is already in their own dictionary entry
                                            if debug: print('\n line 426: person_in_artifact_stripped = ', person_in_artifact_stripped)
                                            # if person doesn't have a folder(i.e. not already in the dictionary
                                            if person_in_artifact_stripped not in folders:
                                                print('\n _get_proj_dict_from_xml line 430 person_in_artifact_stripped = ', person_in_artifact_stripped, ' folder not found')
                                                person_no_folder = open(folders_path + '/zzz_People with no folder.txt','a')
                                                person_no_folder.write('person_in_artifact with no folder = ' + person_in_artifact_stripped + '\n')
                                                person_no_folder.write('check the people field of artifact: ' + xml_file_name + '\n')
                                                person_no_folder.write('long_genwebid = ' + long_genwebid + '\n')
                                                person_no_folder.close()
                                                os.makedirs(folders_path + "/" + person_in_artifact_stripped)
                                                # Create entry
                                                try:
                                                    person_stuff = people_re.findall(person_in_artifact_stripped)[0] # of the form: ['PersondateMotherdate','Persondate','Motherdate']
                                                    overall_dictionary[person_in_artifact_stripped] = {'person_info': [person_stuff[1],person_stuff[2]]}
                                                except:
                                                    print("\n _get_proj_dict_from_xml line 441 person_in_artifact_stripped = ", person_in_artifact_stripped)
                                                    print('\n _get_proj_dict_from_xml line 442 artifact_dictionary = ', artifact_dictionary)
                                                continue
                                            people_list.append(person_in_artifact_stripped)
                                        artifact_dictionary[type.strip('<>/')] = people_list #final list of people
                                        break
                                    else:
                                        artifact_dictionary[type.strip('<>/')] = line
                                        break
                                    pass
                    if debug: print('\n _get_proj_dict_from_xml line 270 \
                        artifact_dictionary = ', artifact_dictionary)
                    artifacts_dictionary[xml_id] = artifact_dictionary
            person_dict['artifacts_info'] = artifacts_dictionary

            if debug: print('_get_proj_dict_from_xml line 291 \
                long_genwebid = ', long_genwebid, '\n   \
                person_dict = ', person_dict)
            file = dictionaries_path + '/' + long_genwebid + '.pkl'
            self._save_dictionary(person_dict, file)
            file = dictionaries_path + '/' + long_genwebid + '.dic'
            dictionary_file = open(file,'w')
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

            file = dictionaries_path + '/' + long_genwebid + '.pkl'
            if os.path.exists(file):
                person_dict = self._load_dictionary(file)
            else: continue

            # no artifact files for this person
            if person_dict['artifacts_info'] == {}: continue

            if debug == True:
                print('\n line 306: long_genwebid = ', long_genwebid, '\n')
            if debug == True:
                print('\n line 307: person_dict = ', person_dict, '\n')
            genwebid_artifacts_dict = person_dict['artifacts_info']
            if debug == True:
                print('\n line 309: genwebid_artifacts_dict = ', \
                    genwebid_artifacts_dict, '\n')
            genwebid_person_info_dict = person_dict['person_info']
            if debug == True:
                print('\n line 311: genwebid_person_info_dict = ', \
                    genwebid_person_info_dict, '\n')
            genwebid_artifacts_dict_keys = sorted(genwebid_artifacts_dict.keys())
            if debug == True:
                print('\n line 313: genwebid_artifacts_dict_keys = ', \
                    genwebid_artifacts_dict_keys, '\n')

            for genwebid_artifact_dict_id in genwebid_artifacts_dict:
                if genwebid_artifact_dict_id == '':
                    debug = True
                else: debug = False
                if debug == True:
                    print('\n \n _get_proj_dict_from_xml line 319 \
                        genwebid_artifact_dict_id = ', genwebid_artifact_dict_id)
                genwebid_artifact_dict = genwebid_artifacts_dict[genwebid_artifact_dict_id]
                genwebid_artifact_dict_people = genwebid_artifacts_dict[genwebid_artifact_dict_id]['people']
                if debug == True:
                    print('\n  _get_proj_dict_from_xml line 322 \
                        genwebid_artifact_dict_people = ', \
                        genwebid_artifacts_dict[genwebid_artifact_dict_id]['people'])

                for person_in_artifact in genwebid_artifact_dict_people:
                    # if the person has no artifacts assigned
                    if person_in_artifact == '-':
                        not_found_file = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                        not_found_file.write('++++++++++++++++ _get_proj_dict_from_xml line 318 ++++++++++++\n')
                        not_found_file.write('person_in_artifact = ' + person_in_artifact + '\n genwedid_artifact_dict = ' + genwedid_artifact_dict + '\n')
                        not_found_file.write('check the people field of ' + genwedid_artifact_dict + '\n')
                        not_found_file.write('long_genwebid = ' + long_genwebid + '\n genwedid_artifact_dict = ' + genwedid_artifact_dict + '\n')
                        not_found_file.close()
                    else:
                        file = dictionaries_path + '/' + person_in_artifact + '.pkl'
                        if os.path.exists(file):
                            artifact_person_dict = self._load_dictionary(file)
                        #add artifact
                        artifact_person_dict['artifacts_info'][genwebid_artifact_dict_id] = person_dict['artifacts_info'][genwebid_artifact_dict_id]
                        file = dictionaries_path + '/' + person_in_artifact + '.pkl'
                        self._save_dictionary(artifact_person_dict, file)
                        file = dictionaries_path + '/' + person_in_artifact + '.dic'
                        dictionary_file = open(file,'w')
                        dictionary_file.write(str(artifact_person_dict))
                        dictionary_file.close()

                    debug = False
                    pass

        return

#--------------------------------------------------_get_proj_dict_from_xml

    def _separate_names(self,item):
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
        if item =='':
            person = {'BirthYear':'','Surname':'','Given':'','Initial':'','FullName':''}
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

        if len(names) <2 and debug:
            print('\n line 402 _separate_names: item = ', item, '\n  names = ', names, '\n')
            person = {'BirthYear':'','Surname':'','Given':'','Initial':'','FullName':''}
            return person

        surname_exceptions = ["O'",'ap','de','De','le','Le','Mc','Mac','Van','of', 'St']
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

        if item != person['Surname'] + person['Given'] + person['Initial'] :
            print('item = ', item, ' person full name = ', person['Given'], ' ', person['Initial'], ' ', person['Surname'])
        return person
#-------------------------------------------------- _separate_names
    def _generate_toc_web(self,people_ids,folders_path):
        """
        This generates the Table of Contents web pages for the whole website.
        The people_ids are of the form: LastnameFirstnameM0000LastnameFirstnameM0000
        where the first ID is the target person and the 2nd ID is that person's mother
        If there is no birthyear, it is set to 0000. If there is no known mother,
        that ID is replaced with a "-"
        """
        #print('_generate_toc_web line 447: people_ids = ', people_ids)
        previous_letter = ''
        table_cell_ct = 0
        table_col = 0
        # this will be used to separate the genwebid (target_person) into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")
        #print('people_ids = ', people_ids)
        for target_person in people_ids: # This is the long_genwebid
            debug = False
            if target_person =='':
                debug = True
            if target_person =='StoriesPersonal0000-':
                continue

            # this will be used to ensure that the artifact xml filename is has the proper form
            person_stuff = people_re.findall(target_person)[0] # of the form: ['PersondateMotherdate','Persondate','Motherdate']
            if debug: print('line 619 person_stuff = ', person_stuff)
            person = person_stuff[1]
            persons_mother = person_stuff[2]
            if persons_mother == '': continue # there is no folder for this person
            if persons_mother == '-': persons_mother = ''

            if person =='':
                debug = True
            full_given = ''
            given = ''
            birth_year = ''
            death_year = ''
            persons_mother_id_dict = {'BirthYear':'','Surname':'','Given':'','Initial':''}

            person_id_dict = self._separate_names(person)
            if len(persons_mother) > 6: persons_mother_id_dict = self._separate_names(persons_mother)

            if person[0:2] == 'de':
                current_letter = person[0:2]
                debug = False
            else:
                current_letter = person[0]
            file_name = folders_path + '/' + current_letter + '.html'
            person_facts = self._get_mothers_child(person, persons_mother, folders_path)
            """
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
                'Suffix': '', 'BirthYear': '1949','Prefix': '',
                'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
                'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
                'FullName': 'Page, Robert Kenneth'}...]
            """
            if debug == True:
                print('line 651 _generate_toc_web - person = ', person)
                print('line 652 ----- person_facts = ', person_facts)
            if person_facts == {'Surname':'','OwnerID':'','Nickname': '',\
                                'Suffix': '', 'BirthYear': '','Prefix': '',\
                                'DeathYear': '', 'Sex':'','GenWebID':'',\
                                'Given': [''], 'IsPrimary': '', 'FullName': ''}:
                not_found_file = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                not_found_file.write('*****build_web_pages line 670 ****** person = ' + person + '  persons_mother = ' + persons_mother + '\n')
                not_found_file.close()
                continue

            if str(type(person_facts)) == "<class 'list'>": person_facts = person_facts[0]

            if current_letter != previous_letter:
                if previous_letter != '':
                    f = open(folders_path + '/' + previous_letter + '.html','a')
                    f.write('\t\t\t</tr>\n')
                    f.write('\t\t</table>\n')
                    f.close()
                    table_col = 0

                f = open(file_name,'w')
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
                f = open(file_name,'a')
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

            if table_col ==3:
                f.write('\t\t\t</tr>\n')
                f.write('\t\t\t<tr>\n')
                table_col = 0
            previous_letter = current_letter

            f.close()
        return              # return from _generate_toc_web

#--------------------------------------------------

    def _last(self,item): # used in _generate_person_web
        return item[-4:]

#--------------------------------------------------
    def _generate_person_web(self, genwebid, person_dict, folders_path):

        """
        This will create an artifacts html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID'], e.g. 'IngramJamieL1971SpackmanJeannine1947'
        These two short genwebids are derived the the long genwebid
        (e.g. 'IngramJamieL1971SpackmanJeannine1947')that is passed.

        person_dict =
        {'person_info':		[persons_id,mothers_id],
         'artifacts_info':
                            {artifact_id: {'type':'picture','title':'title txt here', ...
		                    }
                            {artifact_id: {'type':'picture','title':'title txt here',...
                            }
	                         ...
        }
        """

        debug = False

        # this will be used to separate the genwebid (target_person) into the persons_id and the mothers_id
        people_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")

        # this will be used to separate the persons id from the mothers id
        person_stuff = people_re.findall(genwebid)[0] # of the form: [('PersondateMotherdate','Persondate','Motherdate')] (e.g. [('AbdillAliceH1923SmithAgnessF1900', 'AbdillAliceH1923', 'SmithAgnessF1900')])

        if debug: print('line 608 _generate_person_web - person_stuff = ', person_stuff)
        person = person_stuff[1] #their short genwebid (e.g. AbdillAliceH1923)

        if person == '': # person is short genwebid
            debug = True

        if debug: print('\n _generate_person_web line 623: person_dict = ', person_dict)

        person_id_dict = self._separate_names(person)
        """person_id_dict is a dictionary with the following keys
            'BirthYear'
            'Surname'
            'Given'
            'Initial'
            'FullName = person['Surname'] + ', ' + person['Given'] + ' ' + person['Initial']'
        """
        persons_mother = person_stuff[2]
        if persons_mother == '-':
            persons_mother = ''
            person_facts = rmagic.fetch_person_from_name\
                                (self._tables['NameTable'], \
                                 self._tables['PersonTable'], person_id_dict)[0]
            """
            the return is of the form:
                [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
                  'Suffix': '', 'BirthYear': '1949','Prefix': '',
                  'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
                  'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
                  'FullName': 'Page, Robert Kenneth'}]
          """
        else:
            person_facts = self._get_mothers_child(person, persons_mother, folders_path)
            """
            Given the persons short genwebid (person, e.g. PageRobertK1949) and
            the person's mother's short genwebid (persons_mother, e.g., HughsM1925),
            returns the person_facts for for that mother/child pair.
            (This differentiates two people with the same name and birth year.)
            person_facts =
            {'GenWebID': 'AbdillAliceH1923', 'Nickname': '', 'BirthYear': '1923',
             'IsPrimary': '1', 'Given': ['Alice', 'H'], 'Surname': 'Abdill',
             'Sex': 'female', 'Prefix': '', 'FullName': 'Abdill, Alice H',
             'DeathYear': '0', 'Suffix': '', 'OwnerID': '15390'}
            """
        if debug == True:
            print('line 641 _generate_person_web - person = ', person)
            print('line 642 _generate_person_web - person_facts = ', person_facts)

        if person == 'StoriesPersonal0000':
            artifact_ids = sorted(person_dict['artifacts_info'].keys(), key = self._last)
        else:
            artifact_ids = sorted(person_dict['artifacts_info'].keys())
            if debug:
                print('line 651 _generate_person_web - artifact_ids = ', artifact_ids)
                print('line 652 _generate_person_web - person_dict[artifacts_info] = ', person_dict['artifacts_info'])


        if person_dict['artifacts_info'] == {}:
            people_excluded_file = open(folders_path + '/zzz_PeopleExcluded.txt','a')
            people_excluded_file.write('\n No artifacts found: In _generate_person_web, genwebid = ' + genwebid \
                    + '  was not found in the rootsmagic datbase. It was searched for with the following information person_id_dict[Surname] = ' + person_id_dict['Surname'] \
                    + '  person_id_dict[Given] = ' + person_id_dict['Given'] + '  person_id_dict[Initial] = ' + person_id_dict['Initial'] \
                    + '  person_id_dict[BirthYear] = ' + person_id_dict['BirthYear'] + '\n')
            people_excluded_file.close()
            return

        #print('genwebid = ', genwebid, '----- person_facts = ', person_facts)
        folder_path = folders_path + '/' + genwebid
        person_folder_path = folders_path + '/' + genwebid
        #print('person_folder_path = ', person_folder_path)

        if not os.path.isdir(person_folder_path):
            print('*****_generate_person_web line 670 ' + person_folder_path + '**** created ****')
            os.makedirs(person_folder_path)


        index_html_file = open(person_folder_path + '/index.html','w')
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

        if person == 'StoriesPersonal0000':
            index_html_file.write('\t\t<h1><a name="Top"></a>Personal Stories from our Ancestors</h1>\n')
            index_html_file.write('\t\t\t\t<a href= "../../index.html"><img src="../images/Home.jpg"></a>\n')
        else:

            nickname = ''
            if len(person_facts['Nickname']) > 1: nickname = ' "'+ person_facts['Nickname'] + '" '

            birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
            death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
            index_html_file.write('\t\t<h1><a name="Top"></a>' + person_facts["FullName"] + nickname + ' - ' + birth_year + ' - ' + death_year + '</h1>\n')
            index_html_file.write('\t\t<a href= "HourGlass.html"><img src="../images/family.bmp"></a>\n')

        if person_dict['artifacts_info'] == {}:
            index_html_file.write('\t</body>\n')
            index_html_file.write('</html>\n')
            index_html_file.close()
            return

        artifacts_info = person_dict['artifacts_info']
        if debug == True: print('_generate_person_web line 709 artifacts = ', artifacts_info)

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
            if debug == True: print('_generate_person_web line 734 artifact = ', artifact)
            artifact_genwebid = artifact.lstrip('+0123456789') #this is the long genwebid
            artifact_folder_path = folders_path + '/' + artifact_genwebid
            # Generate index table
            if index_tbl_col == 1:
                index_tbl_lines.append('\t\t\t<tr>\n')

            index_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')

            if debug == True:
                print('***************_generate_person_web line 744: artifact = ', artifact)
                print('artifacts[artifact] = ', artifacts_info[artifact])
                print('sorted(artifacts_info[artifact].keys()) = ', sorted(artifacts_info[artifact].keys()))
                print('genwebid = ', genwebid, '   person_dict = ', person_dict)
            index_tbl_lines.append('\t\t\t\t\t<p><a href="#' + os.path.basename(person_dict['artifacts_info'][artifact]['file']) + '">' + person_dict['artifacts_info'][artifact]['title'] + '</a></p>\n')
            index_tbl_lines.append('\t\t\t\t</td>\n')

            if index_tbl_col == 3:
                index_tbl_lines.append('\t\t\t</tr>\n')

            index_tbl_col = index_tbl_col + 1 if index_tbl_col < 3 else 1


            # Generate artifacts table
            if person_dict['artifacts_info'][artifact]['type'] == 'picture':
                artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(person_dict['artifacts_info'][artifact]['file']) + '"/>\n')
                artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="2">\n')
                artifacts_tbl_lines.append('\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<H2>' + person_dict['artifacts_info'][artifact]['title'] + '</H2>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if not os.path.isfile(artifact_folder_path + '/' + artifact + '.jpg') and genwebid in artifact: # if  image doesn't exist, note it to be fixed
                    pic_issue_file = open(folders_path + '/zzz_Artifact_picture_issue.txt','a')
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
                if 'caption' in person_dict['artifacts_info'][artifact]:
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<p>' + person_dict['artifacts_info'][artifact]["caption"] + '</p>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
                else:
                    f = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    f.write('*****_generate_person_web caption Not Found in person_dict[artifacts_info][artifact] = ' + person_dict['artifacts_info'][artifact] + '\n')
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
            if person_dict['artifacts_info'][artifact]['type'] == 'inline':
                if debug: print('_generate_person_web line 806: Now processing ' + artifact + '.src')
                if os.path.isfile(artifact_folder_path + '/' + artifact + '.src') and proper_format.match(artifact): # if a src exists, insert it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(person_dict['artifacts_info'][artifact]['file']) + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<H2  style="text-align:center;margin-left:auto;margin-right:auto;">' + person_dict['artifacts_info'][artifact]['title'] + '</H2>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
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
                    artifact_issue = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    artifact_issue.write('*****build_web_pages line 756: ' + artifact_folder_path + '/' + artifact + '.src file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 767: person_dict[artifacts_info][artifact][file] = ' + person_dict['artifacts_info'][artifact]['file'] +'\n')
                    artifact_issue.write('*****build_web_pages line 758: person_dict[artifacts_info][artifact][title] = ' + artifact +'\n')
                    artifact_issue.close()
                    if not proper_format.match(artifact):
                        src_file_name_issue_file = open(folders_path + '/zzz_src_file_name_issue.txt','a')
                        src_file_name_issue_file.write('*****_generate_person_web - inline: file name ' + artifact + '.src' + file_name + ' does not have the proper data format\n')
                        src_file_name_issue_file.close()
                    continue
                    if debug: print('*****build_web_pages line 830:' + artifact_folder_path + '/' + artifact + '.src file Not Found')


            if person_dict['artifacts_info'][artifact]['type'] == 'href':
                if debug: print('_generate_person_web line 834: person_dict[artifacts_info][' + artifact + '] = ', person_dict['artifacts_info'][artifact])
                html_path = artifact_folder_path + '/' + person_dict['artifacts_info'][artifact]['folder'] + '/' + person_dict['artifacts_info'][artifact]['file']
                if debug: print('_generate_person_web line 836: Now processing href = ',html_path)
                if os.path.isfile(artifact_folder_path + '/' + person_dict['artifacts_info'][artifact]['folder'] + '/' + person_dict['artifacts_info'][artifact]['file']): # if an html exists, reference it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + person_dict['artifacts_info'][artifact]['file'] + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t<H2>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t\t<a href="../' + artifact_genwebid + '/' + person_dict['artifacts_info'][artifact]['folder'] + '/' + person_dict['artifacts_info'][artifact]['file'] + '" target="_blank"><H2>' + person_dict['artifacts_info'][artifact]['title'] + '</H2></a>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
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
                    artifact_issue = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    artifact_issue.write('*****build_web_pages line 793: href file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 794:' + artifact_folder_path + '/' + person_dict['artifacts_info'][artifact]['folder'] + '/' + person_dict['artifacts_info'][artifact]['file'] +'\n')
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

#--------------------------------------------------
    def _generate_all_hourglass_webs(self, person, folders_path):
        """
        person is the long_genwebid (PersondateMotherdate)
        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID']
        """
        debug = False
        if person == '':
            debug = True
        if person == 'StoriesPersonal0000-':
            return
        short_genwebid_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9]{4}")
        long_genwebid_re = re.compile("(([A-Za-z']+[A-Z][a-z]*[0-9]{4})([-]|[A-Za-z']+[A-Z][a-z]*[0-9]{4}))")
        three_gen_family = self._get_3g_family(person, folders_path)
        person_facts = three_gen_family['tgt_person_facts']
        if not(person_facts['GenWebID'] in person):
            print('*********  Error in _generate_all_hourglass_webs line 1181 person = ', person)
            print('\t\t person_facts = ', str(person_facts))
            return
        long_genwebid = person
        person = person_facts['GenWebID'] # this is the short genwebid
        if three_gen_family['tgt_parents']['Mother']['GenWebID'] != '':
            persons_mother = three_gen_family['tgt_parents']['Mother']['GenWebID']
        else:
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

        for row in range(1,21): #insert start of rows <tr> and end of rows </tr>
            key = 'c0r' + str(row)
            hourglass_table[key] = '  <tr><!--' + key + '-->\n'
            key = 'c10r' + str(row)
            hourglass_table[key] = '  </tr><!--' + key + '-->\n'
        # pre-fill the table with blank info (empty table elements) -
        # these will be the default entries and will be replaced by people,
        # if they exist.
        for column in range(1,10):
            for row in range(2,21):
                key = 'c' + str(column) + 'r' + str(row)
                hourglass_table[key] = \
                '    <td align="center "></td><!--' + key + '-->\n'

        if len(person_facts['GenWebID']) == 0: # if person doesn't exist, return
            f = open(folders_path + '/zzz_PeopleNotFound.txt','a')
            f.write('*****build_web_pages hourglass table row #1 ****** long_genwebid = \
                        ' + long_genwebid + '\n')
            f.close()
            return
        else:
            # c5r4 target person picture
            if os.path.isfile(folders_path + '/' + person + persons_mother \
                                + '/' +  person + persons_mother + '.jpg'):
                hourglass_table['c5r4'] = \
                '    <td align="center "><img src="../' + person + persons_mother + '/' \
                    + person + persons_mother + '.jpg" height="75"></td><!--c5r4-->\n'
            else:
                hourglass_table['c5r4'] = \
                '    <td align="center "><img src="../images/silhouette.jpg" \
                    height="75"></td><!--c5r4-->\n'

            # c5r5 target person name and link
            hourglass_table['c5r5'] = \
            '    <td align="center "><a href=index.html><p>' + \
                person_facts["FullName"] + '</p></a></td><!--c5r5-->\n'

        #add parents (three_gen_family['tgt_parents'])
                    #Build father - possibilities are that:
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

        # sorted(three_gen_family.keys()) = \
        #   ['childList', 'spouseList', 'tgt_fathers_parents', \
        #   'tgt_mothers_parents', 'tgt_parents', 'tgt_person_facts']

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
        if person_facts['OwnerID'] == '':
            debug = True

        if debug == True:
            print('_generate_all_hourglass_webs line 1185 - person = ', person)
            print('********* three_gen_family[tgt_parents] = ', \
                                three_gen_family['tgt_parents'])
            print('********* len(three_gen_family[tgt_parents]) = ', \
                                len(three_gen_family['tgt_parents']))
            print('********* three_gen_family = ', three_gen_family)

        fathers_mother_genwebid = '-'
        if three_gen_family['tgt_parents']['Father']['GenWebID'] == '':
            fathers_mother_genwebid = '-'
        elif three_gen_family['tgt_fathers_parents']['Father']['GenWebID'] != '':
            fathers_mother_genwebid = \
                three_gen_family['tgt_fathers_parents']['Mother']['GenWebID']

        # handle the case where the fathers_mother_genwebid name is incomplete
        if fathers_mother_genwebid == '' or \
            (not short_genwebid_re.match(fathers_mother_genwebid)):
            fathers_mother_genwebid = '-'

        if three_gen_family['tgt_parents']['Father']['FullName'] != '':  # father exists
            # c1r2 father picture
            if os.path.isfile(folders_path + '/' + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid \
                                + '/' + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid + '.jpg'):
                hourglass_table['c1r2'] = '    <td align="center "><img src="../' \
                                        + three_gen_family['tgt_parents']['Father']["GenWebID"] \
                                        + fathers_mother_genwebid + '/' \
                                        + three_gen_family['tgt_parents']['Father']["GenWebID"] \
                                        + fathers_mother_genwebid \
                                        + '.jpg" height="75"></td><!--c1r2-->\n'
            else:
                if debug: print(folders_path + '/' + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid \
                                + '/' + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid + '.jpg')
                hourglass_table['c1r2'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'


            # c1r3 target person name and link
            # was: if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Father']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(folders_path + "/" + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid + "/index.html"):
                hourglass_table['c1r3'] = '    <td align="center "><a href=../' \
                        + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid + '/index.html><p>' \
                        + three_gen_family['tgt_parents']['Father']['FullName'] + '</p></a></td><!--c1r3-->\n'
            else:
                hourglass_table['c1r3'] = '    <td align="center "><p>' \
                        + three_gen_family['tgt_parents']['Father']['FullName'] + '</p></td><!--c1r3-->\n'

            # c2r3 add arrow to select father as new target
            if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Father']['GenWebID'] \
                                + fathers_mother_genwebid):
                hourglass_table['c2r3'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                        + three_gen_family['tgt_parents']['Father']['GenWebID'] \
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

        if debug == True:
            print('_generate_all_hourglass_webs line 1255 - person = ', person)
            print('********* three_gen_family[tgt_parents] = ', three_gen_family['tgt_parents'])
            print('********* len(three_gen_family[tgt_parents]) = ', len(three_gen_family['tgt_parents']))
            print('********* three_gen_family = ', three_gen_family)

        mothers_mother_genwebid = '-'
        if three_gen_family['tgt_parents']['Mother']['GenWebID'] == '':
            mothers_mother_genwebid = '-'
        elif three_gen_family['tgt_mothers_parents']['Mother']['GenWebID'] != '':
            mothers_mother_genwebid = three_gen_family['tgt_mothers_parents']['Mother']['GenWebID']

        # handle the case where the mothers_mother_genwebid name is incomplete
        if mothers_mother_genwebid == '' or (not short_genwebid_re.match(mothers_mother_genwebid)): mothers_mother_genwebid = '-'

        if three_gen_family['tgt_parents']['Mother']['FullName'] != '':  # mother exists
            # c1r6 target person picture
            if os.path.isfile(folders_path + '/' + three_gen_family['tgt_parents']['Mother']['GenWebID'] \
                                + mothers_mother_genwebid \
                                + '/' + three_gen_family['tgt_parents']['Mother']['GenWebID'] + mothers_mother_genwebid + '.jpg'):
                hourglass_table['c1r6'] = '    <td align="center "><img src="../' \
                                        + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid + '/' \
                                        + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid\
                                        + '.jpg" height="75"></td><!--c1r6-->\n'
            else:
                hourglass_table['c1r6'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'

            # c1r7 target person name and link
            #if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Mother']["GenWebID"]): --- I don't want a link unless the index.html file exists
            if os.path.isfile(folders_path + "/" + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid + "/index.html"):
                hourglass_table['c1r7'] = '    <td align="center "><a href=../' \
                        + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid + '/index.html><p>' \
                        + three_gen_family['tgt_parents']['Mother']['FullName'] + '</p></a></td><!--c1r7-->\n'
            else:
                hourglass_table['c1r7'] = '    <td align="center "><p>' \
                        + three_gen_family['tgt_parents']['Mother']['FullName'] + '</p></td><!--c1r7-->\n'

            if debug == True:
                    print('line 1284 - hourglass_table[c1r7] = ', hourglass_table['c1r7'])

            # c2r7 add arrow to select mother as new target
            if os.path.isdir(folders_path + "/" + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid):
                hourglass_table['c2r7'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                        + three_gen_family['tgt_parents']['Mother']["GenWebID"] + mothers_mother_genwebid \
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
        Given a person's PersonID (AKA OwnerID) fetch the NameTable entry for that
        person.
        The fetch_person_from_ID return is of the form spouse =
            [{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
              'Suffix': '', 'BirthYear': '1949','Prefix': '',
              'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
              'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
              'FullName': 'Page, Robert Kenneth'}]
        spouses is a list of spouse NameTable entries
        """
        spouseList = three_gen_family['spouseList']

        # spouses
        row = 6
        debug = False
        if person_facts['OwnerID'] == '':
            debug = True
            print('person = ', person)
            print('********* spouseList = ', spouseList)
            print('********* len(spouseList) = ', len(spouseList))
        for spouse_num in range(len(spouseList)):
            if debug == True:
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
                if debug == True:
                    print(folders_path + '/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid +'/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid + '.jpg')
                if os.path.isfile(folders_path + '/' + spouseList[spouse_num]['GenWebID']  + spouses_mothers_genwebid \
                                    + '/' + spouseList[spouse_num]['GenWebID'] + spouses_mothers_genwebid + '.jpg'):
                    hourglass_table[key] = '    <td align="center "><img src="../' \
                                            + spouseList[spouse_num]["GenWebID"] + spouses_mothers_genwebid + '/' \
                                            + spouseList[spouse_num]["GenWebID"] \
                                            + spouses_mothers_genwebid + '.jpg" height="75"></td><!--' + key + '-->\n'
                    if debug == True:
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
                if debug == True:
                    print('hourglass_table[' + key + '] = ', hourglass_table[key])
                row = row + 1

        #add children    ----left off here

        childList = three_gen_family['childList']
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

        row = 2
        debug = False
        if person_facts['OwnerID'] == '':
            debug = True
            print('person = ', person)
            print('********* childList = ', childList)
            print('********* len(childList) = ', len(childList))
        for child_num in range(len(childList)):
            if debug == True:
                print('********* child_num = ', child_num)
            if childList[child_num] == {}:
                continue
            if not short_genwebid_re.match(childList[child_num]['GenWebID']):
                continue

            child = childList[child_num]

            if debug: print('_generate_all_hourglass_webs line 1437 - child_num = ', child_num, '       child = ', child)

            if child == {}:
                continue
            childs_Owner_ID = child['OwnerID']


            childs_parents = rmagic.fetch_parents_from_ID(\
                                        self._tables['PersonTable'],\
                                        self._tables['NameTable'],\
                                        self._tables['FamilyTable'],\
                                        childs_Owner_ID)
            childs_mothers_genwebid = childs_parents['Mother']['GenWebID']
            # handle the case where the child's mother's name is incomplete
            if childs_mothers_genwebid == '' or (not short_genwebid_re.match(childs_mothers_genwebid)): childs_mothers_genwebid = '-'



            # c9r2, 4, 6, 8, ... 20 target person picture
            if len(childList[child_num]) > 0:
                key = 'c9r' + str(row)
                if debug == True:
                    print(folders_path + '/' + childList[child_num]['GenWebID'] + childs_mothers_genwebid + '/' + childList[child_num]['GenWebID'] + childs_mothers_genwebid + '.jpg')
                if os.path.isfile(folders_path + '/' + childList[child_num]['GenWebID'] + childs_mothers_genwebid \
                                    + '/' + childList[child_num]['GenWebID'] + childs_mothers_genwebid + '.jpg'):
                    hourglass_table[key] = '    <td align="center "><img src="../' \
                                            + childList[child_num]["GenWebID"] + childs_mothers_genwebid + '/' \
                                            + childList[child_num]["GenWebID"] + childs_mothers_genwebid \
                                            + '.jpg" height="75"></td><!--' + key + '-->\n'
                    if debug == True:
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
                        + childList[child_num]["GenWebID"] + childs_mothers_genwebid + '/index.html"><p>' \
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
                                        + childList[child_num]["GenWebID"] + childs_mothers_genwebid \
                                        + '/HourGlass.html><img src=../images/Right_Arrow.gif></a></td><!--' + key + '-->\n'
                if debug == True:
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
        if debug == True: print('\n line 943 _generate_all_hourglass_webs:  person_facts[BirthYear] = ', person_facts["BirthYear"], '     type(person_facts["BirthYear"]) = ',  type(person_facts["BirthYear"]))
        if person_facts['BirthYear'] == '': person_facts['BirthYear'] = '????' #if not birth year then pass


        buildString = buildString + ' - ' + person_facts['BirthYear']

        if debug == True: print('\n line 949 _generate_all_hourglass_webs: person_facts[DeathYear] = ', person_facts["DeathYear"], \
                '     type(person_facts["DeathYear"]) = ',  type(person_facts["DeathYear"]))

        if person_facts['DeathYear'] == '0':
            pass
        else:
            buildString = buildString + ' - ' + person_facts['DeathYear']

        buildString = buildString + "</h1>\n"
        hourglasshtmlList.append(buildString)

        if persons_mother == '': persons_mother = '-'
        commentString = '\t\t\t<p><a href="mailto:pagerk@gmail.com?subject=' + person + persons_mother + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: left; margin-right: auto" height="20"></a>\n'
        hourglasshtmlList.append(commentString)

        hourglasshtmlList.append('<table border="0" cellspacing="0" cellpadding="0" align="center">\n')
        #add the table to the HourGlass
        for row in range(1,21):
            for column in range(0,11):
                key = 'c' + str(column) + 'r' + str(row)
                hourglasshtmlList.append(hourglass_table[key])

        hourglasshtmlList.append('</table>')
        hourglasshtmlList.append('</body>')
        hourglasshtmlList.append('</html>')

        if os.path.isdir(folders_path + '/' + person + persons_mother):
            hourglassFile = open(folders_path + '/' + person + persons_mother + '/HourGlass.html', 'w')

            for row in hourglasshtmlList:
                hourglassFile.writelines(row)

            hourglassFile.close()
        else:

            folder_not_found = open(folders_path + '/zzz_FolderNotFound.txt','a')
            folder_not_found.write('***** _generate_all_hourglass_webs ****** folder = ' + person + persons_mother + '\n')
            folder_not_found.write('person_facts[FullName] = ' + person_facts['FullName'] \
                              + '\n person_facts[BirthYear] = ' + person_facts['BirthYear'] \
                              + '\n person_facts[DeathYear] = ' + person_facts['DeathYear'] + '\n')
            folder_not_found.close()
            #[{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
            #  'Suffix': '', 'BirthYear': '1949','Prefix': '',
            #  'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
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
    build_web.__init__


if __name__ == '__main__':
    main()
