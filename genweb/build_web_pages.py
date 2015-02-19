#!/usr/bin/env python3

import os
import datetime
import string

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
        people_ids = sorted(project_dict.keys())
        #generating toc web pages works - uncomment following line when all else is debugged
        #self._generate_toc_web(people_ids,folders_path)
        person_dict = {}
        for person in people_ids:
            if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
                person_dict = project_dict[person]
                if person_dict:
                    pass # to generate web pages, uncomment the following line
                    #self._generate_person_web(person, person_dict, folders_path)
                    self._generate_all_hourglass_webs(person, folders_path)

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
                person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], person_id_dict)
                #print('person = ', person)
                #print('----- person_facts = ', person_facts)
                if len(person_facts) == 0:
                    f = open(folders_path + '/PeopleNotFound.txt','a')
                    f.write('*********** person = ', person + '\n')
                    f.close()
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

    def _generate_person_web(self, person, person_dict):
        artifact_ids = sorted(person_dict.keys())
        person_id_dict = self._separate_names(person)
        person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], person_id_dict)
        #print('person = ', person, '----- person_facts = ', person_facts)
        for artifact in artifact_ids:
            #print(artifact,person_dict[artifact])
            pass
        return

    def _generate_all_hourglass_webs(self, person, folders_path):
        """
        This will create an hourglass html file for each person in the
        Individual_Web_Pages folder in that person's folder. The source of the
        information is my rootsmagic database.
        """

        if person.lower().lstrip('abcdefghijklmnopqrstuvwxyz').isdigit():
            person_id_dict = self._separate_names(person)
            # person_id_dict is of the form:
            # {'BirthYear':'1896','Given':'Archie','Initial':'B',Surname':'Abdill'}

            person_facts = rmagic.fetch_person_from_name(self._tables['NameTable'], person_id_dict)
        	# person_facts is of the form:
            # person_facts =  [{'Surname': 'Page', 'OwnerID': '1',
            #        'Nickname': 'Bob', 'Suffix': '', 'BirthYear': '1949',
            #        'Prefix': '', 'DeathYear': '0',
            #        'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1'}]
        	# where these rootsmagic tags are equivalent ; OwnerID = person_ID

            #print('person = ', person)
            #print('----- person_facts = ', person_facts)
            if len(person_facts) == 0:
                f = open(folders_path + '/PeopleNotFound.txt','a')
                f.write('*********** person = ', person + '\n')
                f.close()
            else:
                person_facts = person_facts[0]
                self._generate_one_hourglass_web(person, person_facts, folders_path)

        return

    def _generate_one_hourglass_web(self, person, person_facts, folders_path):
        # person =
    	# person_facts is of the form:
        # person_facts =  [{'Surname': 'Page', 'OwnerID': '1',
        #        'Nickname': 'Bob', 'Suffix': '', 'BirthYear': '1949',
        #        'Prefix': '', 'DeathYear': '0',
        #        'Given': ['Robert', 'Kenneth'], 'IsPrimary': '1'}]
    	# where these rootsmagic tags are equivalent ; OwnerID = person_ID

        hourglassFile = open(folders_path + '/HourGlass.html', 'w')


        #This builds the standard html header I use for the family history files
        print('person = ', person)
        #print('person_facts = ', person_facts)
        headerList = []
        headerList.append("<html>\n")
        headerList.append("<head>\n")
        headerList.append('    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />' + "\n")

        given_names = ''
        for names in person_facts['Given']:
            given_names = given_names + ' ' + names

        headerList.append('    <title>' + person_facts['Surname'] + ',' + given_names + '</title>' + "\n")
        headerList.append('    <link href="../css/individual.css" type="text/css" rel="stylesheet" />' + "\n")
        headerList.append('    <style type="text/css">' "\n")
        headerList.append('    /*<![CDATA[*/' + "\n")
        headerList.append(' div.ReturnToTop {text-align: right}' + "\n")
        headerList.append('    /*]]>*/' + "\n")
        headerList.append("    </style>\n")
        headerList.append("</head>\n")
        headerList.append('<body background="../images/back.gif">' + "\n")
        buildString = '    <h1><a name="Top"></a>' + person_facts['Surname'] + ',' + given_names
        if person_facts['BirthYear'] == '':       #if not birth year then pass
            pass
        else:
            buildString = buildString + ' - ' + person_facts['BirthYear']

        if person_facts['DeathYear'] == '':       # if no death year then pass
            pass
        else:
            buildString = buildString + ' - ' + person_facts['DeathYear']

        buildString = buildString + "</h1>\n"
        headerList.append(buildString)
        #buildString = '<address>' + personDict['address'] + ', ' + personDict['phone'] +\
        #              ', ' + personDict['email'] + ', ' + personDict['webpage'] + "</address>\n"
        #print('headerList = ', headerList)                                """

        strSpouseArrow    = "../images/Right_Arrow_Maroon.gif"
        strLtArrow        = "../images/Left_Arrow.gif"
        strRtArrow        = "../images/Right_Arrow.gif"
        strTDCenter       = "    <td align=\"center\""
        strColor          = " bgcolor=\"maroon\""
        strWidth          = " width=\"75\""
        conTR             = "  <tr>\n"
        conSlashTR        = "  </tr>\n"
        conSlashTD        = "    </td>\n"
        conImageSrc       = "<img src="
        conHref           = "<a href="
        conAEnd           = "</a>"
        conHGlass         = "/HourGlass.html"
        conClose          = ">"
        conDummyPic       = "../images/back.gif"
        conDummyMalePic   = "../images/male.jpg"
        conDummyFemalePic = "../images/female.jpg"
        conNameFmt        = "<p>"
        conNameFmtClose   = "</p>"
        con3Space         = "&nbsp; &nbsp; &nbsp;"
        con6Space         = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"

        hourglasshtmlList = headerList

        #Build self
        person_sex = rmagic.fetch_sex_from_ID(\
                                    self._tables['PersonTable'],\
                                    person_facts['OwnerID'])
        conDummyPic = conDummyMalePic if person_sex == "male" else conDummyFemalePic


        if os.path.isfile(folders_path + '/' + person + '.jpg'):
            strSelfPic = strTDCenter + conClose + conImageSrc + "\"" + "../" +\
                         person + "/" + person + '.jpg' \
                         + strWidth + conClose + conSlashTD
        else:
            strSelfPic = strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                         + "\"" + strWidth + conClose + conSlashTD

        strSelfName = strTDCenter + conClose + conHref + "\"" + "index.html"\
                      + "\"" + conClose + conNameFmt + person_facts['Surname']\
                      + ', ' + given_names + conNameFmtClose\
                      + conAEnd + conSlashTD

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
        # - if I have the person's name, use it - blnName
        # - if there is a person_id for the person, use it - blnHref
        # - if neither, don't use maroon
        conDummyPic = conDummyMalePic
        #print('person_facts = ', person_facts)
        parents = rmagic.fetch_parents_from_ID(\
                                    self._tables['PersonTable'],\
                                    self._tables['NameTable'],\
                                    self._tables['FamilyTable'],\
                                    person_facts['OwnerID'])
        if parents['Father']['Surname'] != '' or parents['Father']['Given'] != '':  # Does the father exist?
             #  - there is a father's name in the person's entry

            father_dict = parents['Father']
            person_id = father_dict['Surname']
            for given_num in range(len(father_dict['Given'])):
                if given_num == 0:
                    person_id = person_id + father_dict['Given'][0]
                else:
                    person_id = person_id + father_dict['Given'][given_num][0]
            person_id = person_id + father_dict['BirthYear']

            if os.path.isfile(folders_path + '/' + person_id + '.jpg'): #photo of the father
                                              #    - father's position and link
                strFatherPic = strTDCenter + conClose + conImageSrc + "\"" + "../" +\
                               person_id + "/" + person_id\
                               + ".jpg\"" + strWidth + conClose + conSlashTD
            else:#there is not an entry for the father - no father's position and no link
                strFatherPic = strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                               + "\"" + strWidth + conClose + conSlashTD

        else: #even if the father doesn't exist,
              #I need to generate the html to fill the space
            strFatherPic = strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                           + "\"" + strWidth + conClose + conSlashTD

        if len(person_id) > 0 \
               and os.path.isdir(folders_path + '/' + person_id): # there is a web folder for the father
            blnHref = 1
        else:
            blnHref = 0

        blnName = 1 if person_id != '' else 0 # the father's name exists in the rootsmagic db


        father_full_name = ''
        if blnName ==1:
            father_full_name = father_dict['Surname']
            for given_num in range(len(father_dict['Given'])):
                if given_num == 0:
                    father_full_name = father_full_name + ', ' + father_dict['Given'][0]
                else:
                    father_full_name = father_full_name + ' ' + father_dict['Given'][given_num][0]
            #print('father_full_name = ', father_full_name)
            strFatherName = strTDCenter + conClose + conNameFmt + father_full_name\
                                     + conNameFmtClose + conAEnd + conSlashTD
            strF32 = strTDCenter + strColor + conClose + conSlashTD
            strF33 = strTDCenter + strColor + conClose + conSlashTD
            strF43 = strTDCenter + strColor + conClose + conSlashTD
            if blnHref ==1:
                strFatherName = strTDCenter + conClose + conHref + "\"" + "../" +\
                                person_id + "/index.html" + "\"" + conClose\
                                + conNameFmt + father_full_name + conNameFmtClose\
                                + conAEnd + conSlashTD
                strF32 = strTDCenter + strColor + conClose + conHref\
                  + "../" + person_id + conHGlass + conClose + conImageSrc\
                  + strLtArrow + conClose + conAEnd + conSlashTD
            else: pass

        else:
            strFatherName = strTDCenter + conClose + conNameFmt + father_full_name\
                            + conNameFmtClose + conSlashTD
            strF32 = strTDCenter + conClose + conSlashTD
            strF33 = strTDCenter + conClose + conSlashTD
            strF43 = strTDCenter + conClose + conSlashTD

        #Build mother
        conDummyPic = conDummyFemalePic
        if parents['Mother']['Surname'] != '' or parents['Mother']['Given'] != '':  # Does the mother exist?
             #  - there is a mother's name in the person's entry
            mother_dict = parents['Mother']
            for given_num in range(len(mother_dict['Given'])):
                if given_num == 0:
                    person_id = person_id + mother_dict['Given'][0]
                else:
                    person_id = person_id + mother_dict['Given'][given_num][0]
            person_id = person_id + mother_dict['BirthYear']

            if os.path.isfile(folders_path + '/' + person_id + '.jpg'): #photo of the mother
                                              #    - mother's position and link
                strMotherPic = strTDCenter + conClose + conImageSrc + "\"" + "../" +\
                               person_id + "/" + person_id\
                               + ".jpg\"" + strWidth + conClose + conSlashTD
            else:#there is not an entry for the mother - no mother's position and no link
                strMotherPic = strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                               + "\"" + strWidth + conClose + conSlashTD

        else: #even if the mother doesn't exist,
              #I need to generate the html to fill the space
            strMotherPic = strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                           + "\"" + strWidth + conClose + conSlashTD

        if len(person_id) > 0 \
               and os.path.isdir(folders_path + '/' + person_id): # there is a web folder for the mother
            blnHref = 1
        else:
            blnHref = 0

        blnName = 1 if person_id != '' else 0 # the mother's name exists in the rootsmagic db



        mother_full_name = ''
        if blnName ==1:
            mother_full_name = mother_dict['Surname']
            for given_num in range(len(mother_dict['Given'])):
                if given_num == 0:
                    mother_full_name = mother_full_name + ', ' + mother_dict['Given'][0]
                else:
                    mother_full_name = mother_full_name + ' ' + mother_dict['Given'][given_num][0]
            #print('mother_full_name = ', mother_full_name)
            strMotherName = strTDCenter + conClose + conNameFmt + mother_full_name\
                                     + conNameFmtClose + conAEnd + conSlashTD
            strM63 = strTDCenter + strColor + conClose + conSlashTD
            strM72 = strTDCenter + strColor + conClose + conSlashTD
            strM73 = strTDCenter + strColor + conClose + conSlashTD
            if blnHref ==1:
                strMotherName = strTDCenter + conClose + conHref + "\"" + "../" +\
                                person_id + "/index.html" + "\"" + conClose\
                                + conNameFmt + mother_full_name + conNameFmtClose\
                                + conAEnd + conSlashTD
                strM72 = strTDCenter + strColor + conClose + conHref\
                  + "../" + person_id + conHGlass + conClose + conImageSrc\
                  + strLtArrow + conClose + conAEnd + conSlashTD
            else: pass

        else:
            strMotherName = strTDCenter + conClose + conNameFmt + mother_full_name\
                            + conNameFmtClose + conSlashTD
            strM63 = strTDCenter + conClose + conSlashTD
            strM72 = strTDCenter + conClose + conSlashTD
            strM73 = strTDCenter + conClose + conSlashTD

    # Father or Mother - if father's or mother's name exists do maroon and parent's heading
    #                   - blnFatherOrMother
        if (len(father_full_name) > 0) or (len(mother_full_name)) > 0 :
            strParentHd = "<h2>Grandparents</h2>"
            strFM53 = strTDCenter + strColor + conClose + conSlashTD
            strFM54 = strTDCenter + strColor + conClose + conSlashTD
        else:
            strParentHd = ""
            strFM53 = strTDCenter + conClose + conSlashTD
            strFM54 = strTDCenter + conClose + conSlashTD


    # children
        print('person_facts = ', person_facts)
        childList = rmagic.fetch_children_from_ID(\
                                    self._tables['ChildTable'],\
                                    self._tables['NameTable'],\
                                    self._tables['PersonTable'],\
                                    self._tables['FamilyTable'],\
                                    person_facts['OwnerID'])
        #print('children = ', children)
        childNum = len(childList) #number of children

    # Child 1
        strChildPicList = []
        strPic7 = ['','']     # These aren't used until child 3+
        strName7 = ['','']    # These aren't used until child 3+
        strName8 = ['','']    # These aren't used until child 3+
        if childNum >= 1:
            intchildNum = 0 # List index to get to children
            # Extract the record for the first child:

            childDict = childList[intchildNum]
            # start building the person_id for this child: LastGivenIYYYY
            person_id = childDict['Surname']
            child_full_name = childDict['Surname']
            for given_num in range(len(childDict['Given'])):
                if given_num == 0:
                    person_id = person_id + childDict['Given'][0]
                    child_full_name = child_full_name + ', ' + childDict['Given'][0]
                else:
                    person_id = person_id + childDict['Given'][given_num]
                    child_full_name = child_full_name + ' ' + childDict['Given'][given_num][0]
            person_id = person_id + childDict['BirthYear']
            person_id = person_id.replace('.','')
            print( 'child 1 name = ', child_full_name, '   person_id = ', person_id)


            person_sex = rmagic.fetch_sex_from_ID(\
                                    self._tables['PersonTable'],\
                                    childDict['OwnerID'])
            conDummyPic = conDummyMalePic if person_sex == "male" else conDummyFemalePic

            if os.path.isfile(folders_path + '/' + person_id + '.jpg'):
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + "../"\
                                       + person_id + "/" + person_id + '.jpg' + "\""\
                                       + strWidth + conClose + conSlashTD)
            else:
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                                       + "\"" + strWidth + conClose + conSlashTD)
        else:
            pass



        if len(person_id) > 0 \
               and os.path.isdir(folders_path + '/' + person_id): # there is a web folder for this person
            blnHref = 1
        else:
            blnHref = 0

        print('childDict = ', childDict)
        blnName = 1 if len(childDict) > 0 else 0

        blnChildExists = []
        blnChildExists.append(blnName)

        strChildNameList = []
        strChildLinkList = []
        if blnName :
            if blnHref :    #add link to name and right arrow to bar
                strChildNameList.append(strTDCenter + conClose + conHref + "\"" + "../"\
                                        + person_id + "/index.html" + "\""\
                                        + conClose + conNameFmt + child_full_name +\
                                        conNameFmtClose + conAEnd + conSlashTD)
                strChildLinkList.append(strTDCenter+ strColor+ conClose+ conHref\
                                        + "../"+ person_id + conHGlass\
                                        + conClose+ conImageSrc + strRtArrow + conClose\
                                        + conAEnd+ conSlashTD)
            else: #No link for the child's name and no right arrow
                strChildNameList.append(strTDCenter+ conClose+ conNameFmt\
                                       + child_full_name + conNameFmtClose+ conAEnd\
                                       + conSlashTD)
                strChildLinkList.append(strTDCenter+ strColor+ conClose+ conSlashTD)
        else: #No child's name and no index file
            strChildNameList.append(strTDCenter+ conClose+ conSlashTD)
            strChildLinkList.append(strTDCenter+ strColor+ conClose+ conSlashTD)

    # Child 2
        if childNum >= 2:
            intchildNum = intchildNum + 1 # List index to get to children
             # Extract the record for the this child:
            childDict = childList[intchildNum]

            # start building the person_id for this child: LastGivenIYYYY
            person_id = childDict['Surname']
            child_full_name = childDict['Surname']
            for given_num in range(len(childDict['Given'])):
                if given_num == 0:
                    person_id = person_id + childDict['Given'][0]
                    child_full_name = child_full_name + ', ' + childDict['Given'][0]
                else:
                    person_id = person_id + childDict['Given'][given_num]
                    child_full_name = child_full_name + ' ' + childDict['Given'][given_num][0]
            person_id = person_id + childDict['BirthYear']
            person_id = person_id.replace('.','')
            print( 'child 1 name = ', child_full_name, '   person_id = ', person_id)


            person_sex = rmagic.fetch_sex_from_ID(\
                                    self._tables['PersonTable'],\
                                    childDict['OwnerID'])
            conDummyPic = conDummyMalePic if person_sex == "male" else conDummyFemalePic



            if os.path.isfile(folders_path + '/' + person_id + '.jpg'):
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + "../"\
                                       + person_id + "/" + person_id + '.jpg' + "\""\
                                       + strWidth + conClose + conSlashTD)
            else:
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                                       + "\"" + strWidth + conClose + conSlashTD)
        else:
            pass

        if len(childDict) > 0 \
            and os.path.isdir(folders_path + '/' + person_id):  # there is a web folder for the child
            blnHref = 1
        else:
            blnHref = 0


        blnName = 1 if len(childDict) > 0 else 0  # the child name exists in the record

        blnChildExists.append(blnName)

        if blnName :
            if blnHref :   #add link to name and right arrow to bar
                strChildNameList.append(strTDCenter + conClose + conHref + "\"" + "../" +\
                                        person_id + "/index.html" + "\"" +\
                                        conClose + conNameFmt + child_full_name +\
                                        conNameFmtClose + conAEnd + conSlashTD)
                strChildLinkList.append(strTDCenter + strColor + conClose + conHref\
                                        + "../" + person_id + conHGlass\
                                        + conClose + conImageSrc + strRtArrow + conClose\
                                        + conAEnd+ conSlashTD)
                strC2_58 = strTDCenter + strColor + conClose + conHref + "../" +\
                           person_id + conHGlass + conClose + conImageSrc\
                           + strRtArrow + conClose + conAEnd+ conSlashTD
                #note that strC2_58 == strChildLinkList that was appended in the previous line
            else:  #No link for the child's name and no right arrow
                strChildNameList.append(strTDCenter + conClose + conNameFmt\
                                       + child_full_name + conNameFmtClose + conAEnd\
                                       + conSlashTD)
                strChildLinkList.append(strTDCenter + strColor + conClose + conSlashTD)
                strC2_58 = strTDCenter + strColor + conClose + conSlashTD
        else: #No child's name and no index file
            strChildNameList.append(strTDCenter + conClose + conSlashTD)
            strChildLinkList.append(strTDCenter + strColor + conClose + conSlashTD)
            strC2_58 = strTDCenter + conClose + conSlashTD

    # Child 3 through childNum
        for intchildNum in range(2,childNum):
            # Extract the record for the this child:
            childDict = childList[intchildNum]
            print( 'childs name = ', childDict['name'])

            # start building the person_id for this child: LastGivenIYYYY
            person_id = childDict['Surname']
            child_full_name = childDict['Surname']
            for given_num in range(len(childDict['Given'])):
                if given_num == 0:
                    person_id = person_id + childDict['Given'][0]
                    child_full_name = child_full_name + ', ' + childDict['Given'][0]
                else:
                    person_id = person_id + childDict['Given'][given_num]
                    child_full_name = child_full_name + ' ' + childDict['Given'][given_num][0]
            person_id = person_id + childDict['BirthYear']
            person_id = person_id.replace('.','')
            print( 'child 1 name = ', child_full_name, '   person_id = ', person_id)


            person_sex = rmagic.fetch_sex_from_ID(\
                                    self._tables['PersonTable'],\
                                    childDict['OwnerID'])
            conDummyPic = conDummyMalePic if person_sex == "male" else conDummyFemalePic


            if os.path.isfile(folders_path + '/' + person_id + '.jpg'):
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + "../"\
                                       + person_id + "/" + person_id + '.jpg' + "\""\
                                       + strWidth + conClose + conSlashTD)
            else:
                strChildPicList.append(strTDCenter + conClose + conImageSrc + "\"" + conDummyPic\
                                       + "\"" + strWidth + conClose + conSlashTD)

            blnHref = 1 if len(childDict) > 0 else 0    # the folder exists for the child

            # the child name exists in the parents record:
            if len(childDict[intchildNum]) > 0:
                blnName = 1
            else:
                blnName = 0

            blnChildExists.append(blnName)
            if blnName :
                strPic7.append(strTDCenter + strColor + conClose + conSlashTD)
                if blnHref:
                    strChildNameList.append(strTDCenter + conClose + conHref + "\"" + "../" +\
                                            person_id + "/index.html" + "\""\
                                            + conClose + conNameFmt + child_full_name +
                                            conNameFmtClose + conAEnd + conSlashTD)
                    strChildLinkList.append(strTDCenter + strColor + conClose + conHref\
                                        + "../" + person_id + conHGlass\
                                        + conClose + conImageSrc + strRtArrow + conClose\
                                        + conAEnd+ conSlashTD)
                    strName7.append(strTDCenter + strColor + conClose + conSlashTD)
                    strName8.append(strTDCenter + strColor + conClose + conHref + "../"\
                                    + person_id + conHGlass + conClose +\
                                    conImageSrc + strRtArrow + conClose + conAEnd+ conSlashTD)
                else :
                    strChildNameList.append(strTDCenter + conClose + conNameFmt +\
                                            child_full_name + conNameFmtClose +\
                                            conAEnd + conSlashTD)
                    strChildLinkList.append(strTDCenter + strColor + conClose + conSlashTD)
                    strName7.append(strTDCenter + strColor + conClose + conSlashTD)
                    strName8.append(strTDCenter + strColor + conClose + conSlashTD)
            else:
                strChildNameList.append(strTDCenter + conClose + conSlashTD)
                strPic7.append(strTDCenter + conClose + conSlashTD)
                strName7.append(strTDCenter + conClose + conSlashTD)
                strName8.append(strTDCenter + conClose + conSlashTD)

    # Spouse 1 through intSpouseCnt
        print('person_facts = ', person_facts)
        spouseList = rmagic.fetch_spouses_from_ID(\
                                    self._tables['NameTable'],\
                                    self._tables['PersonTable'],\
                                    self._tables['FamilyTable'],\
                                    person_facts['OwnerID'])
        #print('spouses = ', spouses)
        spouseNum = len(spouseList) #number of spouses


        strSpousePicList = []
        strSpouseNameList = []
        strSpouseLinkList = []
        #fill the lists with dummy values in case I don't need them all
        for intSpouseNum in range(10):
            strSpousePicList.append(strTDCenter + conClose + conImageSrc + "\"" + conDummyPic +\
                                    "\"" + strWidth + conClose + conSlashTD)
            strSpouseNameList.append(strTDCenter + conClose + conSlashTD)

        print( 'range(spouseNum) = ', range(spouseNum))
        for intSpouseNum in range(spouseNum):
            # Extract the record for the this spouse:
            spouseDict = spouseList[intSpouseNum]

            # start building the person_id for this child: LastGivenIYYYY
            person_id = spouseDict['Surname']
            spouse_full_name = spouseDict['Surname']
            for given_num in range(len(spouseDict['Given'])):
                if given_num == 0:
                    person_id = person_id + spouseDict['Given'][0]
                    spouse_full_name = spouse_full_name + ', ' + spouseDict['Given'][0]
                else:
                    person_id = person_id + spouseDict['Given'][given_num]
                    spouse_full_name = spouse_full_name + ' ' + spouseDict['Given'][given_num][0]
            person_id = person_id + spouseDict['BirthYear']
            person_id = person_id.replace('.','')
            print( 'spouse name = ', spouse_full_name, '   person_id = ', person_id)

            # build spouse pictures list
            conDummyPic = conDummyFemalePic
            if os.path.isfile(folders_path + '/' + person_id + '.jpg'):
                strSpousePicList[intSpouseNum] = strTDCenter + conClose + conImageSrc + "\"" + "../" +\
                                                 person_id + "/" + person_id\
                                                 + '.jpg' + "\"" + strWidth + conClose + conSlashTD
            else:
                strSpousePicList[intSpouseNum]=strTDCenter + conClose + conImageSrc + "\"" + conDummyPic +\
                                                "\"" + strWidth + conClose + conSlashTD

            blnHref = 1 if len(spouseDict) > 0 else 0    # the folder exists for the spouse

            # build spouse fule names list
            blnName = 1 if len(spouse_full_name) > 0 else 0

            if blnName :
                strSpouseNameList.append(strTDCenter + conClose + conNameFmt + spouse_full_name\
                                         + conNameFmtClose + conAEnd + conSlashTD)
                if blnHref :
                    strSpouseNameList[intSpouseNum] = strTDCenter + conClose + conHref + "\"" + "../" +\
                                             person_id + "/index.html" + "\"" + conClose\
                                             + conNameFmt + spouse_full_name + conNameFmtClose +\
                                             conAEnd + conSlashTD
                    strSpouseLinkList.append(strTDCenter + conClose + con3Space + conHref + "\"" + "../" +\
                                             person_id + conHGlass + conClose + conImageSrc\
                                             + strSpouseArrow + conClose + conAEnd + conSlashTD)
                else:
                    strSpouseLinkList.append(strTDCenter + conClose + conSlashTD)

            else:
                strSpouseNameList.append(strTDCenter + conClose + conNameFmt + spouse_full_name +\
                                         conNameFmtClose + conSlashTD)

    # end of spouses

    #Body
        hourglasshtmlList.append("<TABLE border=" + "\"" + "0" + "\"" + " cellspacing=" + "\"" + "0" + "\"" + " cellpadding=" + "\"" + "0" + "\"" + " align=" + "\"" + "center" + "\"" + ">")

    #1st Row - sets the column widths - columns 1 thru 9 (0 through 8)
        strHTMLBody = []
        strHTMLBody.append(strTDCenter + conClose + strParentHd + conSlashTD + "\n")
        strHTMLBody.append(strTDCenter + conClose + con6Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + con3Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + con6Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + "<h2>Parents</h2>" + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + con6Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + con3Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + con6Space + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + "<h2>Children</h2>" + conSlashTD)

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add first row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #2nd Row - father and 1st child photos
        strHTMLBody = []
        intChild = 0
        strHTMLBody.append(strFatherPic)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strChildPicList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add second row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #3rd Row - father and 1st child names
        strHTMLBody = []

        strHTMLBody.append(strFatherName)
        strHTMLBody.append(strF32)
        strHTMLBody.append(strF33)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        if blnChildExists[intChild]:
            strHTMLBody.append(strTDCenter + strColor + conClose + conSlashTD)
            strHTMLBody.append(strChildLinkList[intChild])
        else :
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        strHTMLBody.append(strChildNameList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add third row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #4th Row - self and 2nd child photos
        strHTMLBody = []
        intChild = intChild + 1
        print('intChild = ', intChild, 'len(strChildPicList) = ', len(strChildPicList))
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strF43)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strSelfPic)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        if blnChildExists[intChild]:
            strHTMLBody.append(strTDCenter + strColor + conClose + conSlashTD)
        else:
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        if intChild <= len(strChildPicList) - 1:
            strHTMLBody.append(strChildPicList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add fourth row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #5th Row - self and 2nd child names
        strHTMLBody = []
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strFM53)
        strHTMLBody.append(strFM54)
        strHTMLBody.append(strSelfName)
        if blnChildExists[intChild]:
            strHTMLBody.append(strTDCenter + strColor + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + strColor + conClose + conSlashTD)
        else :
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        strHTMLBody.append(strC2_58)
        if intChild <= len(strChildPicList) - 1:
            strHTMLBody.append(strChildNameList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add fifth row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #6th Row - Mother, 1st Spouse, and 3rd child photo
        strHTMLBody = []
        intSpouse = 0
        intChild = intChild + 1
        strHTMLBody.append(strMotherPic)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strM63)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strSpousePicList[intSpouse])
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        if intChild <= len(strChildPicList) - 1:
            strHTMLBody.append(strPic7[intChild])
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        if intChild <= len(strChildPicList) - 1:
            strHTMLBody.append(strChildPicList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add sixth row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #7th Row - Mother, 1st Spouse, and 3rd child names
        strHTMLBody = []
        strHTMLBody.append(strMotherName)
        strHTMLBody.append(strM72)
        strHTMLBody.append(strM73)
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)
        strHTMLBody.append(strSpouseNameList[intSpouse])
        strHTMLBody.append(strTDCenter + conClose + conSlashTD)

        if intChild <= len(strChildPicList) - 1:
            strHTMLBody.append(strName7[intChild])
            strHTMLBody.append(strName8[intChild])
            strHTMLBody.append(strChildNameList[intChild])

        hourglasshtmlList.append(conTR)
        hourglasshtmlList.append(strHTMLBody)  #add seventh row to the body of the web page
        hourglasshtmlList.append(conSlashTR)

    #8th+ Row - 2nd Spouse through intSpouseCnt, and 4th child through intChildCnt+2
        strHTMLBody = []
        for intSpouseNum in range(1,spouseNum-1):
            intChild = intChild + 1

            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strSpousePicList[intSpouseNum])
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            if intChild <= (len(strPic7) - 1) :
                strHTMLBody.append(strPic7[intChild])

            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            if intChild <= (len(strChildPicList) - 1) :
                strHTMLBody.append(strChildPicList[intChild])

            hourglasshtmlList.append(conTR)
            hourglasshtmlList.append(strHTMLBody)  #add row to the body of the web page
            hourglasshtmlList.append(conSlashTR)


    #9th Row - 2nd Spouse, and 4th child names
            strHTMLBody = []

            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strSpouseNameList[intSpouse])
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            if intChild <= (len(strName7) - 1) :
                strHTMLBody.append(strName7[intChild])

            if intChild <= (len(strName8) - 1) :
                strHTMLBody.append(strName8[intChild])

            if intChild <= (len(strChildNameList) - 1) :
                strHTMLBody.append(strChildNameList[intChild])

            hourglasshtmlList.append(conTR)
            hourglasshtmlList.append(strHTMLBody)  #add next rows to the body of the web page
            hourglasshtmlList.append(conSlashTR)

    #Row - intChild child through intChildCnt
        strHTMLBody = []

        for intChild in range(intChild, childNum - 1) :
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strPic7[intChild])
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strChildPic[intChild])

            hourglasshtmlList.append(conTR)
            hourglasshtmlList.append(strHTMLBody)  #add row to the body of the web page
            hourglasshtmlList.append(conSlashTR)

    #Row - child names
            strHTMLBody = []
            intRow = intRow + 1
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strTDCenter + conClose + conSlashTD)
            strHTMLBody.append(strName7[intChild])
            strHTMLBody.append(strName8[intChild])
            strHTMLBody.append(strChildName[intChild])

            hourglasshtmlList.append(conTR)
            hourglasshtmlList.append(strHTMLBody)  #add next rows to the body of the web page
            hourglasshtmlList.append(conSlashTR)



        for row in hourglasshtmlList:
            hourglassFile.writelines(row)

        return hourglasshtmlList


def main():
    # Get the RootsMagic database info
    rmagicPath = 'C:\\Dropbox\\Apps\\RootsMagic\\myfamily.rmgc'
    #rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    build_web = build_web_pages(rmagicPath)
    build_web.__init__


if __name__ == '__main__':
    main()
