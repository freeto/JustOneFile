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
        self.interface.add_from_file('justOneFile.glade')
        self.interface.connect_signals(self)

        # Initialisation des widgets de la fenetre
        self.controls_buttons = self.interface.get_object('hbox_controls_buttons')
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
        col = gtk.TreeViewColumn("", cell, text=0)
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

        # Bouton nouvelle recherche
        tb = gtk.ToolButton(gtk.STOCK_NEW)
        tb.set_tooltip_text('Nouvelle recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        # Bouton suprimme recherche
        tb = gtk.ToolButton(gtk.STOCK_REMOVE)
        tb.set_tooltip_text('Supprime la recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        # Bouton 'Stopper la recherche'. Si cliqué, ce bouton sera remplacé par
        # 'Reprendre la recherche'
        self.tb_stop_search = True
        tb = gtk.ToolButton(gtk.STOCK_MEDIA_STOP)
        tb.set_tooltip_text('Stopper la recherche')
        tb.connect("clicked", self.on_tb_stop_search_clicked)
        tb.show()
        toolbar.insert(tb, -1)

        # Séparateur
        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)
	
        # Bouton UNDO (Annuler)
        tb = gtk.ToolButton(gtk.STOCK_UNDO)
        tb.set_tooltip_text("Annuler l'action")
        tb.show()
        toolbar.insert(tb, -1)
        
        # Bouton REDO (Refaire)
        tb = gtk.ToolButton(gtk.STOCK_REDO)
        tb.set_tooltip_text("Refaire l'action")
        tb.show()
        toolbar.insert(tb, -1)
        
        # Séparateur
        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)
        
        # Bouton quitter
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
        
        sb.push(self.sb_context, 'Construction de la liste ...')


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


    def on_tb_search_toggled(self, widget):
        """
        Call when the search toggle button was toggle.

        Arguments:
        - `widget`: The widget who send the signal
        """

        self.set_searchbar_visibility(widget.get_active())



    def on_tb_stop_search_clicked(self, tb):
        """
        Call when the Stop search toolbutton's was clicked.
        """
        
        # Si l'état de la recherche est stopée, on affiche 'Reprendre'
        # sinon on affiche 'Stopper'.
        
        # Comme les mécanisme de recherche ne sont pas encore implémentés,
        # ce bouton est juste (pour le moment) un bouton de démonstration.
        # On vas donc juste inverser l'état du bouton lors du clic.
        # Penser à une meilleure implémentation.

        if self.tb_stop_search:
            # On vas afficher Reprendre.
            tb.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            tb.set_tooltip_text('Reprendre la recherche')
            self.tb_stop_search = False
        else:
            # On vas afficher Stopper
            tb.set_stock_id(gtk.STOCK_MEDIA_STOP)
            tb.set_tooltip_text('Stopper la recherche')
            self.tb_stop_search = True



    def on_entry_search_unfocus(self, event, widget):
        """
        We hide the search bar
        
        Arguments:
        - `widget`: The widget send the signal.
        """

        self.set_searchbar_visibility(False)
