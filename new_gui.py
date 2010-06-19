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
from src import panel


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
        self.init_panel()

        # C'est l'interface qui s'occupe de gérer la visibilité du panel, mais 
        # c'est la classe Panel qui soccupe d'ajouter des 'layouts'.



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
        # D'arbre.

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



    def init_panel(self):
        """
        Initilize the panel
        """
        
        # (Le panneau est déja dans le fichier .glade)
        self._hpaned = self.interface.get_object('hpaned_panel')
        self._hpaned_parent = self._hpaned.get_parent()
        self._hpaned_child1 = self._hpaned.get_child1()
        self._hpaned_child2 = self._hpaned.get_child2()
        
        # Le panneau est invisible par defaut.
        self.panel_visiblity = False
        self.set_panel_visibility(False)
        self.panel = panel.Panel(self._hpaned_child2, self.interface)
        # On ajoute le calque par defaut
        # self.panel.add_layout('survey')

        # On contruit la combox et on la met à jour
        cb = self.interface.get_object('cb_layout')
        cb_model = gtk.ListStore(str)
        case = gtk.CellRendererText()
        cb.set_model(cb_model)
        cb.pack_start(case, True)
        cb.add_attribute(case, 'text', 0)
        self.panel.update_cblayout()



    def set_panel_visibility(self, visibility):
        """
        Display or not the panel
        
        Arguments:
        - `visibility`: True if the panel will be visible.
        """

        # On met ou on enlève le hpaned, avec les calques correspondants.

        if visibility:
            # On ajoute le panneau
            self._hpaned_parent.remove(self._hpaned_child1)

            self._hpaned.pack1(self._hpaned_child1, True, False)
            self._hpaned.pack2(self._hpaned_child2, True, False)

            # Et on ajoute le HPaned au calque self._hpaned_parent
            self._hpaned_parent.pack_start(self._hpaned)

        else:
            # On enlève le panneau
            self._hpaned_parent.remove(self._hpaned)
            
            # On ajoute le calque vbox_tree_search
            self._hpaned_child1.reparent(self._hpaned_parent)


            



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



    def on_button_panel_clicked(self, widget):
        """
        Call when the panel button is clicked
        Set the visibility of the panel
        
        Arguments:
        - `widget`: The widget who send the signal
        """
        
        if self.panel_visiblity:
            self.set_panel_visibility(False)
            self.panel_visiblity = False
        else:
            self.set_panel_visibility(True)
            self.panel_visiblity = True            


    def on_button_add_layout_clicked(self, widget):
        """
        Add a layout to the panel
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        cb = self.interface.get_object('cb_layout')
        cb_model = cb.get_model()

        layout_name = (cb_model[cb.get_active()][0]).lower()
        self.panel.add_layout(layout_name)




# -----------------------
# Ifmain
# -----------------------


if __name__ == '__main__':
    # On charge l'interface
    window = WindowJustonefile()

    # Et on lance la boucle gtk
    gtk.main()
