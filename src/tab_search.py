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
        self.init_treeview_dbl()


    def init_treeview_dbl(self):
        """
        Initilize the treeview of duplicates files
        """
        
        # Ce treeview contient la liste des fichiers en doubles sous forme
        # d'arbre.

        tree = self.interface.get_object('treeview_dbl')

        # On créé le modèle
        model_treedbl = gtk.TreeStore(str)
        tree.set_model(model_treedbl)

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Doublons", cell, text=0)
        col.set_expand(True)
        tree.append_column(col)

        # On définit le champ de recherche
        tree.set_search_entry(self.interface.get_object('entry_search'))


    def set_searchbar_visibility(self, visibility):
        """
        Hide or show the searchbar
        
        Arguments:
        - `visibility`: A boolean, False -> Hide, True -> Show
        """

        # On affiche ou enlève la barre de recherche.
        # Les différents calques sont contenu dans un notebook. Pour afficher
        # la barre de recherche, on a juste à changer de page !
        # page 0 = barre de bouton
        # page 1 = barre de recherche

        nb = self.interface.get_object('notebook_controlbar')

        # On fait un petit test pour savoir si il est utile de changer de page.
        cur_page = nb.get_current_page()
        if (visibility and cur_page == 1) or (not visibility and cur_page == 0):
            return

        if visibility:
            nb.next_page()
            self.interface.get_object('entry_search').grab_focus()
        else:
            nb.prev_page()


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


    def add_dbl(self, lists_dbl):
        """
        Add the new duplicates files into the list.
        
        Arguments:
        - `list_dbl`: A list who contain the new duplicates files.
        """
        
        if lists_dbl == []: return
        model = self.interface.get_object('treeview_dbl').get_model()

        # Contient une liste de liste de liste de doublons
        for list_dbl in lists_dbl:
            # Contient une liste de liste de doublons
            for list_file in list_dbl:
                
                iter = model.append(None, [list_file[0]])
                # Contient une liste de doublons
                for file in list_file[1:]:
                    model.append(iter, [file])


    # -----------------------
    # Signaux
    # -----------------------

    def on_tb_search_toggled(self, widget):
        """
        Call when the search toggle button was toggle.

        Arguments:
        - `widget`: The widget who send the signal
        """

        self.set_searchbar_visibility(widget.get_active())


    def on_treeview_dbl_focus_in_event(self, widget, event):
        """
        Call when the treeview_dbl get focus.
        Hide the search_bar
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # On test si la barre de recherche est active et on agit en fonction.
        ac = self.interface.get_object('notebook_controlbar').get_current_page()
        
        if ac == 1:
            self.interface.get_object('tb_search').clicked()


    def on_button_prev_dbl_clicked(self, widget):
        """
        Go to the previous dbl.
        
        Arguments:
        - `widget`:
        """
        
        # On selectionne le fichier précédent.
        tree = self.interface.get_object('treeview_dbl')
        path = tree.get_cursor()[0]
        
        # On vérifie avant de selectionner que l'on pas sur le premier
        # fichier.
        if len(path) == 1 and path[0] == 0: return
        elif len(path) == 2: tree.set_cursor(path[0])
        else: tree.set_cursor(path[0] - 1)


    def on_button_prev_file_clicked(self, widget):
        """
        Select the next file.
        
        Arguments:
        - `widget`:
        """

        # On selectionne le fichier suivant.
        tree = self.interface.get_object('treeview_dbl')
        model = tree.get_model()
        path = tree.get_cursor()[0]

        # 3 possibilité : soit le curseur est actuellement sur un doublon
        # soit le curseur est sur un fichier
        # soit le curseur est sur le premier fichier d'un doublons
        if (len(path) == 1 and path[0] > 0) or (len(path) == 2 and path[1] == 0
                                                and path[0] > 0):
            # On prend le doublons précédent, on compte le nombre d'enfant
            # et on place le curseur sur le dernier.
            iter = model.get_iter((path[0] - 1))
            tree.expand_row(path[0] - 1, False)
            lenght = model.iter_n_children(iter)
            tree.set_cursor((path[0] - 1, lenght -1))
        elif len(path) == 2 and path[1] > 0:
            tree.set_cursor((path[0], path[1] - 1))


    def on_button_select_next_clicked(self, widget):
        """
        Select the next file.
        
        Arguments:
        - `widget`:
        """
        
        # On selectionne le fichier suivant.
        tree = self.interface.get_object('treeview_dbl')
        path = tree.get_cursor()[0][0]
        last_path = len(tree.get_model()) - 1
        
        # On vérifie avant de selectionner que l'on pas déjà sur le dernier
        # fichier.
        if path == last_path: return
        tree.set_cursor(path + 1)


    def on_button_select_last_clicked(self, widget):
        """
        Select the last file.
        
        Arguments:
        - `widget`:
        """
        
        # On selectionne le fichier suivant.
        tree = self.interface.get_object('treeview_dbl')
        last_path = len(tree.get_model()) - 1
        tree.set_cursor(last_path)
