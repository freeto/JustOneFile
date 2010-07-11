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
        self.list_dbl = []
        self.action = 'Initialisation'
        self.done = False



    def update_infos(self):
        """
        Send infos about algorithm progress and get signal
        """

        # On envoie un dictionaire
        infos = {}
        infos['progress'] = self.progress
        infos['action'] = self.action
        infos['done'] = self.done
        infos['dbl'] = self.list_dbl

        self.queue_send.put(infos)

        # On retourne 'True' pour indiquer à gobject que la fonction c'est bien
        # déroulée, sinon sa bloque le programme.
        return True

        

    def gen_all_files_paths(self, dir_path):
        """
        Generates all files path
        
        Arguments:
        - `dir_path`: The base directories
        """
        
        # On explore toute l'arborescence à l'aide de la fonction os.walk()
        # elle explore toute l'arborécense des fichier à partie d'un chemin
        # donné.
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for file_name in filenames:
                # Cette fonction est un générateur, elle donne à chaque 'appel'
                # le chemin d'un fichier à tester. (Pour ne pas consommer de mémoire)
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

        # On lit le fichier par block de 1 Mo (1024*1024), pour éviter de prendre 
        # trop de RAM.

        md5_string = ""
        content = True

        while content:
            content = file_obj.read(1048576) # 1048576 = 1024*1024
            if not content: break

            # On Hash le block, et on place tout sa dans une variable qui contient 
            # à la suite les sommes md5 de tout les blocks
            md5_string += hashlib.md5( content ).hexdigest()

        file_obj.close()

        # On retourne la somme md5 de la chaine qui contient toutes les sommes md5
        return hashlib.md5( md5_string ).hexdigest()
        


    def get_size(self, file_path):
        """
        Return size of a file
        
        Arguments:
        - `file_path`: The file to get size
        """

        # On prend sa taille si on peut
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

        # Cette fonction 'run', elle est en fait appellé implicitement lorsque
        # l'on lance la fonction start. la fonction start met
        # cette classe dans un nouveau processus et appelle la fonction run()
        # de cette dernière. A partir de maintenant donc, pour communiquer,
        # c'est avec des queue.
        # C'est la fonction update_infos() qui est chargé d'envoyer l'état de 
        # l'algo dans la queue.

        # -----------------------
        # Fonctionement de l'algorithme
        # 
        # 1 - On fait un tableau organisé des fichiers qui ont la meme taille.
        #     Tout les fichiers qui ont une taille unique sur l'ensemble des
        #     fichiers à tester sont donc obligatoirement unique, il n'y à pas
        #     besoin de les tester avec une somme md5.
        # 
        # 2 - On recherche les fichiers qui ont une meme somme md5.
        #     Si il ont une meme somme md5, alors ce sont des doublons.
        #     Ont les stock dans un tableau et on enverat régulièrement des infos 
        #     dans la queue.
        # -----------------------


        # -----------------------
        # 1 - On garde que les fichiers qui ont la meme taille.
        # -----------------------

        self.action = 'Build file list'
        self.progress = -1      # Met la bare en mode 'activité'

        self.update_infos()

        # Associe une taille (keys) à un/des chemins de fichiers
        dico_filesize = {}
        allfiles_size = 0       # La taille de l'ensemble des fichiers à testé

        # On parcour l'arbre des fichiers ...
        for file_path in self.gen_all_files_paths(self.path):
            file_size = self.get_size(file_path)
            if not file_size: continue

            allfiles_size += file_size

            # si la clé n'éxiste pas encore, on la créée et on indique que la 
            # valeur sera une liste.
            if not dico_filesize.has_key(file_size):
                dico_filesize[file_size] = []

            dico_filesize[file_size].append(file_path)
            

        # On enlève les éléments qui sont unique, pour garder que les fichiers
        # qui ont au moin un autre fichier de meme taille.

        list_filesize = []
        for item in dico_filesize.values():
            if len(item) > 1:    # Si plusieurs fichiers ont la meme taille ..
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
        self.list_dbl = []           # La liste des doublons

        for list_file in list_filesize:
            
            # Si la liste 

            for file_path in list_file:

                md5_sum = self.get_md5sum(file_path)

                # Si l'entré dans le dico n'éxiste pas encore, on la créée
                if not md5_sum in dico_md5:
                    dico_md5[md5_sum] = []

                dico_md5[md5_sum].append(file_path)

                # On fait la progression en fonction de la taille.
                progress += self.get_size(file_path)
                self.progress = float(progress) / float(allfiles_size)
                self.update_infos()
                
            # On cherche les doublons
            for item in dico_md5.values():
                if len(item) > 1: # Doublons !
                    self.list_dbl.append(item)

                    self.update_infos()
            
            # On remet les listes à 0
            dico_md5 = {}
            self.list_dbl = []


        # -----------------------
        # Recherche finie
        # -----------------------

        self.action = 'Finished'
        self.progress = 1.0
        self.done = True

        self.update_infos()

        print 'Terminated !'
        return
