#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	algorithm.py
#	
#	Copyright 2010 Draless <draless@mailoo.org>
#	
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU general Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your options) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	Gnu General Public License for more details.
#
#	You should have received a copy of the Gnu General Public License
#	along with this program; if not; write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	MA 02110-1301, USA.

"""
Class and functions to search duplicates files
"""


import multiprocessing, os, hashlib, time, gtk


# -----------------------
# Cette classe est comme un processus.
# -----------------------

class Algorithm(multiprocessing.Process):
    """
    Search duplicates files
    """
    
    def __init__(self, queue_send, path, options={}):
        """
        Initilize algorithm
        
        Arguments:
        - `queue_send`: The queue for communicate with the parent's process
        - `path`: The path were you want to search duplicates files
        - `options`: Options for algorithm
        """
        multiprocessing.Process.__init__(self)
        
        self.queue_send = queue_send
        self.path = path
        
        self.progress = 0.0
        self.action = 'Initialisation'
        self.step = 0
        self.done = False



    def update_infos(self):
        """
        Send infos about algorithm progress and get signal
        """

        # On envoie un dictionaire
        infos = {}
        infos['progress'] = self.progress
        infos['action'] = self.action
        infos['step'] = self.step
        infos['done'] = self.done

        self.queue_send.put(infos)

        return True

        

    def gen_all_files_paths(self, dir_path):
        """
        Generates all files path
        
        Arguments:
        - `dir_path`: The base directories
        """
        
        # On explore toute l'arborescence
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for file_name in filenames:
                yield dirpath + '/' + file_name




    def get_md5sum(self, file_path):
        """
        Return md5 sum of a file
        
        Arguments:
        - `file_path`: The path of the file
        """
        
        # On prend un descripteur de fichier pour pouvoir tester si le fichier
        # est bloquant ou pas (comme par exemple '/dev/null')
        try:
            file_des = os.open(file_path, os.O_RDONLY|os.O_NONBLOCK)
        except:
            print "Impossible d'ouvrir le fichier", file_path
            return False

        # On convertit le descripteur de fichier en object file
        file_obj = os.fdopen(file_des)

        md5_string = ""
        content = True

        while content:
            content = file_obj.read(1024 * 1024)
            md5_string += hashlib.md5( content ).hexdigest()

        file_obj.close()

        # On fait la somme md5 de la somme md5 des lignes du fichier
        return hashlib.md5( md5_string ).hexdigest()
        



    def get_listdir(self, dir_path):
        """
        Return a list containing all elements in the @dir_path

        Arguments:
        - `dir_path`: The dir path where you want get
        """

        try:
            return os.listdir(dir_path)
        except:
            print "Impossible d'acceder au dossier", dir_path
            return []


    def get_size(self, file_path):
        """
        Return size of a file
        
        Arguments:
        - `file_path`: The file to get size
        """

        # On prend sa taille
        try:
            file_size = os.path.getsize(file_path)
        except:
            print "Impossible d'agir sur le fichier", file_path
            return False

        return file_size
        



    # -----------------------
    # Run function
    # -----------------------

    def run(self):
        """
        Call when the start function is called.

        Return a list of duplicate's file.
        """
        

        # -----------------------
        # On garde que les fichiers qui ont la meme taille
        # -----------------------

        self.step = 1
        self.action = 'Build file list'
        self.progress = -1

        self.update_infos()

        dico_filesize = {}
        allfiles_size = 0
        i = 0

        for file_path in self.gen_all_files_paths(self.path):
            # On prend la taille du fichier
            file_size = self.get_size(file_path)
            if not file_size: continue

            allfiles_size += file_size

            # Et on ajoute le nom du fichier associer à sa taille dans le dico
            if not dico_filesize.has_key(file_size):
                dico_filesize[file_size] = []

            dico_filesize[file_size].append(file_path)
            

        # On enlève les éléments qui sont unique, pour garder que les fichiers
        # qui ont au moin un autre fichier de meme taille.

        list_filesize = []
        for item in dico_filesize.values():
            if len(item) > 1:
                list_filesize.append(item)
            else:
                allfiles_size -= self.get_size(item[0])
            

        # -----------------------
        # On recherche les fichiers qui ont une meme somme md5
        # -----------------------

        self.action = 'Searching duplicates files'
        self.progress = 0
        progress = 0
        
        self.update_infos()

        dico_md5 = {}

        for list_file in list_filesize:
            
            # Si la liste contient plus d'un item, il convient de faire une 
            # somme md5 pour vérifier si les fichiers sont bien identiques.

            for file_path in list_file:

                md5_sum = self.get_md5sum(file_path)

                # Si l'entré dans le dico n'éxiste pas encore, on la créée
                if not md5_sum in dico_md5:
                    dico_md5[md5_sum] = []

                dico_md5[md5_sum].append(file_path)

                # On fait la progression
                progress += self.get_size(file_path)
                self.progress = float(progress) / float(allfiles_size)
                self.update_infos()

        
        # On contruit la liste des doublons
        list_dbl = [item for item in dico_md5.values() if len(item) > 1]


        # La recherche est finie !
        self.action = 'Finished'
        self.progress = 1.0
        self.done = True

        self.update_infos()

        print 'Terminated !'

        return
