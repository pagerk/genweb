#!/usr/bin/env python3

import os
import datetime
import time
import string
import winsound
import glob
import re

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
        self._rmagicPath = rmagicPath
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)

        self._matched_persons = []

        debug = 'no'

        folders_path = \
            'C:/Family History/Family History CD/Research/Individual_Web_Pages'
        project_dict = self._get_proj_dict_from_xml(folders_path)

        people_ids = sorted(project_dict.keys()) # a list of genwebid
        #generating toc web pages
        self._generate_toc_web(people_ids,folders_path)

        person_dict = {}
        for person in people_ids:
            """if 'enter genwebid' in person:
                debug = 'yes'
                print('__init__ **** person = ', person)"""
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                """if debug == 'yes':
                    print('__init__ **** person.lower().lstrip(abcdefghijklmnopqrstuvwxyz) = ', person.lower().lstrip('abcdefghijklmnopqrstuvwxyz'))"""
                person_dict = project_dict[person]
                """if debug == 'yes':
                    print('__init__ **** person_dict = ', person_dict)"""

                self._generate_all_hourglass_webs(person, folders_path)

                # generate web pages
                self._generate_person_web(person, person_dict, folders_path)
        t1 = timer()
        print('execution time =' , int((t1 - t0)//60), ' minutes, ',  int((t1 - t0)%60), ' seconds or ', (t1 - t0), ' seconds total')
        winsound.Beep(500,1000)
        winsound.Beep(500,1000)


    def _get_proj_dict_from_xml(self,folders_path):
        """
        Build a dictionary with each person's genwebid as a key. Each person's
        key will be attached to a dictionary containing zero or more artifacts.
        Each artifact will consist of a key (the artifact_id) of the
        form: YYYYMMDD##Last_nameFirst_nameMiddle_initialYYYY where the
        first date in the id is the date of the artifact (birth, death,
        marriage, etc.) and the last date is the birth year of the person whose
        folder has "custody" of the artifact. Associated with that artifact key
        is a dictionary of the artifact description. The artifact description
        has a key indicating the type of artifact ('inline','picture','href')
        and the data elements describing the artifact and it's location: 'path',
        'file','folder','title','caption','comment','people','height','mod_dat'
        """
        os.chdir(folders_path)
        # I only want folders that have at least a first and last name with a four digit number
        folders = glob.glob("[a-zA-Z']*[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
        #print('folders = ', folders)
        folder_file_contents = []
        overall_dictionary = {}
        for folder in folders:
            genwebid = folder
            os.chdir(folders_path + '/' + folder)
            #print('current working dir = ', os.getcwd(), '    folder = ', folder, '   xml files = ', glob.glob('*.xml'))
            folder_files = glob.glob('*.xml') #xml files are artifact description files

            if len(folder_files)  == 0:  # if there are no xml files in this person's folder
                continue                 # move on to the next folder

            big_dictionary = {}
            for file_name in folder_files:

                if not (folder in file_name): # if  xml file name doesn't match folder
                    xml_file_name_issue_file = open(folders_path + '/zzz_xml_file_name_issue.txt','a')
                    xml_file_name_issue_file.write('*****_get_proj_dict_from_xml file name ' + file_name + ' should Not be in ' + folder + '\n')
                    xml_file_name_issue_file.close()
                    continue
                proper_format = re.compile("[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
                if not proper_format.match(file_name.rstrip('.xml')):
                    xml_file_name_issue_file = open(folders_path + '/zzz_xml_file_name_issue.txt','a')
                    xml_file_name_issue_file.write('*****_get_proj_dict_from_xml file name ' + folder + '/' + file_name + ' does not have the proper data format\n')
                    xml_file_name_issue_file.close()
                    continue

                file_string = ''

                # create a dictionary of xml file contents
                with open(file_name, 'r') as current_xml_file:
                    file_data = []
                    tags = ['path','file','folder','title','caption','comment','people','height','mod_dat']
                    types = ['inline','picture','href']
                    tags_types = types + tags
                    dictionary = {}

                    #extract all data from the current xml file
                    for line in current_xml_file:
                        line = line.lstrip(' ')
                        line = line.replace('<![CDATA[','')
                        line = line.replace(']]>','')
                        lc_line = line.lower()
                        #print(line_str)
                        for type in tags_types:
                            if lc_line.find(type) > 0:
                                if type in types:
                                    dictionary['type'] = type
                                elif type in tags:
                                    line = line.replace('<'+type+'>','')
                                    line = line.replace('</'+type+'>','')
                                    line = line.lstrip('\t')
                                    line = line.rstrip('\n')
                                    dictionary[type] = line
                                    #print(dictionary)
                                    pass
                    big_dictionary[file_name.replace('.xml','')] = dictionary
            overall_dictionary[genwebid] = big_dictionary
        #print('overall_dictionary a = ', overall_dictionary)
        #print('overall_dictionary a keys = ', sorted(overall_dictionary.keys()))

        people_re = re.compile("[A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")
        # people excluded are those with only one name and a date
        people_excluded_re = re.compile('[A-Z][a-z]+[0-9][0-9][0-9][0-9]')
        people_excluded = []
        for genwebid in overall_dictionary: #make sure everybody is in the dictionary
            if len(overall_dictionary[genwebid]) == 0: # if there are no xml files skip this person
                people_excluded_file = open(folders_path + '/zzz_PeopleExcluded.txt','a')
                people_excluded_file.write('People excluded are (from _get_proj_dict_from_xml): ' + '\n')
                people_excluded_file.write(genwebid + ' was excluded because no xml for this person\n')
                people_excluded_file.close()
                continue
            #for each xml file, ensure that the people references in <people>
            #   - have legitimate names
            #   - have their own folder
            for artifact in overall_dictionary[genwebid]:
                people_in_artifact = people_re.findall(overall_dictionary[genwebid][artifact]['people'])
                people_excluded = list(set(people_excluded + people_excluded_re.findall(overall_dictionary[genwebid][artifact]['people'])))
                for person_in_artifact in people_in_artifact:
                    if not os.path.isdir(folders_path + "/" + person_in_artifact):
                        os.makedirs(folders_path + "/" + person_in_artifact)
                    #if not os.path.isdir(folders_path + "/" + genwebid):
                    #    os.makedirs(folders_path + "/" + genwebid)

        # if there are any names excluded, save those for manual cleanup
        if len(people_excluded) > 0:
            people_excluded.sort()
            people_excluded_file = open(folders_path + '/zzz_PeopleExcluded.txt','a')
            people_excluded_file.write('People excluded are (from _get_proj_dict_from_xml): ' + '\n')
            for person_excluded in people_excluded:
                people_excluded_file.write(person_excluded + '\n')
            people_excluded_file.close()

        # assign all artifacts to all of the appropriate people
        overall_dictionary_genwebid_list = sorted(overall_dictionary.keys())
        for genwebid in overall_dictionary_genwebid_list:
            if len(overall_dictionary[genwebid]) == 0:
                continue

            for artifact in overall_dictionary[genwebid]:
                people_in_artifact = people_re.findall(overall_dictionary[genwebid][artifact]['people'])
                for person_in_artifact in people_in_artifact:
                    # if the person has no artifacts assigned
                    if person_in_artifact == '':
                        not_found_file = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                        not_found_file.write('person_in_artifact = ' + person_in_artifact + '  artifact = ' + artifact + '\n')
                        not_found_file.write('check the people field of ' + artifact + '\n')
                        not_found_file.write('genwebid = ' + genwebid + '  artifact = ' + artifact + '\n')
                        not_found_file.close()
                    else:
                        #print('genwebid = ', genwebid, '  artifact = ', artifact)
                        #print('person_in_artifact = ', person_in_artifact, '  artifact = ', artifact)
                        if person_in_artifact not in overall_dictionary:
                            #print('overall_dictionary[person_in_artifact] is not found for person_in_artifact = ', person_in_artifact)
                            #print('overall_dictionary[genwebid]) = ', overall_dictionary[genwebid])
                            overall_dictionary[person_in_artifact] = {}
                            overall_dictionary[person_in_artifact][artifact] = overall_dictionary[genwebid][artifact]

                        else:
                            overall_dictionary[person_in_artifact][artifact] = overall_dictionary[genwebid][artifact]
                    pass
        #print('overall_dictionary b = ', overall_dictionary)

        #print('overall_dictionary b keys = ', sorted(overall_dictionary.keys()))
        return overall_dictionary


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
            'Initial'"""

        # extract the date
        debug = 'no'
        if item == "":
            debug = 'yes'
        person = {}
        person['BirthYear'] = item.strip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'")
        item = item.strip('0123456789')


        people_re = re.compile(r"([A-Z][a-z]+)")

        names = people_re.split(item)
        names = [x for x in names if x != '']

        surname_exceptions = ["O'",'ap','de','De','le','Le','Mc','Mac','Van','of']
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

        person['FullName'] = person['Given'] + person['Initial'] + person['Surname']

        if item != person['Surname'] + person['Given'] + person['Initial'] :
            print('item = ', item, ' person full name = ', person['Given'], ' ', person['Initial'], ' ', person['Surname'])


        return person

    def _generate_toc_web(self,people_ids,folders_path):
        """
        This generates the Table of Contents web pages for the whole website.
        The people_ids are of the form: LastnameFirstnameM0000
        If there is no birthyear, it is set to 0000
        """
        person_dict = {}
        #print('people_ids = ', people_ids)
        previous_letter = ''
        table_cell_ct = 0
        table_col = 0
        debug = 'no'
        for person in people_ids:
            if person == "":
                debug = 'yes'
                print('person = ', person)
            if person.lower().lstrip("abcdefghijklmnopqrstuvwxyz'").isdigit():
                person_id_dict = self._separate_names(person)
                if debug == 'yes':
                    person_dict_keys = sorted(person_dict.keys())
                    for key in person_dict_keys:
                        print(key, ' = ', person_id_dict[key])

                if person[0:2] == 'de':
                    current_letter = person[0:2]
                else:
                    current_letter = person[0]
                file_name = folders_path + '/' + current_letter + '.html'
                person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], self._tables['PersonTable'], person_id_dict)
                if debug == 'yes':
                    print('person = ', person)
                    print('----- person_facts = ', person_facts)
                if len(person_facts) == 0:
                    not_found_file = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                    not_found_file.write('*****build_web_pages line 276 ****** person = ' + person + '\n')
                    not_found_file.close()
                    continue

                person_facts = person_facts[0]

                if current_letter != previous_letter:
                    if previous_letter != '':
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
                    f.write('\t\t<table align="center" bgcolor="#FFCCCC" border cellpadding="8" cellspacing="4" cols="3">\n')
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
                    f.write('\t\t\t\t\t\t<a href= "./' + person + '/index.html"><img src="./images/individual.bmp"></a>\n')
                    f.write('\t\t\t\t\t\t<a href= "./' + person + '/HourGlass.html"><img src="./images/family.bmp"></a>\n')
                    birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
                    death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
                    f.write('\t\t\t\t\t\t<br>' + birth_year + ' - ' + death_year + '</h5></p>\n')
                    f.write('\t\t\t\t</td>\n')

                if current_letter == previous_letter:
                    table_col = table_col + 1
                    f.write('\t\t\t\t<td align="CENTER" valign="BOTTOM">\n')
                    full_given = ''
                    for given in person_facts['Given']:
                        full_given = full_given + ' ' + given
                    f.write('\t\t\t\t\t<h5>' + person_facts['Surname'] + ', ' + full_given + '\n')
                    f.write('\t\t\t\t\t\t<a href= "./' + person + '/index.html"><img src="./images/individual.bmp"></a>\n')
                    f.write('\t\t\t\t\t\t<a href= "./' + person + '/HourGlass.html"><img src="./images/family.bmp"></a>\n')
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

    def _last(self,item):
        return item[-4:]

    def _generate_person_web(self, genwebid, person_dict, folders_path):
        person_id_dict = self._separate_names(genwebid)
        if genwebid == 'StoriesPersonal0000':
            artifact_ids = sorted(person_dict.keys(), key = self._last)
        else:
            artifact_ids = sorted(person_dict.keys())
            #print('artifact_ids = ', artifact_ids)

        person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], self._tables['PersonTable'], person_id_dict)
        if person_facts == []:
            people_excluded_file = open(folders_path + '/zzz_PeopleExcluded.txt','a')
            people_excluded_file.write('In _generate_person_web, genwebid = ' + genwebid \
                    + '  was not found in the rootsmagic datbase. It was searched for with the following information person_id_dict[Surname] = ' + person_id_dict['Surname'] \
                    + '  person_id_dict[Given] = ' + person_id_dict['Given'] + '  person_id_dict[Initial] = ' + person_id_dict['Initial'] \
                    + '  person_id_dict[BirthYear] = ' + person_id_dict['BirthYear'] + '\n')
            people_excluded_file.close()
            return
        else:
            person_facts = person_facts[0]
        #print('genwebid = ', genwebid, '----- person_facts = ', person_facts)
        folder_path = folders_path + '/' + genwebid
        person_folder_path = folders_path + '/' + genwebid
        #print('folder_path = ', folder_path)

        if not os.path.isdir(folder_path):
            print('*****build_web_pages ' + folder_path + '**** created ****')
            os.makedirs(folder_path)


        f = open(folder_path + '/index.html','w')
        f.write('<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >\n')
        f.write('<html>\n')
        f.write('\t<head>\n')
        f.write('\t\t<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />\n')
        f.write('\t\t<title>Family History</title>\n')
        f.write('\t\t<link href="../css/individual.css" type="text/css" rel="stylesheet" />\n')
        f.write('\t\t<style type="text/css">\n')
        f.write('\t\t/*<![CDATA[*/\n')
        f.write('\t\tdiv.ReturnToTop {text-align: right}\n')
        f.write('\t\t/*]]>*/\n')
        f.write('\t\t</style>\n')
        f.write('\t</head>\n')
        f.write('\t<body background="../images/back.gif">\n')

        if genwebid == 'StoriesPersonal0000':
            f.write('\t\t<h1><a name="Top"></a>Personal Stories from our Ancestors</h1>\n')
        else:
            birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
            death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
            f.write('\t\t<h1><a name="Top"></a>' + person_facts["FullName"] + ' - ' + birth_year + ' - ' + death_year + '</h1>\n')
            f.write('\t\t<a href= "HourGlass.html"><img src="../images/family.bmp"></a>\n')

        if person_dict == {}:
            f.write('\t</body>\n')
            f.write('</html>\n')
            f.close()
            return

        index_tbl_lines = []
        index_tbl_lines.append('\t\t<!-- Index table -->\n')
        index_tbl_lines.append('\t\t<table align="center" border cellpadding="4" cellspacing="4" cols="3">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')
        index_tbl_lines.append('\t\t\t<col width="33%">\n')

        artifacts_tbl_lines = []
        artifacts_tbl_lines.append('\t\t<!-- Beginning of Content -->\n')
        artifacts_tbl_lines.append('\t\t<!-- artifacts -->\n')

        index_tbl_col = 1
        for artifact in artifact_ids:
            artifact_genwebid = artifact.lstrip('+0123456789')
            artifact_folder_path = folders_path + '/' + artifact_genwebid
            # Generate index table
            if index_tbl_col == 1:
                index_tbl_lines.append('\t\t\t<tr>\n')

            index_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')

            if artifact == '':
                print('*************** artifact = ', artifact)
                print('person_dict[artifact] = ', person_dict[artifact])
                print('genwebid = ', genwebid, '   person_dict = ', person_dict)
            index_tbl_lines.append('\t\t\t\t\t<p><a href="#' + os.path.basename(person_dict[artifact]['file']) + '">' + person_dict[artifact]['title'] + '</a></p>\n')
            index_tbl_lines.append('\t\t\t\t</td>\n')

            if index_tbl_col == 3:
                index_tbl_lines.append('\t\t\t</tr>\n')

            index_tbl_col = index_tbl_col + 1 if index_tbl_col < 3 else 1


            # Generate artifacts table
            if person_dict[artifact]['type'] == 'picture':
                artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(person_dict[artifact]['file']) + '"/>\n')
                artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="2">\n')
                artifacts_tbl_lines.append('\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<H2>' + person_dict[artifact]['title'] + '</H2>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if not os.path.isfile(artifact_folder_path + '/' + artifact + '.jpg') and genwebid in artifact: # if  image doesn't exist, note it to be fixed
                    pic_issue_file = open(folders_path + '/zzz_Artifact_picture_issue.txt','a')
                    pic_issue_file.write('*****build_web_pages picture Not Found: artifact = ' + artifact + ' for ' + genwebid + '\n')
                    pic_issue_file.close()
                if os.path.isfile(artifact_folder_path + '/+' + artifact + '.jpg'): # if a hi res image exists, insert a link to it
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<a href="../' + artifact_genwebid + '/+' + artifact + '.jpg' + '" target="Resource Window">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<img src="../' + artifact_genwebid + '/' + artifact + '.jpg' + '" target="Resource Window">\n')
                if os.path.isfile(artifact_folder_path + '/+' + artifact + '.jpg'): # if a hi res image exists, insert a link to it - continued
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t</a>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if 'caption' in person_dict[artifact]:
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<p>' + person_dict[artifact]["caption"] + '</p>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
                else:
                    f = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    f.write('*****_generate_person_web caption Not Found in person_dict[artifact] = ' + person_dict[artifact] + '\n')
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
            if person_dict[artifact]['type'] == 'inline':
                #print('Now processing ' + artifact + '.src')
                if os.path.isfile(artifact_folder_path + '/' + artifact + '.src') and proper_format.match(artifact): # if a src exists, insert it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + os.path.basename(person_dict[artifact]['file']) + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<H2>' + person_dict[artifact]['title'] + '</H2>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
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
                    artifact_issue.write('*****build_web_pages line 526: ' + artifact_folder_path + '/' + artifact + '.src file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 527: person_dict[artifact][file] = ' + person_dict[artifact]['file'] +'\n')
                    artifact_issue.write('*****build_web_pages line 528: person_dict[artifact][title] = ' + artifact +'\n')
                    artifact_issue.close()
                    if not proper_format.match(artifact):
                        src_file_name_issue_file = open(folders_path + '/zzz_src_file_name_issue.txt','a')
                        src_file_name_issue_file.write('*****_generate_person_web - inline: file name ' + artifact + '.src' + file_name + ' does not have the proper data format\n')
                        src_file_name_issue_file.close()
                    continue
                    #print('*****build_web_pages ' + artifact_folder_path + '/' + artifact + '.src file Not Found')


            if person_dict[artifact]['type'] == 'href':
                #print('person_dict[' + artifact + '] = ', person_dict[artifact])
                html_path = artifact_folder_path + '/' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file']
                #print('Now processing href = ',html_path)
                if os.path.isfile(artifact_folder_path + '/' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file']): # if an html exists, reference it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + person_dict[artifact]['file'] + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<table WIDTH="600" Align="CENTER" NOBORDER COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t<tr>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t<H2>\n')
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t\t\t<a href="../' + artifact_genwebid + '/' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file'] + '" target="_blank"><H2>' + person_dict[artifact]['title'] + '</H2></a>\n<p><a href="mailto:pagerk@gmail.com?subject=' + artifact + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>\n')
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
                    artifact_issue.write('*****build_web_pages line 563: href file Not Found\n')
                    artifact_issue.write('*****build_web_pages line 564:' + artifact_folder_path + '/' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file'] +'\n')
                    artifact_issue.close()
                    pass

            pass



        index_tbl_lines.append('\t\t</table>\n')
        for line in index_tbl_lines:
            f.write(line)

        artifacts_tbl_lines.append('\t</body>\n')
        artifacts_tbl_lines.append('</html>\n')

        for line in artifacts_tbl_lines:
            f.write(line)
        f.close()
        pass

        return      # return from _generate_person_web

    def _generate_all_hourglass_webs(self, person, folders_path):

        """
        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID']
        """
        debug = 'no'
        if 'enter genwebid' in person:
            print('_generate_all_hourglass_webs ***** person = ', person)
            debug = 'yes'

        # self._separate_names(person) is of the form:
        # {'BirthYear':'1896','Given':'Archie','Initial':'B', 'Surname':'Abdill'}
        person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'],\
                                                     self._tables['PersonTable'], \
                                                     self._separate_names(person))
    	# person_facts is of the form:
        #[{'Surname': 'Page', 'OwnerID': '1','Nickname': 'Bob',
        #  'Suffix': '', 'BirthYear': '1949','Prefix': '',
        #  'DeathYear': '0', 'Sex':'male,'GenWebID':'PageRobertK1949',
        #  'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1',
        #  'FullName': 'Page, Robert Kenneth'}]
    	# where these rootsmagic tags are equivalent ; OwnerID = person_ID

        if len(person_facts) == 0:
            #print('person = ', person)
            f = open(folders_path + '/zzz_PeopleNotFound.txt','a')
            f.write('*****build_web_pages target person section ****** person = ' + person + '\n')
            possible_matches = rmagic.fetch_person_from_fuzzy_name(self._tables['NameTable'], self._separate_names(person), year_error=2)
            for match_num in range(len(possible_matches)):
                f.write('possible match number = ' + str(match_num) + '\n')
                f.write(str(possible_matches[match_num]['GenWebID']) + '\n')
            f.close()
        else:
            person_facts = person_facts[0]

            #This builds the standard html header I use for the family history files
            #print('person = ', person, '  OwnerID = ', person_facts['OwnerID'])
            #print('person_facts = ', person_facts)
            headerList = []
            headerList.append("<html>\n")
            headerList.append("<head>\n")
            headerList.append('    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />' + "\n")

            given_names = ''
            for names in person_facts['Given']:
                given_names = given_names + ' ' + names

            headerList.append('    <title>' + person_facts['FullName'] + '</title>' + "\n")
            headerList.append('    <link href="../css/individual.css" type="text/css" rel="stylesheet" />' + "\n")
            headerList.append('    <style type="text/css">' "\n")
            headerList.append('    /*<![CDATA[*/' + "\n")
            headerList.append(' div.ReturnToTop {text-align: right}' + "\n")
            headerList.append('    /*]]>*/' + "\n")
            headerList.append("    </style>\n")
            headerList.append("</head>\n")
            headerList.append('<body background="../images/back.gif">' + "\n")
            buildString = '    <h1><a name="Top"></a>' + person_facts['FullName']
            if int(person_facts['BirthYear']) == 0:       #if not birth year then pass
                pass
            else:
                buildString = buildString + ' - ' + person_facts['BirthYear']

            if int(person_facts['DeathYear']) == 0:       # if no death year then pass
                pass
            else:
                buildString = buildString + ' - ' + person_facts['DeathYear']

            buildString = buildString + "</h1>\n"
            headerList.append(buildString)

            commentString = '\t\t\t<p><a href="mailto:pagerk@gmail.com?subject=' + person_facts['GenWebID'] + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: left; margin-right: auto" height="20"></a>\n'
            headerList.append(commentString)

            hourglasshtmlList = headerList

            hourglasshtmlList.append('<TABLE border="0" cellspacing="0" cellpadding="0" align="center">\n')

            hourglass_table = {}

            # Row 1
            hourglass_table['c1r1'] = '    <td align="center "><h2>Grandparents</h2></td><!--c1r1-->\n'
            hourglass_table['c2r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c2r1-->\n'
            hourglass_table['c3r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c3r1-->\n'
            hourglass_table['c4r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c4r1-->\n'
            hourglass_table['c5r1'] = '    <td align="center "><h2>Parents</h2></td><!--c5r1-->\n'
            hourglass_table['c6r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c6r1-->\n'
            hourglass_table['c7r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp;</td><!--c7r1-->\n'
            hourglass_table['c8r1'] = '    <td align="center ">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td><!--c8r1-->\n'
            hourglass_table['c9r1'] = '    <td align="center "><h2>Children</h2></td><!--c9r1-->\n'

            for row in range(1,21):
                key = 'c0r' + str(row)
                hourglass_table[key] = '  <tr><!--' + key + '-->\n'

                key = 'c10r' + str(row)
                hourglass_table[key] = '  </tr><!--' + key + '-->\n'

            for column in range(1,10):
                for row in range(2,21):
                    key = 'c' + str(column) + 'r' + str(row)
                    hourglass_table[key] = '    <td align="center "></td><!--' + key + '-->\n'

            if len(person_facts) == 0:
                f = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                f.write('*****build_web_pages hourglass table row #1 ****** person = ', person + '\n')
                possible_matches = rmagic.fetch_person_from_fuzzy_name(self._tables['NameTable'], self._separate_names(person), year_error=2)
                for match_num in range(len(possible_matches)):
                    f.write('possible match number = ' + str(match_num) + '\n')
                    f.write(str(possible_matches[match_num]['GenWebID']) + '\n')
                f.close()
            else:
                # c5r4 target person picture
                if os.path.isfile(folders_path + '/' + person_facts['GenWebID'] \
                                    + '/' + person_facts['GenWebID'] + '.jpg'):
                    hourglass_table['c5r4'] = '    <td align="center "><img src="../' + person_facts["GenWebID"] + '/' \
                        + person_facts["GenWebID"] + '.jpg" height="75"></td><!--c5r4-->\n'
                else:
                    hourglass_table['c5r4'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c5r4-->\n'

                # c5r5 target person name and link
                hourglass_table['c5r5'] = '    <td align="center "><a href=index.html><p>' + person_facts["FullName"] + '</p></a></td><!--c5r5-->\n'

            #add grandparents
                        #Build father - possibilities are that:
            #                    - there is no father's name in the person's entry
            #                                   - father's position empty and no link
            #                    - there is a father's name in the person's entry
            #                                   - father's position (if no record, no name available)
            #                    - there is a record for the father
            #                                   - father's position and link
            #                    - there is not a record for the father
            #                                   - no father's position and no link
            #Need to do three things here
            # - if I have the person's name, use it
            # - if there is a person_id for the person, use it
            # - if neither, don't use maroon
            grandparents = rmagic.fetch_parents_from_ID(\
                                        self._tables['PersonTable'],\
                                        self._tables['NameTable'],\
                                        self._tables['FamilyTable'],\
                                        person_facts['OwnerID'])

            # preload the silhouette in case grandparents are unknown
            hourglass_table['c1r2'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'
            hourglass_table['c1r3'] = '    <td align="center "><p>unknown</p></a></td><!--c1r3-->\n'
            hourglass_table['c2r3'] = '    <td align="center " bgcolor="maroon "></td><!--c2r3-->\n'
            hourglass_table['c3r3'] = '    <td align="center " bgcolor="maroon "></td><!--c3r3-->\n'
            hourglass_table['c3r4'] = '    <td align="center " bgcolor="maroon "></td><!--c3r4-->\n'
            hourglass_table['c3r5'] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'
            hourglass_table['c4r5'] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'
            hourglass_table['c1r6'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'
            hourglass_table['c1r7'] = '    <td align="center "><p>unknown</p></a></td><!--c1r7-->\n'
            hourglass_table['c2r7'] = '    <td align="center " bgcolor="maroon "></td><!--c2r7-->\n'
            hourglass_table['c3r7'] = '    <td align="center " bgcolor="maroon "></td><!--c3r7-->\n'
            hourglass_table['c3r6'] = '    <td align="center " bgcolor="maroon "></td><!--c3r6-->\n'
            hourglass_table['c3r5'] = '    <td align="center " bgcolor="maroon "></td><!--c3r5-->\n'
            hourglass_table['c4r5'] = '    <td align="center " bgcolor="maroon "></td><!--c4r5-->\n'

            debug = 'no'
            if person_facts['OwnerID'] == '':
                debug = 'yes'
                print('person = ', person)
                print('********* grandparents = ', grandparents)
                print('********* len(grandparents) = ', len(grandparents))

            if grandparents['Father']['FullName'] != '':  # grandfather exists
                # c1r2 target person picture
                if os.path.isfile(folders_path + '/' + grandparents['Father']['GenWebID'] \
                                    + '/' + grandparents['Father']['GenWebID'] + '.jpg'):
                    hourglass_table['c1r2'] = '    <td align="center "><img src="../' \
                                            + grandparents['Father']["GenWebID"] + '/' \
                                            + grandparents['Father']["GenWebID"] \
                                            + '.jpg" height="75"></td><!--c1r2-->\n'
                else:
                    #print(folders_path + '/' + grandparents['Father']['GenWebID'] \
                    #                + '/' + grandparents['Father']['GenWebID'] + '.jpg')
                    hourglass_table['c1r2'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r2-->\n'

                # c1r3 target person name and link
                # was: if os.path.isdir(folders_path + "/" + grandparents['Father']["GenWebID"]): --- I don't want a link unless the index.html file exists
                if os.path.isfile(folders_path + "/" + grandparents['Father']["GenWebID"] + "/index.html"):
                    hourglass_table['c1r3'] = '    <td align="center "><a href=../' \
                            + grandparents['Father']["GenWebID"] + '/index.html><p>' \
                            + grandparents['Father']['FullName'] + '</p></a></td><!--c1r3-->\n'
                else:
                    hourglass_table['c1r3'] = '    <td align="center "><p>' \
                            + grandparents['Father']['FullName'] + '</p></td><!--c1r3-->\n'

                # c2r3 add arrow to select grandfather as new target
                if os.path.isdir(folders_path + "/" + grandparents['Father']["GenWebID"]):
                    hourglass_table['c2r3'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                            + grandparents['Father']["GenWebID"] \
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
                pass # don't add any content

            if grandparents['Mother']['FullName'] != '':  # grandmother exists
                # c1r6 target person picture
                if os.path.isfile(folders_path + '/' + grandparents['Mother']['GenWebID'] \
                                    + '/' + grandparents['Mother']['GenWebID'] + '.jpg'):
                    hourglass_table['c1r6'] = '    <td align="center "><img src="../' \
                                            + grandparents['Mother']["GenWebID"] + '/' \
                                            + grandparents['Mother']["GenWebID"] \
                                            + '.jpg" height="75"></td><!--c1r6-->\n'
                else:
                    hourglass_table['c1r6'] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--c1r6-->\n'

                # c1r7 target person name and link
                #if os.path.isdir(folders_path + "/" + grandparents['Mother']["GenWebID"]): --- I don't want a link unless the index.html file exists
                if os.path.isfile(folders_path + "/" + grandparents['Mother']["GenWebID"] + "/index.html"):
                    hourglass_table['c1r7'] = '    <td align="center "><a href=../' \
                            + grandparents['Mother']["GenWebID"] + '/index.html><p>' \
                            + grandparents['Mother']['FullName'] + '</p></a></td><!--c1r7-->\n'
                else:
                    hourglass_table['c1r7'] = '    <td align="center "><p>' \
                            + grandparents['Mother']['FullName'] + '</p></td><!--c1r7-->\n'

                if debug == 'yes':
                        print('hourglass_table[c1r7] = ', hourglass_table['c1r7'])

                # c2r7 add arrow to select grandmother as new target
                if os.path.isdir(folders_path + "/" + grandparents['Mother']["GenWebID"]):
                    hourglass_table['c2r7'] = '    <td align="center " bgcolor="maroon "><a href= ../' \
                                            + grandparents['Mother']["GenWebID"] \
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
                pass # don't add any content

            #add spouses
            spouseList = rmagic.fetch_spouses_from_ID(\
                                        self._tables['NameTable'],\
                                        self._tables['PersonTable'],\
                                        self._tables['FamilyTable'],\
                                        person_facts['OwnerID'])

            row = 6
            debug = 'no'
            if person_facts['OwnerID'] == '':
                debug = 'yes'
                print('person = ', person)
                print('********* spouseList = ', spouseList)
                print('********* len(spouseList) = ', len(spouseList))
            for spouse_num in range(len(spouseList)):
                if debug == 'yes':
                    print('********* spouse_num = ', spouse_num)

                # c5r6,8,10,12 target person picture
                if len(spouseList[spouse_num]) > 0:
                    key = 'c5r' + str(row)
                    if debug == 'yes':
                        print(folders_path + '/' + spouseList[spouse_num]['GenWebID'] + '/' + spouseList[spouse_num]['GenWebID'] + '.jpg')
                    if os.path.isfile(folders_path + '/' + spouseList[spouse_num]['GenWebID'] \
                                        + '/' + spouseList[spouse_num]['GenWebID'] + '.jpg'):
                        hourglass_table[key] = '    <td align="center "><img src="../' \
                                                + spouseList[spouse_num]["GenWebID"] + '/' \
                                                + spouseList[spouse_num]["GenWebID"] \
                                                + '.jpg" height="75"></td><!--' + key + '-->\n'
                        if debug == 'yes':
                            print('hourglass_table[' + key + '] = ', hourglass_table[key])
                    else:
                        hourglass_table[key] = '    <td align="center "><img src="../images/silhouette.jpg" height="75"></td><!--' + key + '-->\n'

                    row = row + 1
                    # c5r7,9,11,13 target person name and link
                    key = 'c5r' + str(row)
                    hourglass_table[key] = '    <td align="center "><a href="../' \
                            + spouseList[spouse_num]["GenWebID"] + '/index.html"><p>' \
                            + spouseList[spouse_num]["FullName"] + '</p></a></td><!--' + key + '-->\n'

                    # c4r7,9,11,13 add arrow to select spouse as new target
                    key = 'c4r' + str(row)
                    hourglass_table[key] = '    <td align="center"><a href= ../' \
                                            + spouseList[spouse_num]["GenWebID"] \
                                            + '/HourGlass.html><img src=../images/Right_Arrow_Maroon.gif></a></td><!--' + key + '-->\n'
                    if debug == 'yes':
                        print('hourglass_table[' + key + '] = ', hourglass_table[key])
                    row = row + 1

            #add children
            childList = rmagic.fetch_children_from_ID(\
                                        self._tables['ChildTable'],\
                                        self._tables['NameTable'],\
                                        self._tables['PersonTable'],\
                                        self._tables['FamilyTable'],\
                                        person_facts['OwnerID'])

            row = 2
            debug = 'no'
            if person_facts['OwnerID'] == 'StrongShirleyR1917':
                debug = 'yes'
                print('person = ', person)
                print('********* childList = ', childList)
                print('********* len(childList) = ', len(childList))
            for child_num in range(len(childList)):
                if debug == 'yes':
                    print('********* child_num = ', child_num)

                # c9r2, 4, 6, 8, ... 20 target person picture
                if len(childList[child_num]) > 0:
                    key = 'c9r' + str(row)
                    if debug == 'yes':
                        print(folders_path + '/' + childList[child_num]['GenWebID'] + '/' + childList[child_num]['GenWebID'] + '.jpg')
                    if os.path.isfile(folders_path + '/' + childList[child_num]['GenWebID'] \
                                        + '/' + childList[child_num]['GenWebID'] + '.jpg'):
                        hourglass_table[key] = '    <td align="center "><img src="../' \
                                                + childList[child_num]["GenWebID"] + '/' \
                                                + childList[child_num]["GenWebID"] \
                                                + '.jpg" height="75"></td><!--' + key + '-->\n'
                        if debug == 'yes':
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
                            + childList[child_num]["GenWebID"] + '/index.html"><p>' \
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
                                            + childList[child_num]["GenWebID"] \
                                            + '/HourGlass.html><img src=../images/Right_Arrow.gif></a></td><!--' + key + '-->\n'
                    if debug == 'yes':
                        print('hourglass_table[' + key + '] = ', hourglass_table[key])
                    row = row + 1

            #add the table to the HourGlass
            for row in range(1,21):
                for column in range(0,11):
                    key = 'c' + str(column) + 'r' + str(row)
                    hourglasshtmlList.append(hourglass_table[key])

            hourglasshtmlList.append('</table>')
            hourglasshtmlList.append('</body>')
            hourglasshtmlList.append('</html>')

            if os.path.isdir(folders_path + '/' + person_facts['GenWebID']):
                hourglassFile = open(folders_path + '/' + person_facts['GenWebID'] + '/HourGlass.html', 'w')

                for row in hourglasshtmlList:
                    hourglassFile.writelines(row)

                hourglassFile.close()
            else:

                folder_not_found = open(folders_path + '/zzz_FolderNotFound.txt','a')
                folder_not_found.write('***** _generate_all_hourglass_webs ****** folder = ' + person_facts['GenWebID'] + '\n')
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


def main():
    # Get the RootsMagic database info
    rmagicPath = 'C:\\Users\\pager\\Dropbox\\Apps\\RootsMagic\\myfamily.rmgc'
    #rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    build_web = build_web_pages(rmagicPath)
    build_web.__init__


if __name__ == '__main__':
    main()
