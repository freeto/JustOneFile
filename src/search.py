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
Class for manage algorithm and communicate with her
"""

import gtk, multiprocessing, Queue

from src import algorithm, tab_search

# -----------------------
# La Recherche contient l'algorithm et des fonctions
# pour communiquer avec lui, ainsi que ces informations associées
# Une recherche contient donc :
#  - l'état d'avencement de l'algo
#  - Des fonctions pour communiquer avec l'algo
#  - L'onglet associé avec la recherche
# -----------------------


class Search():
    """
    Contain functions for communicate with the algorithm.
    """
    
    def __init__(self, path):
        """
        Initialize attributs and algorithm
        
        Arguments:
        - `path`: The path who want to search duplicates files
        """

        self.path = path

        self.progress = 0.0
        self.action = 'Initilize'
        self.step = 0
        self.done = False
        self.new_dbl = []
        self.tab = tab_search.TabSearch()  # L'onglet associé
        self._queue_send = multiprocessing.Queue()

        self.algorithm = algorithm.Algorithm(self._queue_send, path)
        

    
    def _get_last_entry(self):
        """
        Return the last entry of the pipe
        """

        self.list_dbl = []

        if self._queue_send.empty():
            return False

        # Tant qu'il y à une entrée, on contenu de recevoir ..
        while not self._queue_send.empty():
            infos = self._queue_send.get()
            self.new_dbl.append(infos['dbl'])

        return infos
        


    def update_infos(self):
        """
        Update informations
        """

        infos = self._get_last_entry()

        if not infos: return

        self.progress = infos['progress']
        self.action = infos['action']
        self.done = infos['done']



    def start(self):
        """
        Run algorithm
        """
        
        self.algorithm.start()


    def join(self):
        """
        Join processus
        """
        
        self.algorithm.join()


    def terminate(self):
        """
        Terminate algorithm
        """
        
        self.algorithm.terminate()
