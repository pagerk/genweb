#!/usr/bin/env python3

import os
import datetime
import string
import winsound

from . import rmagic

import sys
#sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts/MyLib')

class build_web_pages(object):

    def __init__(self, rmagicPath):
        self._rmagicPath = rmagicPath
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)

        self._matched_persons = []

        folders_path = \
            'D:/Family History/Family History CD/Research/Individual_Web_Pages'
        project_dict = self._get_proj_dict_from_xml(folders_path)
        #print('__init__ **** project_dict = ', project_dict)
        people_ids = sorted(project_dict.keys())
        #generating toc web pages works - uncomment following line when all else is debugged
        self._generate_toc_web(people_ids,folders_path)
        winsound.Beep(500,1000)
        person_dict = {}
        for person in people_ids:
            #print('__init__ **** person = ', person)
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                #print('__init__ **** person.lower().lstrip(abcdefghijklmnopqrstuvwxyz) = ', person.lower().lstrip('abcdefghijklmnopqrstuvwxyz'))
                person_dict = project_dict[person]
                #print('__init__ **** person_dict = ', person_dict)
                #_generate_all_hourglass_webs works - uncomment following line when all else is debugged
                self._generate_all_hourglass_webs(person, folders_path)
                if person_dict:
                    pass # to generate web pages, uncomment the following line
                    self._generate_person_web(person, person_dict, folders_path)
        winsound.Beep(500,1000)
        winsound.Beep(500,1000)


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
            a date or 0000
            The results are a dictionary with the following keys
            'BirthYear'
            'Surname'
            'Given'
            'Initial'"""

        import string

        # extract the date
        debug = 'no'
        if item == '':
            debug = 'yes'
        person = {}
        person['BirthYear'] = item.strip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        item = item.strip('0123456789')
        if debug == 'yes':
            print('date = ',person['BirthYear'], '  name string = ',item)

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

        if debug == 'yes':
            print('_separate_names line 121 item = ', item)
            print('_separate_names line 121 cap = ', cap)

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

        if debug == 'yes':
            print('line 138 separate_names------------ name = ', name)

        surname_exceptions = ["O'",'ap','de','De','le','Le','Mc','Mac','Van','of']
        givenname_exceptions = ['De']
        if len(name) == 1:
            person['Surname'] = name[0]
            person['Given'] = ''
            person['Initial'] = ''

        if len(name) == 2 and (name[0] in surname_exceptions):
            person['Surname'] = name[0] + name[1]
            person['Given'] = ''
            person['Initial'] = ''
        elif len(name) == 2:
            person['Surname'] = name[0]
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
                person['Surname'] = name[0] + name[1]
                person['Given'] =  name[2]
                person['Initial'] = name[3]
            elif (name[1] in surname_exceptions):
                person['Surname'] = name[0]
                person['Given'] = name[1] + name[2]
                person['Initial'] = name[3]
            else:
                person['Surname'] = name[0]
                person['Given'] = name[1]
                person['Initial'] =  name[2] + name[3]

        if len(name) == 5:
            if (name[0] in surname_exceptions):
                person['Surname'] = name[0] + name[1]
                person['Given'] = name[2]
                person['Initial'] =  name[3] + name[4]
            else:
                person['Surname'] = name[0]
                person['Given'] = name[1]
                person['Initial'] = name[2] + name[3] + name[4]

        if debug == 'yes':
            print('line 190 len(name) = ',len(name), '  person = ', person)


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
        for person in people_ids:
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                person_id_dict = self._separate_names(person)
                if person[0:2] == 'de':
                    current_letter = person[0:2]
                else:
                    current_letter = person[0]
                file_name = folders_path + '/' + current_letter + '.html'
                person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], self._tables['PersonTable'], person_id_dict)
                #print('person = ', person)
                #print('----- person_facts = ', person_facts)
                if len(person_facts) == 0:
                    not_found_file = open(folders_path + '/zzz_PeopleNotFound.txt','a')
                    not_found_file.write('*****build_web_pages line 208****** person = ' + person + '\n')
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
        return

    def _generate_person_web(self, genwebid, person_dict, folders_path):
        artifact_ids = sorted(person_dict.keys())
        #print('artifact_ids = ', artifact_ids)
        person_id_dict = self._separate_names(genwebid)
        person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], self._tables['PersonTable'], person_id_dict)[0]
        #print('genwebid = ', genwebid, '----- person_facts = ', person_facts)
        folder_path = folders_path + '/' + genwebid
        #print('folder_path = ', folder_path)

        if not os.path.isdir(folder_path):
            print('*****build_web_pages ' + folder_path + '**** does not exist****')
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

        birth_year = person_facts['BirthYear'] if len(person_facts['BirthYear']) > 2 else '?'
        death_year = person_facts['DeathYear'] if len(person_facts['DeathYear']) > 2 else '?'
        f.write('\t\t<h1><a name="Top"></a>' + person_facts["FullName"] + ' - ' + birth_year + ' - ' + death_year + '</h1>\n')
        f.write('\t\t<a href= "HourGlass.html"><img src="../images/family.bmp"></a>\n')

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
            # Generate index table
            if index_tbl_col == 1:
                index_tbl_lines.append('\t\t\t<tr>\n')

            index_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')
            #print('*************** artifact = ', artifact)
            #print('person_dict[artifact] = ', person_dict[artifact])
            index_tbl_lines.append('\t\t\t\t\t<p><a href="#' + person_dict[artifact]['file'] + '">' + person_dict[artifact]['title'] + '</a></p>\n')
            index_tbl_lines.append('\t\t\t\t</td>\n')

            if index_tbl_col == 3:
                index_tbl_lines.append('\t\t\t</tr>\n')

            index_tbl_col = index_tbl_col + 1 if index_tbl_col < 3 else 1


            # Generate artifacts table
            if person_dict[artifact]['type'] == 'picture':
                artifacts_tbl_lines.append('\t\t<a name="' + person_dict[artifact]['file'] + '"/>\n')
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
                if os.path.isfile(folder_path + '/+' + artifact + '.jpg'): # if a hi res image exists, insert a link to it
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<a href="../' + genwebid + '/+' + artifact + '.jpg' + '" target="Resource Window">\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t\t<img src="../' + genwebid + '/' + artifact + '.jpg' + '" target="Resource Window">\n')
                if os.path.isfile(folder_path + '/+' + artifact + '.jpg'): # if a hi res image exists, insert a link to it - continued
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t</a>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t<tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t\t<td ALIGN="CENTER" VALIGN="TOP">\n')
                if 'caption' in person_dict[artifact]:
                    artifacts_tbl_lines.append('\t\t\t\t\t\t\t<p>' + person_dict[artifact]["caption"] + '</p>\n')
                else:
                    f = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    f.write('*****build_web_pages caption Not Found in person_dict[artifact] = ' + person_dict[artifact] + '\n')
                    f.close()
                    print('*** caption Not Found in person_dict[artifact] = ', person_dict[artifact])
                artifacts_tbl_lines.append('\t\t\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t\t\t\t</table>\n')
                artifacts_tbl_lines.append('\t\t\t\t</td>\n')
                artifacts_tbl_lines.append('\t\t\t</tr>\n')
                artifacts_tbl_lines.append('\t\t</table>\n')
                artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')


            if person_dict[artifact]['type'] == 'inline':
                #print('Now processing ' + artifact + '.src')
                if os.path.isfile(folder_path + '/' + artifact + '.src'): # if a src exists, insert it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + person_dict[artifact]['file'] + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<H2>' + person_dict[artifact]['title'] + '</H2>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')
                    artifact_source = open(folder_path + '/' + artifact + '.src', 'r')
                    for line in artifact_source:
                        artifacts_tbl_lines.append(line)
                    artifact_source.close()
                    artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')
                else:
                    artifact_issue = open(folders_path + '/zzz_Artifact_xml_issue.txt','a')
                    artifact_issue.write('*****build_web_pages ' + folder_path + '/' + artifact + '.src file Not Found\n')
                    artifact_issue.close()
                    print('*****build_web_pages ' + folder_path + '/' + artifact + '.src file Not Found')


            if person_dict[artifact]['type'] == 'href':
                print('Now processing href = ' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file'])
                if os.path.isfile(person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file']): # if an html exists, reference it - continued
                    artifacts_tbl_lines.append('\t\t<a name="' + person_dict[artifact]['folder'] + '/' + person_dict[artifact]['file'] + '"/>\n')
                    artifacts_tbl_lines.append('\t\t<H2>' + person_dict[artifact]['title'] + '</H2>\n')
                    artifacts_tbl_lines.append('\t\t\t\t<td align="center" valign=top>\n')
                    artifacts_tbl_lines.append('\t\t<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>\n')

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

        return

    def _generate_all_hourglass_webs(self, person, folders_path):

        """
        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database. Note that "person" is the same
        as person_facts['GenWebID']
        """
        if person == 'BrentMabel1896':
            print('_generate_all_hourglass_webs ***** person = ', person)

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
            print('person = ', person)
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
                if os.path.isdir(folders_path + "/" + grandparents['Father']["GenWebID"]):
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
                if os.path.isdir(folders_path + "/" + grandparents['Mother']["GenWebID"]):
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
            if person_facts['OwnerID'] == '':
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
                    if row > 2:
                        key = 'c7r' + str(row)
                        hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c7r4, 6, 8, ... 20-->\n'

                    row = row + 1
                    # c9r3, 5, 7, ... 19 target person name and link
                    key = 'c9r' + str(row)
                    hourglass_table[key] = '    <td align="center "><a href="../' \
                            + childList[child_num]["GenWebID"] + '/index.html"><p>' \
                            + childList[child_num]["FullName"] + '</p></a></td><!--' + key + '-->\n'

                    # c7r3, 5, 7, ... 19 add maroon cell
                    key = 'c7r' + str(row)
                    hourglass_table[key] = '    <td align="center " bgcolor="maroon "></td><!--c7r3, 5, 7, ... 19-->\n'

                    if row == 5:
                        # c6r5 add maroon cell
                        key = 'c6r' + str(row)
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

                f = open(folders_path + '/zzz_FolderNotFound.txt','a')
                f.write('*********** folder = ' + person_facts['GenWebID'] + '\n')
                f.close()

        return


def main():
    # Get the RootsMagic database info
    rmagicPath = 'C:\\Dropbox\\Apps\\RootsMagic\\myfamily.rmgc'
    #rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    build_web = build_web_pages(rmagicPath)
    build_web.__init__


if __name__ == '__main__':
    main()
