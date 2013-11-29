#-------------------------------------------------------------------------------
# Name:
# Purpose:     given a string that is a concatenation of names with their first
#              letters capitalized, separate them into separate words or
#              characters
#
# Author:      pagerk
#
# Created:     06/08/2013
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

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

if __name__ == '__main__':
    import string
    cat_string = 'initialize'
    while len(cat_string) > 0:
        cat_string = input('enter the test string')
        #print(' separated string = ', separate_on_caps(cat_string))
