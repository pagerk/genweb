#------------------------------------------------------------------------------
# Name:        famhist_person_entry
# Purpose:
#
# Author:      pagerk
#
# Created:     14/10/2013
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk
from datetime import *
import sys
import pprint
sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts')
sys.path.append('C:/Users/pagerk/PyScripter_Workspace/Python3Scripts/MyLib')
import os
import string
from file_folder_ops import get_folders_in_folder
from file_ops import separate_strings_on_char
from build_family_from_rm import *

# Get the RootsMagic database info
rm_db = 'C:\\Dropbox\\RootsMagic Database\\myfamily.rmgc'
global tables
tables = fetch_rm_tables(rm_db)

person_folders_path = \
    'D:\Family History\Family History CD\Research\Individual_Web_Pages_Copy'


def search_for_matches(*args):
    global persons
    given_name_value = str(srch_person["Given"].get())
    surname_value = str(srch_person["Surname"].get())
    birthyear_value = str(srch_person["BirthYear"].get())

    name_dict = {'Surname': surname_value, 'Given': given_name_value,
                 'BirthYear': birthyear_value}

    persons = fetch_person_from_fuzzy_name(tables['NameTable'], name_dict)

    # Labels for found persons
    for number in range(5):
        if number <= len(persons)-1:
            namestring = ''
            for names in persons[number]["Given"]:
                if namestring == '':
                    namestring = names
                else:
                    namestring = namestring + ' ' + names[0]
            match[number]["Given"].set(str(namestring))
            match[number]["Surname"].set(str(persons[number]["Surname"]))
            match[number]["BirthYear"].set(str(persons[number]["BirthYear"]))


def view_possible_person(*args):
    import pprint
    global person_no

    # identify the target person
    person_no = int(selected_person.get())

    # Clear the possible person table
    for person in range(22):
        for category in tgt_family[person]:
            tgt_family[person][category].set('-')

    namestring = ''
    for names in persons[person_no]["Given"]:
        if namestring == '':
            namestring = names
        else:
            namestring = namestring + ' ' + names[0]
    target = 0
    tgt_family[target]["Given"].set(str(namestring))
    tgt_family[target]["Surname"].set(str(persons[person_no]["Surname"]))
    tgt_family[target]["BirthYear"].set(str(persons[person_no]["BirthYear"]))
    tgt_family[target]["DeathYear"].set(str(persons[person_no]["DeathYear"]))
    tgt_family[target]["ID"].set(str(persons[person_no]["OwnerID"]))

    #{'NameTable':name_table,'PersonTable':person_table,
    # 'ChildTable':child_table, 'FamilyTable':family_table}

    parents = fetch_parents_from_ID(tables['PersonTable'], tables['NameTable'],
                                    tables['FamilyTable'],
                                    persons[person_no]['OwnerID'])

    namestring = ''
    for names in parents['Father']["Given"]:
        if namestring == '':
            namestring = names
        else:
            namestring = namestring + ' ' + names[0]
    father = 1
    tgt_family[father]["Given"].set(str(namestring))
    tgt_family[father]["Surname"].set(str(parents['Father']["Surname"]))
    tgt_family[father]["BirthYear"].set(str(parents['Father']["BirthYear"]))
    tgt_family[father]["DeathYear"].set(str(parents['Father']["DeathYear"]))
    tgt_family[father]["ID"].set(str(parents['Father']["OwnerID"]))

    namestring = ''
    for names in parents['Mother']["Given"]:
        if namestring == '':
            namestring = names
        else:
            namestring = namestring + ' ' + names[0]
    mother = 2
    tgt_family[mother]["Given"].set(str(namestring))
    tgt_family[mother]["Surname"].set(str(parents['Mother']["Surname"]))
    tgt_family[mother]["BirthYear"].set(str(parents['Mother']["BirthYear"]))
    tgt_family[mother]["DeathYear"].set(str(parents['Mother']["DeathYear"]))
    tgt_family[mother]["ID"].set(str(parents['Mother']["OwnerID"]))

    spouses = fetch_spouses_from_ID(tables['NameTable'], tables['PersonTable'],
                                    tables['FamilyTable'],
                                    persons[person_no]['OwnerID'])

    for spouse_no in range(len(spouses)):
        namestring = ''
        for names in spouses[spouse_no]["Given"]:
            if namestring == '':
                namestring = names
            else:
                namestring = namestring + ' ' + names[0]
        fam_spouses = 3
        tgt_family[fam_spouses+spouse_no]["Given"].\
            set(str(namestring))
        tgt_family[fam_spouses+spouse_no]["Surname"].\
            set(str(spouses[spouse_no]["Surname"]))
        tgt_family[fam_spouses+spouse_no]["BirthYear"].\
            set(str(spouses[spouse_no]["BirthYear"]))
        tgt_family[fam_spouses+spouse_no]["DeathYear"].\
            set(str(spouses[spouse_no]["DeathYear"]))
        tgt_family[fam_spouses+spouse_no]["ID"].\
            set(str(spouses[spouse_no]["OwnerID"]))

    children = fetch_children_from_ID(tables['ChildTable'],
                                      tables['NameTable'],
                                      tables['PersonTable'],
                                      tables['FamilyTable'],
                                      persons[person_no]['OwnerID'])

    for child_no in range(len(children)):
        namestring = ''
        for names in children[child_no]["Given"]:
            if namestring == '':
                namestring = names
            else:
                namestring = namestring + ' ' + names[0]
        fam_children = 7
        tgt_family[fam_children+child_no]["Given"].\
            set(str(namestring))
        tgt_family[fam_children+child_no]["Surname"].\
            set(str(children[child_no]["Surname"]))
        tgt_family[fam_children+child_no]["BirthYear"].\
            set(str(children[child_no]["BirthYear"]))
        tgt_family[fam_children+child_no]["DeathYear"].\
            set(str(children[child_no]["DeathYear"]))
        tgt_family[fam_children+child_no]["ID"].\
            set(str(children[child_no]["OwnerID"]))


def build_image_ref(*args):
    for target_person in chk_incld:
        pass


def add_to_people_ref(*args):
    pass


def build_ext_html():
    pass


def build_inline_txt(*args):
    # Set the file generation labels
    file_gen["Header"].set('Inline Text')
    file_gen["Artifact_ID_Label"].set('ID	YYYYMMDD##')
    file_gen["Artifact_Title_Label"].set('Title')
    file_gen["Artifact_Caption_Label"].set('Caption')

    # Only display the people who have been selected
    ppl_ref = 0
    for ref in range(len(tgt_family)):
        if str(tgt_family[ref]["Check"].get()) == 'yes':
            ppl[ppl_ref]["Given"].\
                set(str(tgt_family[ref]["Given"].get()))
            ppl[ppl_ref]["Surname"].\
                set(str(tgt_family[ref]["Surname"].get()))
            ppl[ppl_ref]["BirthYear"].\
                set(str(tgt_family[ref]["BirthYear"].get()))
            ppl[ppl_ref]["DeathYear"].\
                set(str(tgt_family[ref]["DeathYear"].get()))
            ppl[ppl_ref]["ID"].\
                set(str(tgt_family[ref]["ID"].get()))
            ppl_ref += 1
    for ppl_ref in range(ppl_ref,len(tgt_family)):
            ppl[ppl_ref]["Given"].set('-')
            ppl[ppl_ref]["Surname"].set('-')
            ppl[ppl_ref]["BirthYear"].set('-')
            ppl[ppl_ref]["DeathYear"].set('-')
            ppl[ppl_ref]["ID"].set('-')


def create_entry(*args):
    pass

if __name__ == '__main__':
    root = Tk()
    root.title("Family History: Enter a Person")

    style = ttk.Style()
    style.theme_use("vista")

    mainframe = ttk.Frame(root, borderwidth=5, relief="sunken", width=200,
                          height=100, padding="12 12 12 12")

    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    #Search boxes
    srch_person = {}
    srch_person["Given"] = StringVar()
    srch_person["Given"].set("")

    srch_person["Surname"] = StringVar("")
    srch_person["Surname"].set("")

    srch_person["BirthYear"] = StringVar()
    srch_person["BirthYear"].set('YYYY')


    # Found person labels
    match = []
    for m_no in range(6):
        match.append({"Given": StringVar(),
                        "Surname": StringVar(),
                        "BirthYear": StringVar()})
        for f in match[m_no]:
            match[m_no][f].set('-')

    # Radiobutton person selector
    selected_person = StringVar()

    # Target family labels
    # checkbox include person - the variable is set to 1 if the button is
    # selected, and 0 otherwise.
    tgt_family = []
    for tf_no in range(22):
        tgt_family.append({"Check": StringVar(),
                           "Given": StringVar(),
                           "Surname": StringVar(),
                           "BirthYear": StringVar(),
                           "DeathYear": StringVar(),
                           "ID": StringVar()})
        tgt_family[tf_no]["Given"].set('-')
        tgt_family[tf_no]["Surname"].set('-')
        tgt_family[tf_no]["BirthYear"].set('-')
        tgt_family[tf_no]["DeathYear"].set('-')
        tgt_family[tf_no]["ID"].set('-')


    # target person - tgt_family index = 0
    # father of target - tgt_family index = 1
    # mother of target - tgt_family index = 2
    # spouses of target - tgt_family index = 3-6
    # children of target - tgt_family index = 7-21

    # set up the people referenced table
    ppl = []
    for ppl_no in range(26):
        ppl.append({"Check": StringVar(),
                    "Given": StringVar(),
                    "Surname": StringVar(),
                    "BirthYear": StringVar(),
                    "DeathYear": StringVar(),
                    "ID": StringVar()})
        ppl[ppl_no]["Given"].set('-')
        ppl[ppl_no]["Surname"].set('-')
        ppl[ppl_no]["BirthYear"].set('-')
        ppl[ppl_no]["DeathYear"].set('-')
        ppl[ppl_no]["ID"].set('-')

    # File Generation labels
    file_gen = {}
    file_gen["Header"] = StringVar()
    file_gen["Artifact_ID_Label"] = StringVar()
    file_gen["Artifact_ID"] = StringVar()
    file_gen["Artifact_Title_Label"] = StringVar()
    file_gen["Artifact_Title"] = StringVar()
    file_gen["Artifact_Caption_Label"] = StringVar()
    file_gen["Artifact_Caption"] = StringVar()

#---------------------------

    # Define the rows
    current_row = 1
    ttk.Label(mainframe, text="1st Given Name").\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Surname   ").\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Birth").\
        grid(column=5, row=current_row, sticky=EW)
    colmSep1 = ttk.Separator(mainframe, orient=VERTICAL)
    colmSep1.grid(column=8, row=current_row, rowspan="35", sticky="ns")
    colmSep2 = ttk.Separator(mainframe, orient=VERTICAL)
    colmSep2.grid(column=9, row=current_row, rowspan="35", sticky="ns")
    ttk.Label(mainframe, textvariable=file_gen["Header"]).\
        grid(column=11, row=current_row, sticky=EW, columnspan=5)

    current_row = 2
    ttk.Button(mainframe, text="Search", command=search_for_matches).\
        grid(column=1, row=2, sticky=W, columnspan=1, rowspan=1)
    ttk.Entry(mainframe, width=7, textvariable=srch_person["Given"]).\
        grid(column=3, row=current_row, sticky=(W, E), columnspan=1)
    ttk.Entry(mainframe, width=7, textvariable=srch_person["Surname"]).\
        grid(column=4, row=current_row, sticky=(W, E), columnspan=1)
    ttk.Entry(mainframe, width=7, textvariable=srch_person["BirthYear"]).\
            grid(column=5, row=current_row, sticky=(W, E), columnspan=1)

    current_row = 3
    titleSep1 = ttk.Separator(mainframe, orient=HORIZONTAL)
    titleSep1.grid(column=0, row=current_row, columnspan="16", sticky="we")

    current_row = 4
    ttk.Button(mainframe, text="View\nPossible\nMatch",
               command=view_possible_person).\
        grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='0').\
        grid(column=2, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[0]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[0]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[0]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=file_gen["Artifact_ID_Label"]).\
        grid(column=10, row=current_row, sticky=EW, columnspan=2)
    ttk.Entry(mainframe, width=7, textvariable=file_gen["Artifact_ID"]).\
            grid(column=12, row=current_row, sticky=(W, E), columnspan=3)

    current_row = 5
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='1').\
        grid(column=2, row=5, sticky=EW)
    ttk.Label(mainframe, textvariable=match[1]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[1]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[1]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=file_gen["Artifact_Title_Label"]).\
        grid(column=10, row=current_row, sticky=EW)
    ttk.Entry(mainframe, width=7, textvariable=file_gen["Artifact_Title"]).\
            grid(column=11, row=current_row, sticky=(W, E), columnspan=6)

    current_row = 6
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='2').\
        grid(column=2, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[2]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[2]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[2]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=file_gen["Artifact_Caption_Label"]).\
        grid(column=10, row=current_row, sticky=EW)
    ttk.Entry(mainframe, width=7, textvariable=file_gen["Artifact_Caption"]).\
        grid(column=11, row=current_row, sticky=(W, E),
            columnspan=6, rowspan=1)

    current_row = 7
    ttk.Button(mainframe, text="Add to\nPeople\nReferenced",
               command=add_to_people_ref).\
        grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='3').\
        grid(column=2, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[3]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[3]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[3]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)

    current_row = 8
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='4').\
        grid(column=2, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[4]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[4]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[4]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)

    current_row = 9
    ttk.Radiobutton(mainframe, text='', variable=selected_person, value='5').\
        grid(column=2, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[5]["Given"]).\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[5]["Surname"]).\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, textvariable=match[5]["BirthYear"]).\
        grid(column=5, row=current_row, sticky=EW)

    current_row = 10
    titleSep2 = ttk.Separator(mainframe, orient=HORIZONTAL)
    titleSep2.grid(column=0, row=current_row, columnspan="8", sticky="we")
    ttk.Label(mainframe, text="Given Names").\
        grid(column=11, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Surname").\
        grid(column=12, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Birth").\
        grid(column=13, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Death").\
        grid(column=14, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="ID#").\
        grid(column=15, row=current_row, sticky=EW)

    current_row = 11
    ttk.Label(mainframe, text="Matching Person Details").\
        grid(column=3, row=current_row, columnspan="3", sticky=EW)
    ttk.Label(mainframe, text="People").\
        grid(column=10, row=current_row, sticky=EW)

    current_row = 12
    ttk.Label(mainframe, text="Given Names").\
        grid(column=3, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Surname").\
        grid(column=4, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Birth").\
        grid(column=5, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Death").\
        grid(column=6, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="ID#").\
        grid(column=7, row=current_row, sticky=EW)
    ttk.Label(mainframe, text="Referenced").\
        grid(column=10, row=current_row, sticky=EW)

    current_row = 13
    ttk.Label(mainframe, text="Target").\
        grid(column=1, row=current_row, sticky=EW)

    for current_row in range(13,35):
        ttk.Checkbutton(mainframe,
            variable=tgt_family[current_row-13]["Check"],
            onvalue="yes", offvalue="no").\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=tgt_family[current_row-13]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=tgt_family[current_row-13]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=tgt_family[current_row-13]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=tgt_family[current_row-13]["DeathYear"]).\
            grid(column=6, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=tgt_family[current_row-13]["ID"]).\
            grid(column=7, row=current_row, sticky=EW)

    for current_row in range(11,37):
        ttk.Label(mainframe,
            textvariable=ppl[current_row-11]["Given"]).\
            grid(column=11, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=ppl[current_row-11]["Surname"]).\
            grid(column=12, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=ppl[current_row-11]["BirthYear"]).\
            grid(column=13, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=ppl[current_row-11]["DeathYear"]).\
            grid(column=14, row=current_row, sticky=EW)
        ttk.Label(mainframe,
            textvariable=ppl[current_row-11]["ID"]).\
            grid(column=15, row=current_row, sticky=EW)

    current_row = 14
    ttk.Label(mainframe, text="Father").\
        grid(column=1, row=current_row, sticky=EW)

    current_row = 15
    ttk.Label(mainframe, text="Mother").\
        grid(column=1, row=current_row, sticky=EW)

    current_row = 16
    ttk.Label(mainframe, text="Spouses").\
        grid(column=1, row=current_row, sticky=EW)

    current_row = 20
    ttk.Label(mainframe, text="Children").\
        grid(column=1, row=current_row, sticky=EW)

    current_row = 35
    titleSep3 = ttk.Separator(mainframe, orient=HORIZONTAL)
    titleSep3.grid(column=0, row=current_row, columnspan="8", sticky="we")

    current_row = 36
    ttk.Label(mainframe, text="Create file to add:").\
        grid(column=3, row=current_row, columnspan="3", sticky=EW)

    current_row = 37
    ttk.Button(mainframe, text="Image\nReference", command=build_image_ref).\
        grid(column=3, row=current_row, sticky=W,
             columnspan=1, rowspan=1)
    ttk.Button(mainframe, text="Inline\nText", command=build_inline_txt).\
        grid(column=4, row=current_row, sticky=W,
             columnspan=1, rowspan=1)
    ttk.Button(mainframe, text="External\nhtml", command=build_ext_html).\
        grid(column=5, row=current_row, sticky=W,
             columnspan=1, rowspan=1)

    current_row = 38

#----------------------------------------------

    for child in mainframe.winfo_children():
        child.grid_configure(padx=2, pady=2)

    root.mainloop()
