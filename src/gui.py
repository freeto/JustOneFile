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


import pygtk, gtk, os, subprocess, gobject, threading, time

gobject.threads_init() # Sinon PyGtk bug


from src import search


class windowJustonefile():
    """
    A Fdupes gui
    """
    
    def __init__(self):
        """
	Initialize compenants
        """

        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder()
        self.interface.add_from_file('justOneFile.glade')

        self.interface.connect_signals(self)

        # Une liste des recherche en cour (thread)
        self.list_search = []

        gobject.timeout_add(200, self.update_search_info)



    def start_search(self, path):
        """
        Run search in a new thread
        """
        
        # On créé un nouveau thread
        s = search.Search(path)

        # On ajoute une barre de progression ainsi qu'un label pour la
        # recherche.
        s.label = gtk.Label(path)
        s.pb = gtk.ProgressBar()

        # On les ajoutes au calque principale
        vbox = self.interface.get_object('vbox_p')
        vbox.pack_end(s.pb)
        vbox.pack_end(s.label)

        # Et on les active
        s.label.show()
        s.pb.show()

        self.list_search.append(s)

        self.list_search[-1].start()



    def update_search_info(self):
        """
        Get searchs info and display its
        """
        
        for s in self.list_search:

            pb = s.pb
            pb.set_text(s.action)

            if s.progress == -1:
                # On met la barre en mode attente
                pb.pulse()
            else:

                pb.set_fraction(float(s.progress))


        # On donne la main à un autre processus
        time.sleep(0.01)
        
        return True

        
        
    # -----------------------
    # Signal function
    # -----------------------

    def on_windowFdupes_destroy(self, widget):
        """
        Call when window is destroy
        Exit to the gtk main loop and close all threads
        
        Arguments:
        - `widget`: The widget who call this function
        """

        for s in self.list_search:
            s.finished = True

        gtk.main_quit()
        

    def on_button_run_clicked(self, widget):
        """
        Call when run's button was clicked
        
        Arguments:
        - `widget`: The widget who call this function
        """
        
        # On prend le chemin et on le formate
        path = self.interface.get_object('entry_path').get_text()
        path = os.path.normpath(path)
        path = os.path.abspath(path)

        # Et on lance le processus
        self.start_search(path)


    def on_button_clean_clicked(self, widget):
        """
        Call when button 'button_clean' is clicked
        
        Arguments:
        - `widget`: The widget who call this function
        """

        for s in self.list_search:
            print s
            if s.finished:
                # On enlève les widgets du conteneur et on enlève les
                # recherches de la liste

                vbox = self.interface.get_object('vbox_p')
                vbox.remove(s.pb)
                vbox.remove(s.label)
