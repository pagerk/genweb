#!/usr/bin/env python3

import os
from tkinter import *
from tkinter import ttk
import logging

from . import rmagic


_moduleLogger = logging.getLogger(__name__)


class Editor(object):

    _MAX_MATCHES_VISIBLE = 6
    _MAX_TARGET_FAMILIES_VISIBLE = 22
    _MAX_PEOPLE_REFERENCED = 26

    def __init__(self, rmagicPath):
        self._rmagicPath = rmagicPath
        self._tables = rmagic.fetch_rm_tables(self._rmagicPath)

        self._matched_persons = []

        self._root = Tk()
        self._root.title("Family History: Enter a Person")

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except Exception:
            _moduleLogger.debug("Theme unsupported")

        mainframe = ttk.Frame(
            self._root,
            borderwidth=5, relief="sunken",
            width=200, height=100, padding="12 12 12 12"
        )

        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        #Search boxes
        self._srch_person = {
            "Given": StringVar(),
            "Surname": StringVar(),
            "BirthYear": StringVar(),
        }
        self._srch_person["Given"].set("")
        self._srch_person["Surname"].set("")
        self._srch_person["BirthYear"].set('19??')


        # Found person labels
        self._match = []
        for m_no in range(self._MAX_MATCHES_VISIBLE):
            self._match.append({
                "Given": StringVar(),
                "Surname": StringVar(),
                "BirthYear": StringVar(),
            })
            for f in self._match[m_no]:
                self._match[m_no][f].set('-')

        # Radiobutton person selector
        self._selected_person = StringVar()

        # Target family labels
        # checkbox include person - the variable is set to 1 if the button is
        # selected, and 0 otherwise.
        self._tgt_family = []
        for tf_no in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            self._tgt_family.append({
                "Check": StringVar(),
                "Given": StringVar(),
                "Surname": StringVar(),
                "BirthYear": StringVar(),
                "DeathYear": StringVar(),
                "ID": StringVar(),
            })
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
        for ppl_no in range(self._MAX_PEOPLE_REFERENCED):
            self._ppl.append({
                "Check": StringVar(),
                "Given": StringVar(),
                "Surname": StringVar(),
                "BirthYear": StringVar(),
                "DeathYear": StringVar(),
                "ID": StringVar(),
            })
            self._ppl[ppl_no]["Given"].set('-')
            self._ppl[ppl_no]["Surname"].set('-')
            self._ppl[ppl_no]["BirthYear"].set('-')
            self._ppl[ppl_no]["DeathYear"].set('-')
            self._ppl[ppl_no]["ID"].set('-')

        # File Generation labels
        self._file_gen = {
            "Header": StringVar(),
            "Artifact_ID_Label": StringVar(),
            "Artifact_ID": StringVar(),
            "Artifact_Title_Label": StringVar(),
            "Artifact_Title": StringVar(),
            "Artifact_Caption_Label": StringVar(),
            "Artifact_Caption": StringVar(),
        }

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
        ttk.Label(mainframe, textvariable=self._match[0]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[0]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[0]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_ID_Label"]).\
            grid(column=10, row=current_row, sticky=EW, columnspan=2)
        ttk.Entry(mainframe, width=7, textvariable=self._file_gen["Artifact_ID"]).\
                grid(column=12, row=current_row, sticky=(W, E), columnspan=3)

        current_row = 5
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='1').\
            grid(column=2, row=5, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[1]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[1]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[1]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._file_gen["Artifact_Title_Label"]).\
            grid(column=10, row=current_row, sticky=EW)
        ttk.Entry(mainframe, width=7, textvariable=self._file_gen["Artifact_Title"]).\
                grid(column=11, row=current_row, sticky=(W, E), columnspan=6)

        current_row = 6
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='2').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[2]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[2]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[2]["BirthYear"]).\
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
        ttk.Label(mainframe, textvariable=self._match[3]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[3]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[3]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)

        current_row = 8
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='4').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[4]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[4]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[4]["BirthYear"]).\
            grid(column=5, row=current_row, sticky=EW)

        current_row = 9
        ttk.Radiobutton(mainframe, text='', variable=self._selected_person, value='5').\
            grid(column=2, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[5]["Given"]).\
            grid(column=3, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[5]["Surname"]).\
            grid(column=4, row=current_row, sticky=EW)
        ttk.Label(mainframe, textvariable=self._match[5]["BirthYear"]).\
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

    def _populate_match_label(self):
        numPeoplePopulated = min(self._MAX_MATCHES_VISIBLE, len(self._matched_persons))
        for number in range(numPeoplePopulated):
            namestring = rmagic.build_given_name(self._matched_persons[number]["Given"])
            self._match[number]["Given"].set(str(namestring))
            self._match[number]["Surname"].set(str(self._matched_persons[number]["Surname"]))
            self._match[number]["BirthYear"].set(str(self._matched_persons[number]["BirthYear"]))
        for number in range(numPeoplePopulated, self._MAX_MATCHES_VISIBLE):
            self._match[number]["Given"].set("-")
            self._match[number]["Surname"].set("-")
            self._match[number]["BirthYear"].set("-")

    def _populate_target_relation(self, target, person):
        namestring = rmagic.build_given_name(person["Given"])
        target["Given"].set(str(namestring))
        target["Surname"].set(str(person["Surname"]))
        target["BirthYear"].set(str(person["BirthYear"]))
        target["DeathYear"].set(str(person["DeathYear"]))
        target["ID"].set(str(person["OwnerID"]))

    def _on_search_for_matches(self, *args):
        given_name_value = str(self._srch_person["Given"].get())
        surname_value = str(self._srch_person["Surname"].get())
        birthyear_value = str(self._srch_person["BirthYear"].get())

        name_dict = {
            'Surname': surname_value,
            'Given': given_name_value,
            'BirthYear': birthyear_value,
        }

        self._matched_persons = rmagic.fetch_person_from_fuzzy_name(self._tables['NameTable'], name_dict)
        self._populate_match_label()

    def _on_view_possible_person(self, *args):
        # identify the target person
        person_no = int(self._selected_person.get())

        # Clear the possible person table
        for person in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            for category in self._tgt_family[person]:
                self._tgt_family[person][category].set('-')

        target = 0
        self._populate_target_relation(self._tgt_family[target], self._matched_persons[person_no])

        parents = rmagic.fetch_parents_from_ID(
            self._tables['PersonTable'],
            self._tables['NameTable'],
            self._tables['FamilyTable'],
            self._matched_persons[person_no]['OwnerID'],
        )

        father = 1
        self._populate_target_relation(self._tgt_family[father], parents["Father"])

        mother = 2
        self._populate_target_relation(self._tgt_family[mother], parents["Mother"])

        spouses = rmagic.fetch_spouses_from_ID(
            self._tables['NameTable'],
            self._tables['PersonTable'],
            self._tables['FamilyTable'],
            self._matched_persons[person_no]['OwnerID'],
        )

        for spouse_no in range(len(spouses)):
            fam_spouses = 3
            self._populate_target_relation(self._tgt_family[fam_spouses+spouse_no], spouses[spouse_no])

        children = rmagic.fetch_children_from_ID(
            self._tables['ChildTable'],
            self._tables['NameTable'],
            self._tables['PersonTable'],
            self._tables['FamilyTable'],
            self._matched_persons[person_no]['OwnerID'],
        )

        for child_no in range(len(children)):
            fam_children = 7
            self._populate_target_relation(self._tgt_family[fam_children+child_no], children[child_no])

    def _on_build_image_ref(self, *args):
        raise NotImplementedError("TODO")

    def _on_add_to_people_ref(self, *args):
        # How many people are already in the People Referenced table (ppl_ref_no)
        ppl_ref_no = 0
        for i in range(self._MAX_PEOPLE_REFERENCED):
            if self._ppl[ppl_ref_no]["Given"].get() != '-':
                ppl_ref_no += 1
        # Append checked people to the People Referenced table
        for tf_no in range(self._MAX_TARGET_FAMILIES_VISIBLE):
            print('self._tgt_family[tf_no]["Check"] = ', self._tgt_family[tf_no]["Check"].get())
            if self._tgt_family[tf_no]["Check"].get() == 'yes':
                self._ppl[ppl_ref_no]["Given"].set(self._tgt_family[tf_no]["Given"].get())
                self._ppl[ppl_ref_no]["Surname"].set(self._tgt_family[tf_no]["Surname"].get())
                self._ppl[ppl_ref_no]["BirthYear"].set(self._tgt_family[tf_no]["BirthYear"].get())
                self._ppl[ppl_ref_no]["DeathYear"].set(self._tgt_family[tf_no]["DeathYear"].get())
                self._ppl[ppl_ref_no]["ID"].set(self._tgt_family[tf_no]["ID"].get())
                ppl_ref_no += 1

    def _on_build_ext_html(self, *args):
        raise NotImplementedError("TODO")

    def _on_build_inline_txt(self, *args):
        # Set the file generation labels
        self._file_gen["Header"].set('Inline Text')
        self._file_gen["Artifact_ID_Label"].set('ID	YYYYMMDD##')
        self._file_gen["Artifact_Title_Label"].set('Title')
        self._file_gen["Artifact_Caption_Label"].set('Caption')

        # Only display the people who have been selected
        ppl_ref = 0
        for ref in range(len(self._tgt_family)):
            if str(self._tgt_family[ref]["Check"].get()) == 'yes':
                self._ppl[ppl_ref]["Given"].set(str(self._tgt_family[ref]["Given"].get()))
                self._ppl[ppl_ref]["Surname"].set(str(self._tgt_family[ref]["Surname"].get()))
                self._ppl[ppl_ref]["BirthYear"].set(str(self._tgt_family[ref]["BirthYear"].get()))
                self._ppl[ppl_ref]["DeathYear"].set(str(self._tgt_family[ref]["DeathYear"].get()))
                self._ppl[ppl_ref]["ID"].set(str(self._tgt_family[ref]["ID"].get()))
                ppl_ref += 1
        for ppl_ref in range(ppl_ref, len(self._tgt_family)):
                self._ppl[ppl_ref]["Given"].set('-')
                self._ppl[ppl_ref]["Surname"].set('-')
                self._ppl[ppl_ref]["BirthYear"].set('-')
                self._ppl[ppl_ref]["DeathYear"].set('-')
                self._ppl[ppl_ref]["ID"].set('-')


def main():
    # Get the RootsMagic database info
    rmagicPath = 'C:\\Dropbox\\RootsMagic Database\\myfamily.rmgc'
    #rmagicPath = os.path.expanduser('~/Dropbox/RootsMagic Database/myfamily.rmgc')
    editor = Editor(rmagicPath)
    editor.mainloop()


if __name__ == '__main__':
    main()
