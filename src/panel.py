#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	panel.py
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
Panel class and functions for add layout, ect ...
"""

import gtk, pygtk, os
from src import layout


# Fonction pour importer un module avec tout ces attributs.
def import_all_attr(name):
    """
    Import all attributs from a module named 'name'
    
    Arguments:
    - `name`: The module name's
    """
    
    try:
        m = __import__(name)
    except ImportError:
        print "Impossible de trouver le module '"+name+"'."
        return

    # On import touts ces attributs, car cela n'est pas fait autrement
    for n in name.split('.')[1:]:
        m = getattr(m, n)

    print "Layout '"+name+"' was sucessfully loaded !"
    return m



# On import tout les layouts
_path_layout = 'src/layouts/'
_layout_module = {}
for layout_dir in os.listdir(_path_layout):
    if os.path.isdir(_path_layout+layout_dir):
        _layout_module[layout_dir] = import_all_attr('src.layouts.'+layout_dir+'.'+layout_dir)

class Panel():
    """
    Panel functions for ads a layout, ect...
    """
    
    def __init__(self, box, gui):
        """
	Initilize variables
        
        Arguments:
        - `box`: The main box of the panel
        """

        self._box = box
        self.gui = gui
        self.list_layouts = []
        self.list_all_layouts = _layout_module.keys()
        self.list_unused_layouts = self.list_all_layouts



    def add_layout(self, layout_name):
        """
        Adding a layout to the panel
        
        Arguments:
        - `layout_name`: Layout to add
        """

        if not layout_name in self.list_all_layouts:
            print 'Ajouter un layout : Nom invalide'
            return

        l = _layout_module[layout_name].Layout(self.gui, layout_name)
        self.list_layouts.append(layout_name)
        self.list_unused_layouts.remove(layout_name)

        # On ajoute ensuite le layout au panneau
        self._box.pack_start(self.format_mainbox(l.main_box, layout_name))

        self.update_cblayout()
        


    def remove_layout(self, widget, layout_name, box):
        """
        Call when 'button_close_layout' was clicked
        Remove the layout named 'name'
        
        Arguments:
        - `widget`: The widget who send the signal.
        - `layout_name`: The name of the layout to remove
        - `box`: The main_box of the layout.
        """
        
        if not layout_name in self.list_layouts:
            print "Suppression d'un layout : Nom invalide"
            return

        # On enlève le box
        self._box.remove(box)

        # On met à jour les listes
        self.list_layouts.remove(layout_name)
        self.list_unused_layouts.append(layout_name)
        
        self.update_cblayout()
        



    def format_mainbox(self, main_box, layout_name):
        """
        Format the main box for the panel display.
        
        Arguments:
        - `main_box`: The main box to format 
        - `layout_name`: The name of the layout
        """
        
        # On lui ajoute une entete contenant le nom du layout et un bouton
        # fermer. Le modèle de l'entete est dans un fichier glade.
        self.header = gtk.Builder()
        self.header.add_from_file('src/layouts/layout.glade')
        self.header.connect_signals(self)

        # On place le containeur principale du layout dans le box conçu pour.
        layout_content_box = self.header.get_object('layout_content')
        layout_content_box.pack_start(main_box)

        main_box = self.header.get_object('main_box')
        main_box.unparent()

        # On connect le signal du bouton de fermeture du layout a la fonction 
        # coresspondante.
        button_close = self.header.get_object('button_close_layout')
        button_close.connect('clicked', self.remove_layout, layout_name, main_box)

        # On change le titre du layout :
        titre = self.header.get_object('label_layout_title')
        titre.set_text(layout_name.capitalize())

        return main_box


  
    def update_cblayout(self):
        """
        Update the content of the combobox layout.
        """
        
        cb = self.gui.get_object('cb_layout')
        cb_model = cb.get_model()

        # On met à jour le modèle avec les layout restant non encore utilisés
        cb_model.clear()

        if not self.list_unused_layouts: # Plus de layout à ajouté
            # On affiche un message et on désactive le bouton
            cb_model.append(['Aucun panneau inutilisé'])
            cb.set_sensitive(False)
            self.gui.get_object('button_add_layout').set_sensitive(False)

        else:
            # On active la cb et le bouton et on ajoute dans le modèle de la cb
            # tout les layouts restants.
            cb.set_sensitive(True)
            self.gui.get_object('button_add_layout').set_sensitive(True)
            for l_name in self.list_unused_layouts:
                cb_model.append([l_name.capitalize()])

        cb.set_active(0)        
