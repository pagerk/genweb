#!/usr/bin/env python3

#-------------------------------------------------------------------------------
# Name:        file_ops
# Purpose:
#               srch_and_replace - Replace a search string with the replace string in the
#               specified file.
#
#               separate_strings_on_char - Given a string that has a chsracter
#               separating the sub-strings, return the substrings as a list
#
#               separate_on_caps - given a string that is a concatenation of
#               names with their first letters capitalized, separate them into
#               separate words or characters
#
# Author:      pagerk
#
# Created:     25/01/2013
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def srch_and_replace(folder_path, file, search_string,replace_string):
    import string
    import os

    with open(folder_path + '/' + file, 'r') as f:
        # create a list of the file contents
        file_contents = f.readlines()
    f.closed

    with open(folder_path + '/' + file, 'w') as f:
        # find and replace the string and then write the string to the file
        for line in file_contents:
            #if the file has the search string, change it, else keep old string
            if line.find(search_string) > -1:
                replaced_line = line.replace(search_string, replace_string)

            else:
                replaced_line = line

            f.write(replaced_line)
    f.closed

    return

def separate_strings_on_char(semicolon_separated_strings, separation_character):
    import string

    list_of_strings = []
    semicolon_count = semicolon_separated_strings.count(separation_character)
    for i in range(semicolon_count + 1):
        string_parts = semicolon_separated_strings.partition(separation_character)
        list_of_strings.append(string_parts[0])
        if string_parts[2] == '':
            break
        else:
            semicolon_separated_strings = string_parts[2]
    return list_of_strings

def separate_on_caps(item):
    import string

    item_length = len(item)
    last_char = item_length - 1

    #extract the name elements
    name = []
    letter_num = 0
    current_word = ''
    cap = []
    for letter_num in range(item_length):
        if item[letter_num].isupper():
            cap.append(letter_num)

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

    return name

#
if __name__ == "__main__":
    import sys
    folder_path = 'D:\Family History\Family History CD\Research\Individual Web Pages\TOCxml'
    file = 'aaa_test_Search_and_replace.xml'
    search_string = 'Abdill, Hanrvey'
    replace_string = 'Abdill, Harvey'
    srch_and_replace(folder_path, file, search_string,replace_string)
