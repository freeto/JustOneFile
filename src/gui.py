#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	gui.py
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
Gui class with functions
"""


import pygtk, gtk, os, subprocess, gobject, multiprocessing, time

from src import algorithm, search


class WindowJustonefile():
    """
    The JustOneFile GUI
    """
    
    def __init__(self):
        """
	Initialize compenants
        """

        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder()
        self.interface.add_from_file('justOneFile.glade')

        self.interface.connect_signals(self)

        # La liste des recherches
        self.list_search = []

        gobject.timeout_add(200, self.update_searchs_infos)



    def update_searchs_infos(self):
        """
        Update infos of all search's
        """

        for s in self.list_search:
            s.update_infos()
            
            # On met à jour l'interface
            s.tab.set_pb(s.progress, s.action)

            title = str(int(s.progress * 100)) + '%'
            s.tab.set_title(title)

        return True
        


    def new_search(self, path):
        """
        Create a new searh
        
        Arguments:
        - `path`: The path of the new search
        """
        
        # Chaque recherche est associée à un onglet.
        new_search = search.Search(path)

        self.list_search.append(new_search)
        
        self.add_tab(new_search.tab)
        new_search.start()

    
    def add_tab(self, tab):
        """
        Add a tab to the notebook
        
        Arguments:
        - `tab`: A TabSearch object
        """

        notebook = self.interface.get_object('notebook')

        notebook.append_page(tab.main_box, tab.label_title)
        

        
    # -----------------------
    # Signal function
    # -----------------------

    def on_windowFdupes_destroy(self, widget):
        """
        Call when window is destroy
        Exit to the gtk main loop and send a clase signal to all process
        
        Arguments:
        - `widget`: The widget who call this function
        """
        
        for s in self.list_search:
            s.terminate()

        gtk.main_quit()
        

    def on_button_run_clicked(self, widget):
        """
        Call when run's button was clicked
        
        Arguments:
        - `widget`: The widget who call this function
        """

        path = self.interface.get_object('entry_path').get_text()

        self.new_search(path)


    def on_button_clean_clicked(self, widget):
        """
        Call when button 'button_clean' is clicked
        
        Arguments:
        - `widget`: The widget who call this function
        """



# -----------------------
# TabSearch class
# -----------------------


class TabSearch():
    """
    Function of a search's tab
    """
    
    def __init__(self, title='Recherche'):
        """
        Initilize the tab's search
        
        Arguments:
        - `title`: The tab's title
        """
        
        # On contruit l'onglet à partir du fichier Glade
        # On prend juste les widgets qu'il y a dans la fenetre

        self.interface = gtk.Builder()
        self.interface.add_from_file('tab_search.glade')

        self.interface.connect_signals(self)

        # Le calque principal s'appelle 'main_box'
        self.main_box = self.interface.get_object('main_box')
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
        

