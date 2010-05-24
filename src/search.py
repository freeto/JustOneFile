#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	search.py
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
Algorithme for search duplicates files
"""


import threading, os, hashlib, time


# -----------------------
# Cette classe est comme un thread.
# -----------------------

class Search(threading.Thread):
    """
    Algorithm and controls functions
    """
    
    def __init__(self, path, option={}):
        """
	Initilize algorithm variables
        
        Arguments:
        - `path`: The path who want to search duplicates
        - `option`: Options for searching
        """

        # Appeller la méthode start du thread appellera la méthode self.run()

        threading.Thread.__init__(self)

        self._path = path
        self._option = option

        self.progress = 0
        self.action = 'Initilizing'
        self.finished = False   # True when the search is completed
        
        # Les widget associés à la recherche
        self.label = None
        self.pb = None




    def _get_all_file_path(self, dir_path):
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
                list_files_path += self._get_all_file_path(abs_path)

        return list_files_path



    def _get_content(self, file_path):
        """
        Return Content of file @file_path

        Arguments:
        - `file_path`: the file path
        """

        # On prend un descripteur de fichier pour pouvoir tester si le fichier
        # est bloquant ou pas (comme par exemple '/dev/null')
        try:
            file = os.open(file_path, os.O_RDONLY|os.O_NONBLOCK)
        except:
            print "Impossible d'ouvrir le fichier", file_path
            return False

        # On convertit le descripteur de fichier en object file
        file = os.fdopen(file)

        # Il se peut que l'on a le droit d'écrire dessus mais pas de le lire
        try:
            content = file.read()
        except:
            print "Impossible de lire le fichier", file_path
            file.close()
            return False

        file.close()

        return content



    def run(self):
        """
        Call when thread is started.
        Return a list of duplicate file.
        """

        self.action = 'Make files list'
        self.progress = -1

        list_all_files_path = self._get_all_file_path(self._path)


        # On tri la liste par la taille ds fichiers
        self.action = 'Sort files list'
        self.progress = 0

        dico_filesize = {}
        list_len = len(list_all_files_path)
        i = 0

        for file_path in list_all_files_path:
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
            
            if self.finished: return None

            time.sleep(0.01)


        # On fait un test sur les fichiers de meme taille.
        self.action = 'Searching duplicates files'
        self.progress = 0

        dico_md5 = {}
        list_len = len(dico_filesize.values())
        i = 0

        for list_file in dico_filesize.values():

            i += 1
            self.progress = float(i) / float(list_len)

            # Si la liste contient plus d'un item, il convient de faire une 
            # somme md5 pour vérifier si les fichiers sont bien identiques.

            if len(list_file) > 1:
                for file_path in list_file:
                    # On prend le contenu du fichier
                    content = self._get_content(file_path)

                    if content == False:
                        continue

                    md5_sum = hashlib.md5( content ).hexdigest()

                    if not dico_md5.has_key(md5_sum):
                        dico_md5[md5_sum] = []

                    dico_md5[md5_sum].append(file_path)


                time.sleep(0.01)
            
            if self.finished: return None


        # On contruit la liste des doublons
        list_dbl = []
        for item in dico_md5.values():
            if len(item) > 1:
                list_dbl.append(item)

        # Pour que la variable soit accéssible de l'extérieur ..
        self.list_dbl = list_dbl

        # La recherche est finit, on stop le thread
        self.action = 'Finished'
        self.progress = 1.0

        self.finished = True


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
