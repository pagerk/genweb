#!/usr/bin/env python3

import os
import datetime
import string

from . import rmagic

import sys
#sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts/MyLib')

class Build_web(object):

    def __init__(self, rmagicPath):
        self._rmagicPath = rmagicPath
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)

        self._matched_persons = []

        folders_path = \
            'D:/Family History/Family History CD/Research/Individual_Web_Pages'
        project_dict = self._get_proj_dict_from_xml(folders_path)
        people_ids = sorted(project_dict.keys())
        self._generate_toc_web(people_ids,folders_path)
        person_dict = {}
        for person in people_ids:
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                person_dict = project_dict[person]
                if person_dict:
                    pass # to generate web pages, uncomment the following line
                    #self._generate_person_web(person, person_dict, folders_path)

    def _get_proj_dict_from_xml(self,folders_path):
        args = os.listdir(folders_path)
        folders = []
        for a in args:
            if os.path.isdir(folders_path + "/" + a):
                folders.append(folders_path + "/" + a)
            else:
                pass
        folder_file_contents = []
        overall_dictionary = {}
        for folder in folders:
            big_dictionary = {}
            person_id = os.path.basename(folder)
            folder_files = os.listdir(folder)
            #print('folder = ', folder)
            big_dictionary = {}
            for file_name in folder_files:
                file_string = ''
                # Separate the path from the file name
                base_file_name = os.path.basename(file_name)
                artifact_id = os.path.splitext(base_file_name)[0]
                # The only file contents we care about are xml files
                if (base_file_name.endswith('.xml')):
                    #print('file_name = ', file_name)
                    with open(folder + '/' + file_name, 'r') as f:
                        # create a dictionary of xml file contents
                        file_data = []
                        tags = ['path','file','title','caption','comment','people','height','mod_date']
                        types = ['inline','picture','href']
                        tags_types = types + tags
                        dictionary = {}
                        for line in f:
                            lc_line_str = str.lower(line)
                            line_str = line.replace('<![CDATA[','')
                            line_str = line_str.replace(']]>','')
                            #print(line_str)
                            for type in tags_types:
                                if lc_line_str.find(type) > 0:
                                    if type in types:
                                        dictionary['type'] = type
                                    elif type in tags:
                                        find_tag = '<'+type+'>'
                                        start_position = lc_line_str.find(find_tag)+len(find_tag)
                                        find_tag = '</'+type+'>'
                                        end_position = lc_line_str.find(find_tag)
                                        dictionary[type] = line_str[start_position:end_position]
                                        #print(dictionary)
                                    #else:
                                        #break
                    big_dictionary[artifact_id] = dictionary
            overall_dictionary[person_id] = big_dictionary
        return overall_dictionary


    def _separate_names(self,item):
        """given a string that is a concatenation of names with their first
            letters capitalized [e.g. PageRobertK1949], separate them into
            separate words or characters and the date -
            assumes person IDs contain no spaces and every person's ID has
            a date or 0000"""

        import string

        # extract the date
        person = {}
        person['BirthYear'] = item[-4:]
        item = item.strip('0123456789')
        #print('date = ',person['BirthYear'], '  name string = ',item)
        # Separate the text portion of the file name into a list of names that start
        # with capital letters
        item_length = len(item)
        last_char = item_length - 1
        letter_num = 0
        cap = []
        name = []
        for letter_num in range(item_length):
            if item[letter_num].isupper():
                cap.append(letter_num)

        if 0 not in cap:
            cap.insert(0,0)

        cap_length = len(cap)
        for cap_num in range(cap_length):
            start = cap[cap_num]
            end_index = cap_num + 1
            if end_index <= (cap_length - 1):
                end = cap[cap_num+1]
                name.append(item[start:end])
            elif cap[cap_length-1] < item_length - 1:
                end = item_length
                name.append(item[start:end])
            else:
                name.append(item[start])
        #print('separate_names------------ name = ', name)

        surname_exceptions = ["O'",'ap','de','De','le','Le','Mc','Mac','Van','of']
        givenname_exceptions = ['De']
        if len(name) == 1:
            person['Surname'] = name[0]
            person['Given'] = ''
            person['Initial'] = ''
            #print('len(name) = ',len(name), '  person = ', person)

        if len(name) == 2 and (name[0] in surname_exceptions):
            person['Surname'] = name[0] + name[1]
            person['Given'] = ''
            person['Initial'] = ''
        elif len(name) == 2:
            person['Surname'] = name[0]
            #print('len(name) = ',len(name), '  person = ', person)
            person['Given'] = name[1]
            person['Initial'] = ''

        if len(name) == 3:
                if (name[0] in surname_exceptions):
                    person['Given'] = name[2]
                    person['Surname'] = name[0] + name[1]
                elif (name[1] in givenname_exceptions):
                    person['Surname'] = name[0]
                    person['Given'] =  name[1] + name[2]
                else:
                    person['Surname'] = name[0]
                    person['Given'] = name[1]
                    person['Initial'] = name[2]


        if len(name) == 4:
                if (name[0] in surname_exceptions):
                    if (name[2] in givenname_exceptions):
                        person['Surname'] = name[0] + name[1]
                        person['Given'] = name[2] + name[3]
                    else:
                        person['Surname'] = name[0] + name[1]
                        person['Given'] = name[2]
                        person['Initial'] = name[3]
                else:
                    person['Surname'] = name[0]
                    person['Given'] = name[1] + name[2]
                    person['Initial'] = name[3]

        if len(name) == 5:
            person['Surname'] = name[0] + name[1]
            person['Given'] = name[2] + name[3]
            person['Initial'] = name[4]


        return person

    def _generate_toc_web(self,people_ids,folders_path):
        person_dict = {}
        print('people_ids = ', people_ids)
        previous_letter = ''
        table_cell_ct = 0
        table_col = 0
        for person in people_ids:
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                person_id_dict = self._separate_names(person)
                if person[0:2] == 'de':
                    current_letter = person[0:2]
                else:
                    current_letter = person[0]
                file_name = folders_path + '/' + current_letter + '.html'
                person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], person_id_dict)
                #print('person = ', person)
                #print('----- person_facts = ', person_facts)
                if len(person_facts) == 0:
                    print('*********** not found: person = ', person)
                    break
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
        return

    def _generate_person_web(self, person, person_dict):
        artifact_ids = sorted(person_dict.keys())
        person_id_dict = self._separate_names(person)
        person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], person_id_dict)
        #print('person = ', person, '----- person_facts = ', person_facts)
        for artifact in artifact_ids:
            #print(artifact,person_dict[artifact])
            pass
        return

    def _generate_hourglass_webs(self):
        return

def main():
    # Get the RootsMagic database info
    rmagicPath = 'C:\\Dropbox\\Apps\\RootsMagic\\myfamily.rmgc'
    #rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    build_web = Build_web(rmagicPath)
    build_web.__init__


if __name__ == '__main__':
    main()
