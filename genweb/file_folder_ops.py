# Name:        FileFolderOps
# Purpose:      This has three functions:
#                   - get a list of the files in a folder
#                       getFilesInFolder(pathString) which returns a list
#                   - get a list of folders in a folder
#                       getFoldersInFolder(pathString) which returns a list
#                   - get a list of the contents of each file in a folder that have the
#                       specified extension (e.g. html, xml)
#                       get_folder_file_contents(pathstring,extension)
#
#
# Author:      pagerk
#
# Created:     25/01/2013
# Copyright:   (c) pagerk 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def get_files_in_folder(pathString):
   """creates a list of files in the specified folder"""
   import string
   import os

   args = os.listdir(pathString)
   files = []
   for a in args:
      if os.path.isdir(pathString + "/" + a):
         #files.append(getFilesInFolder(pathString + "/" + a))
         pass
      else:
         files.append(pathString + "/" + a)

   return files

def rename_files_in_folder(pathString,find_str,replace_str,file_ext):
    """renames all files in specified folder that match the source string
        and extension"""
    import string
    import os
    import sys

    files = get_files_in_folder(pathString)

    for file_name in files:
        if file_name.find(find_str) > 0 and file_name.find(file_ext) > 0:
            new_file_name = file_name.replace(find_str, replace_str)
            try:
                os.renames(file_name, new_file_name)
            except:
                print("Folder rename error:", sys.exc_info()[0])
                print('  current file name = ',file_name, \
                      '   renamed file = ', new_file_name, '\n')

    return

def get_folders_in_folder(pathString):
   """creates a list of folders in the specified folder"""
   import string
   import os
   args = os.listdir(pathString)
   folders = []
   for a in args:
      if os.path.isdir(pathString + "/" + a):
         folders.append(pathString + "/" + a)
      else:
         pass
   return folders

def get_folder_file_contents(folder_path,extension):
    import string
    import os

    folder_files = get_files_in_folder(folder_path)
    file_contents = []
    # Loop through the file names in the current subfolder.
    for file_name in folder_files:
        file_string = ''
        # Separate the path from the file name
        file_name_length = len(file_name)
        folder_path_length = len(folder_path)+1
        base_file_name = file_name[folder_path_length:file_name_length]
        # The only file contents we care about are xml files
        if (base_file_name.endswith(extension)):
            with open(file_name, 'r') as f:
                # create a list of tuples containing file name and file contents
                file_string = str(f.readlines())
                file_contents.append((base_file_name,file_string))
            f.closed

    return file_contents