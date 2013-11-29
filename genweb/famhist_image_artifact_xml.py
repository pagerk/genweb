#!/usr/bin/env python3
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
import os
from tkinter import *
from tkinter import ttk
import logging

from genweb import build_family_from_rm


_moduleLogger = logging.getLogger(__name__)


class Editor(object):

    def __init__(self, rmagicPath):
        self._rmagicPath = rmagicPath
        self._tables = build_family_from_rm.fetch_rm_tables(self._rmagicPath)

        self._persons = None

        self._root = Tk()
        self._root.title("Family History: Enter a Person")

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except Exception:
            _moduleLogger.debug("Theme unsupported")

        mainframe = ttk.Frame(self._root, borderwidth=5, relief="sunken", width=200,
                            height=100, padding="12 12 12 12")

        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        #Search boxes
        self._srch_person = {}
        self._srch_person["Given"] = StringVar()
        self._srch_person["Given"].set("")

        self._srch_person["Surname"] = StringVar("")
        self._srch_person["Surname"].set("")

        self._srch_person["BirthYear"] = StringVar()
        self._srch_person["BirthYear"].set('YYYY')


        # Found person labels
        match = []
        for m_no in range(6):
            match.append({"Given": StringVar(),
                            "Surname": StringVar(),
                            "BirthYear": StringVar()})
            for f in match[m_no]:
                match[m_no][f].set('-')

        # Radiobutton person selector
        self._selected_person = StringVar()

        # Target family labels
        # checkbox include person - the variable is set to 1 if the button is
        # selected, and 0 otherwise.
        self._tgt_family = []
        for tf_no in range(22):
            self._tgt_family.append({"Check": StringVar(),
                            "Given": StringVar(),
                            "Surname": StringVar(),
                            "BirthYear": StringVar(),
                            "DeathYear": StringVar(),
                            "ID": StringVar()})
            self._tgt_family[tf_no]["Given"].set('-')
            self._tgt_family[tf_no]["Surname"].set('-')
            self._tgt_family[tf_no]["BirthYear"].set('-')
            self._tgt_family[tf_no]["DeathYear"].set('-')
            self._tgt_family[tf_no]["ID"].set('-')


        # target person - self._tgt_family index = 0
        # father of target - self._tgt_family index = 1
        # mother of target - self._tgt_family index = 2
        # spouses of target - self._tgt_family index = 3-6
        # children of target - self._tgt_family index = 7-21

        # set up the people referenced table
        self._ppl = []
        for ppl_no in range(26):
            self._ppl.append({"Check": StringVar(),
                        "Given": StringVar(),
                        "Surname": StringVar(),
                        "BirthYear": StringVar(),
                        "DeathYear": StringVar(),
                        "ID": StringVar()})
            self._ppl[ppl_no]["Given"].set('-')
            self._ppl[ppl_no]["Surname"].set('-')
            self._ppl[ppl_no]["BirthYear"].set('-')
            self._ppl[ppl_no]["DeathYear"].set('-')
            self._ppl[ppl_no]["ID"].set('-')

        # File Generation labels
        self._file_gen = {}
        self._file_gen["Header"] = StringVar()
        self._file_gen["Artifact_ID_Label"] = StringVar()
        self._file_gen["Artifact_ID"] = StringVar()
        self._file_gen["Artifact_Title_Label"] = StringVar()
        self._file_gen["Artifact_Title"] = StringVar()
        self._file_gen["Artifact_Caption_Label"] = StringVar()
        self._file_gen["Artifact_Caption"] = StringVar()

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
        ttk.Label(mainframe, textvariable=self._file_gen["Header"]).\
            grid(column=11, row=current_row, sticky=EW, columnspan=5)

        current_row = 2
        ttk.Button(mainframe, text="Search", command=self._on_search_for_matches).\
            grid(column=1, row=2, sticky=W, columnspan=1, rowspan=1)
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["Given"]).\
            grid(column=3, row=current_row, sticky=(W, E), columnspan=1)
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["Surname"]).\
            grid(column=4, row=current_row, sticky=(W, E), columnspan=1)
        ttk.Entry(mainframe, width=7, textvariable=self._srch_person["BirthYear"]).\
                grid(column=5, row=current_row, sticky=(W, E), columnspan=1)

        current_row = 3
        titleSep1 = ttk.Separator(mainframe, orient=HORIZONTAL)
        titleSep1.grid(column=0, row=current_row, columnspan="16", sticky="we")

        current_row = 4
        ttk.Button(mainframe, text="View\nPossible\nMatch",
                command=self._on_view_possible_person).\
            grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='0').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[0]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[0]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[0]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_ID_Label"]).\
            grid(column=10, row=current_row, sticky=EW, columnspan=2)
        ttk.Entry(mainframe, width=7, textvariable=self._file_gen["Artifact_ID"]).\
                grid(column=12, row=current_row, sticky=(W, E), columnspan=3)

        current_row = 5
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='1').\
            grid(column=2, row=5, sticky=EW)
        ttk.Label(mainframe, textvariable=match[1]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[1]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[1]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Title_Label"]).\
            grid(column=10, row=current_row, sticky=EW)
        ttk.Entry(mainframe, width=7, textvariable=self._file_gen["Artifact_Title"]).\
                grid(column=11, row=current_row, sticky=(W, E), columnspan=6)

        current_row = 6
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='2').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[2]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[2]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[2]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Caption_Label"]).\
            grid(column=10, row=current_row, sticky=EW)
        ttk.Entry(mainframe, width=7, textvariable=self._file_gen["Artifact_Caption"]).\
            grid(column=11, row=current_row, sticky=(W, E),
                columnspan=6, rowspan=1)

        current_row = 7
        ttk.Button(mainframe, text="Add to\nPeople\nReferenced",
                command=self._on_add_to_people_ref).\
            grid(column=1, row=current_row, sticky=W, columnspan=1, rowspan=3)
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='3').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[3]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[3]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[3]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)

        current_row = 8
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='4').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[4]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[4]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=match[4]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)

        current_row = 9
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='5').\
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
                variable=self._tgt_family[current_row-13]["Check"],
                onvalue="yes", offvalue="no").\
                grid(column=2, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._tgt_family[current_row-13]["Given"]).\
                grid(column=3, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._tgt_family[current_row-13]["Surname"]).\
                grid(column=4, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._tgt_family[current_row-13]["BirthYear"]).\
                grid(column=5, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._tgt_family[current_row-13]["DeathYear"]).\
                grid(column=6, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._tgt_family[current_row-13]["ID"]).\
                grid(column=7, row=current_row, sticky=EW)

        for current_row in range(11,37):
            ttk.Label(mainframe,
                textvariable=self._ppl[current_row-11]["Given"]).\
                grid(column=11, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._ppl[current_row-11]["Surname"]).\
                grid(column=12, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._ppl[current_row-11]["BirthYear"]).\
                grid(column=13, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._ppl[current_row-11]["DeathYear"]).\
                grid(column=14, row=current_row, sticky=EW)
            ttk.Label(mainframe,
                textvariable=self._ppl[current_row-11]["ID"]).\
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
        ttk.Button(mainframe, text="Image\nReference", command=self._on_build_image_ref).\
            grid(column=3, row=current_row, sticky=W,
                columnspan=1, rowspan=1)
        ttk.Button(mainframe, text="Inline\nText", command=self._on_build_inline_txt).\
            grid(column=4, row=current_row, sticky=W,
                columnspan=1, rowspan=1)
        ttk.Button(mainframe, text="External\nhtml", command=self._on_build_ext_html).\
            grid(column=5, row=current_row, sticky=W,
                columnspan=1, rowspan=1)

        current_row = 38

        for child in mainframe.winfo_children():
            child.grid_configure(padx=2, pady=2)

    def mainloop(self):
        self._root.mainloop()

    def _on_search_for_matches(self, *args):
        given_name_value = str(self._srch_person["Given"].get())
        surname_value = str(self._srch_person["Surname"].get())
        birthyear_value = str(self._srch_person["BirthYear"].get())

        name_dict = {'Surname': surname_value, 'Given': given_name_value,
                    'BirthYear': birthyear_value}

        self._persons = build_family_from_rm.fetch_person_from_fuzzy_name(self._tables['NameTable'], name_dict)

        # Labels for found persons
        for number in range(5):
            if number <= len(self._persons)-1:
                namestring = ''
                for names in self._persons[number]["Given"]:
                    if namestring == '':
                        namestring = names
                    else:
                        namestring = namestring + ' ' + names[0]
                match[number]["Given"].set(str(namestring))
                match[number]["Surname"].set(str(self._persons[number]["Surname"]))
                match[number]["BirthYear"].set(str(self._persons[number]["BirthYear"]))

    def _on_view_possible_person(self, *args):
        # identify the target person
        person_no = int(self._selected_person.get())

        # Clear the possible person table
        for person in range(22):
            for category in self._tgt_family[person]:
                self._tgt_family[person][category].set('-')

        namestring = ''
        for names in self._persons[person_no]["Given"]:
            if namestring == '':
                namestring = names
            else:
                namestring = namestring + ' ' + names[0]
        target = 0
        self._tgt_family[target]["Given"].set(str(namestring))
        self._tgt_family[target]["Surname"].set(str(self._persons[person_no]["Surname"]))
        self._tgt_family[target]["BirthYear"].set(str(self._persons[person_no]["BirthYear"]))
        self._tgt_family[target]["DeathYear"].set(str(self._persons[person_no]["DeathYear"]))
        self._tgt_family[target]["ID"].set(str(self._persons[person_no]["OwnerID"]))

        #{'NameTable':name_table,'PersonTable':person_table,
        # 'ChildTable':child_table, 'FamilyTable':family_table}

        parents = build_family_from_rm.fetch_parents_from_ID(self._tables['PersonTable'], self._tables['NameTable'],
                                        self._tables['FamilyTable'],
                                        self._persons[person_no]['OwnerID'])

        namestring = ''
        for names in parents['Father']["Given"]:
            if namestring == '':
                namestring = names
            else:
                namestring = namestring + ' ' + names[0]
        father = 1
        self._tgt_family[father]["Given"].set(str(namestring))
        self._tgt_family[father]["Surname"].set(str(parents['Father']["Surname"]))
        self._tgt_family[father]["BirthYear"].set(str(parents['Father']["BirthYear"]))
        self._tgt_family[father]["DeathYear"].set(str(parents['Father']["DeathYear"]))
        self._tgt_family[father]["ID"].set(str(parents['Father']["OwnerID"]))

        namestring = ''
        for names in parents['Mother']["Given"]:
            if namestring == '':
                namestring = names
            else:
                namestring = namestring + ' ' + names[0]
        mother = 2
        self._tgt_family[mother]["Given"].set(str(namestring))
        self._tgt_family[mother]["Surname"].set(str(parents['Mother']["Surname"]))
        self._tgt_family[mother]["BirthYear"].set(str(parents['Mother']["BirthYear"]))
        self._tgt_family[mother]["DeathYear"].set(str(parents['Mother']["DeathYear"]))
        self._tgt_family[mother]["ID"].set(str(parents['Mother']["OwnerID"]))

        spouses = build_family_from_rm.fetch_spouses_from_ID(self._tables['NameTable'], self._tables['PersonTable'],
                                        self._tables['FamilyTable'],
                                        self._persons[person_no]['OwnerID'])

        for spouse_no in range(len(spouses)):
            namestring = ''
            for names in spouses[spouse_no]["Given"]:
                if namestring == '':
                    namestring = names
                else:
                    namestring = namestring + ' ' + names[0]
            fam_spouses = 3
            self._tgt_family[fam_spouses+spouse_no]["Given"].\
                set(str(namestring))
            self._tgt_family[fam_spouses+spouse_no]["Surname"].\
                set(str(spouses[spouse_no]["Surname"]))
            self._tgt_family[fam_spouses+spouse_no]["BirthYear"].\
                set(str(spouses[spouse_no]["BirthYear"]))
            self._tgt_family[fam_spouses+spouse_no]["DeathYear"].\
                set(str(spouses[spouse_no]["DeathYear"]))
            self._tgt_family[fam_spouses+spouse_no]["ID"].\
                set(str(spouses[spouse_no]["OwnerID"]))

        children = build_family_from_rm.fetch_children_from_ID(self._tables['ChildTable'],
                                        self._tables['NameTable'],
                                        self._tables['PersonTable'],
                                        self._tables['FamilyTable'],
                                        self._persons[person_no]['OwnerID'])

        for child_no in range(len(children)):
            namestring = ''
            for names in children[child_no]["Given"]:
                if namestring == '':
                    namestring = names
                else:
                    namestring = namestring + ' ' + names[0]
            fam_children = 7
            self._tgt_family[fam_children+child_no]["Given"].\
                set(str(namestring))
            self._tgt_family[fam_children+child_no]["Surname"].\
                set(str(children[child_no]["Surname"]))
            self._tgt_family[fam_children+child_no]["BirthYear"].\
                set(str(children[child_no]["BirthYear"]))
            self._tgt_family[fam_children+child_no]["DeathYear"].\
                set(str(children[child_no]["DeathYear"]))
            self._tgt_family[fam_children+child_no]["ID"].\
                set(str(children[child_no]["OwnerID"]))


    def _on_build_image_ref(self, *args):
        raise NotImplementedError("TODO")


    def _on_add_to_people_ref(self, *args):
        raise NotImplementedError("TODO")


    def _on_build_ext_html():
        raise NotImplementedError("TODO")


    def _on_build_inline_txt(*args):
        # Set the file generation labels
        self._file_gen["Header"].set('Inline Text')
        self._file_gen["Artifact_ID_Label"].set('ID	YYYYMMDD##')
        self._file_gen["Artifact_Title_Label"].set('Title')
        self._file_gen["Artifact_Caption_Label"].set('Caption')

        # Only display the people who have been selected
        ppl_ref = 0
        for ref in range(len(self._tgt_family)):
            if str(self._tgt_family[ref]["Check"].get()) == 'yes':
                self._ppl[ppl_ref]["Given"].\
                    set(str(self._tgt_family[ref]["Given"].get()))
                self._ppl[ppl_ref]["Surname"].\
                    set(str(self._tgt_family[ref]["Surname"].get()))
                self._ppl[ppl_ref]["BirthYear"].\
                    set(str(self._tgt_family[ref]["BirthYear"].get()))
                self._ppl[ppl_ref]["DeathYear"].\
                    set(str(self._tgt_family[ref]["DeathYear"].get()))
                self._ppl[ppl_ref]["ID"].\
                    set(str(self._tgt_family[ref]["ID"].get()))
                ppl_ref += 1
        for ppl_ref in range(ppl_ref,len(self._tgt_family)):
                self._ppl[ppl_ref]["Given"].set('-')
                self._ppl[ppl_ref]["Surname"].set('-')
                self._ppl[ppl_ref]["BirthYear"].set('-')
                self._ppl[ppl_ref]["DeathYear"].set('-')
                self._ppl[ppl_ref]["ID"].set('-')


def main():
    # Get the RootsMagic database info
    #rmagicPath = 'C:\\Dropbox\\RootsMagic Database\\myfamily.rmgc'
    rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    editor = Editor(rmagicPath)
    editor.mainloop()


if __name__ == '__main__':
    main()
