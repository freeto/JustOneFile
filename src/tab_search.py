#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	tab_search.py
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
The interface of a search's tab.
"""


import gtk, pygtk

class TabSearch():
    """
    Function of a search's tab
    """
    
    def __init__(self, title='Recherche'):
        """
        Initilize the tab's search
        
        Arguments:
        - `title`: The tab title
        """
        
        # On contruit l'onglet à partir du fichier Glade
        # On prend juste les widgets qu'il y a dans la fenetre

        self.interface = gtk.Builder()
        self.interface.add_from_file('tab_search.glade')

        self.interface.connect_signals(self)

        # Le calque principale s'appelle 'main_box'
        self.main_box = self.interface.get_object('main_box')
        # On lui enlève son parent
        self.main_box.unparent()

        self.label_title = gtk.Label(title)



    def set_pb(self, progress, text):
        """
        Set the progress bar infos
        
        Arguments:
        - `progress`: The progress bar fraction
        - `text`: The progress bar text
        """
        
        pb = self.interface.get_object('pb_progress')

        if progress == -1:
            # On met la barre en mode attente
            pb.pulse()
        else:
            pb.set_fraction(float(progress))

        pb.set_text(text)

            
    def set_label(self, text):
        """
        Set the label_search_path text
        
        Arguments:
        - `text`: The new text of the label
        """
        
        label = self.interface.get_object('label_search_path')
        label.set_text(text)


    def set_title(self, title):
        """
        Set the new title of the tab's search
        
        Arguments:
        - `title`: The new title of the tab's search
        """
        
        self.label_title.set_text(title)
