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


import pygtk, gtk


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
        self.interface.add_from_file('new_gui.glade')

        self.interface.connect_signals(self)
        
        # Initialisation des widgets de la fenetre
        self.init_treemenu()



    def init_treemenu(self):
        """
        Init the window's treeview menu
        """
        
        # Le treemenu est en fait le treeview a gauche qui sert de menu.
        # A ne pas confondre avec le menu du haut.

        menu = self.interface.get_object('treeview_menu')

        # On créé le modèle du menu
        self.modele_treemenu = gtk.TreeStore(str)
        menu.set_model(self.modele_treemenu)

        # Et on le remplit
        self.modele_treemenu.append(None, ['Accueil'])
        self.modele_treemenu.append(None, ['Préférence'])
        self.modele_treemenu.append(None, ['Aide'])

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Colone à virée", cell, text=0)
        col.set_expand(True)
        menu.append_column(col)

        # On modifie ces propriétés
        menu.set_headers_visible(False)



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




if __name__ == '__main__':
    # On charge l'interface
    window = WindowJustonefile()

    # Et on lance la boucle gtk
    gtk.main()
