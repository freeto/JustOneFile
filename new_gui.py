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

import pygtk, gtk, os


class WindowJustonefile():
    """
    The JustOneFile GUI
    """
    
    def __init__(self):
        """
        Initialize 
        """

        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder()
        self.interface.add_from_file('new_gui.glade')
        self.interface.connect_signals(self)
        
        # Initialisation des widgets de la fenetre
        self.init_treeview_menu()
        self.init_treeview_dbl()
        self.init_toolbar()
        self.init_statusbar()



    def init_treeview_menu(self):
        """
        Init the window's treeview menu
        """
        
        # Le treeview_menu est en fait le treeview a gauche qui sert de menu.
        # A ne pas confondre avec le menu du haut.

        self.tree_menu = self.interface.get_object('treeview_menu')

        # On créé le modèle du menu
        self.modele_treemenu = gtk.TreeStore(str)
        self.tree_menu.set_model(self.modele_treemenu)

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Colone à virée", cell, text=0)
        col.set_expand(True)
        self.tree_menu.append_column(col)

        # On modifie ces propriétés
        self.tree_menu.set_headers_visible(False)

        # Et on le remplit
        self.modele_treemenu.append(None, ['Accueil'])
        self.modele_treemenu.append(None, ['Préférence'])
        self.modele_treemenu.append(None, ['Aide'])


    def init_treeview_dbl(self):
        """
        Initilize the treeview of duplicates files
        """
        
        # Ce treeview contient la liste des fichiers en doubles sous forme
        # d'arbre.

        self.tree_dbl = self.interface.get_object('treeview_dbl')

        # On créé le modèle du menu
        self.modele_treedbl = gtk.TreeStore(str)
        self.tree_dbl.set_model(self.modele_treedbl)

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Doublons", cell, text=0)
        col.set_expand(True)
        self.tree_dbl.append_column(col)

        # Et on le remplit
        iter = self.modele_treedbl.append(None, ['Fichier 1.txt'])
        self.modele_treedbl.append(iter, ['Autre fichier 1.txt'])
        iter = self.modele_treedbl.append(None, ['background.jpg'])
        self.modele_treedbl.append(iter, ['arbres.jpg'])



    def init_toolbar(self):
        """
        Input buttons in toolbar
        """
        
        toolbar = self.interface.get_object("toolbar")

        # On ajoute les boutons

        tb = gtk.ToolButton(gtk.STOCK_NEW)
        tb.set_tooltip_text('Nouvelle recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        tb = gtk.ToolButton(gtk.STOCK_REMOVE)
        tb.set_tooltip_text('Supprime la recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)

        tb = gtk.ToolButton(gtk.STOCK_PREFERENCES)
        tb.set_tooltip_text('Préférences')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        tb = gtk.ToolButton(gtk.STOCK_HELP)
        tb.set_tooltip_text('Aide')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)

        tb = gtk.ToolButton(gtk.STOCK_QUIT)
        tb.set_tooltip_text('Quitter JustOneFile')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)


    def init_statusbar(self):
        """
        Initialize the windows status bar
        """
        
        sb = self.interface.get_object('statusbar')

        # Context à modifier, un context pour une recherche + contexte pour les
        # actions du programme (enregistrer ...)
        self.sb_context = sb.get_context_id('Search status bar')
        
        sb.push(self.sb_context, 'Construction de la liste ... (63 %)')



    # -----------------------
    # Signaux
    # -----------------------


    def on_windowJustonefile_destroy(self, widget):
        """
        Call when the window was destroy
        
        Arguments:
        - `widget`: The widget who send the signal
        """
        
        gtk.main_quit()



# -----------------------
# Ifmain
# -----------------------


if __name__ == '__main__':
    # On charge l'interface
    window = WindowJustonefile()

    # Et on lance la boucle gtk
    gtk.main()
