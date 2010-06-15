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

        

    def get_all_files_paths(self, dir_path):
        """
        Return a list containing all file path of file in
        a directory.

        Arguments:
        - `dir_path`: The dir path
        """

        list_files_path = []


        # On parcour l'arbre des dossiers récursivement et on stock tout les fichiers
        # recontrés dans une liste
        for elem_path in self._get_listdir(dir_path):

            # On contruit le chemin absolu.
            abs_path = dir_path + '/' + elem_path

            # Si c'est un fichier, on l'ajoute à la liste, si c'est un dossier,
            # on le parcour avec cette fonction.
            if os.path.isfile(abs_path):
                list_files_path.append(abs_path)

            elif os.path.isdir(abs_path):
                list_files_path += self.get_all_files_paths(abs_path)

        return list_files_path



    def get_content(self, file_path):
        """
        Return Content of file @file_path

        Arguments:
        - `file_path`: The file's path
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

        # Il se peut que l'on a le droit d'écrire dessus mais pas de le lire
        try:
            content = file_obj.read()
        except:
            print "Impossible de lire le fichier", file_path
            file_obj.close()
            return False

        file_obj.close()

        return content



    def _get_listdir(self, dir_path):
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



    # -----------------------
    # Run function
    # -----------------------

    def run(self):
        """
        Call when the start function is called.

        Return a list of duplicate's file.
        """
        
        # -----------------------
        # On fait la liste des fichiers
        # -----------------------

        self.step = 1
        self.action = 'Making files list'
        self.progress = -1
        
        self.update_infos()

        list_all_files_paths = self.get_all_files_paths(self.path)


        # -----------------------
        # On garde que les fichiers qui ont la meme taille
        # -----------------------

        self.step = 2
        self.action = 'Sort files list'
        self.progress = 0

        dico_filesize = {}
        list_len = len(list_all_files_paths)
        i = 0

        for file_path in list_all_files_paths:
            self.update_infos()

            # Calcul de la progression de la tache
            i += 1
            self.progress = float(i) / float(list_len)
            
            # On prend sa taille
            try:
                file_size = os.path.getsize(file_path)
            except:
                print "Impossible d'agir sur le fichier", file_path
                continue

            # Et on ajoute le nom du fichier associer à sa taille dans le dico
            if not dico_filesize.has_key(file_size):
                dico_filesize[file_size] = []

            dico_filesize[file_size].append(file_path)
            

        # On enlève les éléments qui sont unique, pour garder que les fichiers
        # qui ont au moin un autre fichier de meme taille.

        list_filesize = [x for x in dico_filesize.values() if len(x) > 1]
            

        # -----------------------
        # On recherche les fichiers qui ont une meme somme md5
        # -----------------------

        self.action = 'Searching duplicates files'
        self.progress = 0

        
        dico_md5 = {}
        list_len = len(list_filesize)
        i = 0
        last_p = 0

        for list_file in list_filesize:

            i += 1
            self.progress = float(i) / float(list_len)
            
            # On envoie les infos tout les 1% pour éviter la lenteur
            if int(self.progress * 100) > last_p:
                self.update_infos()
                last_p = int(self.progress * 100)
            

            # Si la liste contient plus d'un item, il convient de faire une 
            # somme md5 pour vérifier si les fichiers sont bien identiques.

            for file_path in list_file:
                # On prend le contenu du fichier
                content = self.get_content(file_path)

                if content == False: continue

                md5_sum = hashlib.md5( content ).hexdigest()

                # Si l'entré dans le dico n'éxiste pas encore, on la créée
                if not md5_sum in dico_md5:
                    dico_md5[md5_sum] = []

                dico_md5[md5_sum].append(file_path)

        
        # On contruit la liste des doublons
        list_dbl = [item for item in dico_md5.values() if len(item) > 1]


        # La recherche est finie !
        self.action = 'Finished'
        self.progress = 1.0
        print 'Terminated !'
        self.done = True

        self.update_infos()

        return
