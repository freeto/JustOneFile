#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	layout.py
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
Layout class
"""

import gtk, pygtk, os


# Un layout est un objet qui peut etre rajouté dans 
# le panel.

class Layout():
    """
    Class for layout panel's
    """
    
    def __init__(self, gui, name):
        """
	Initialize variables
        
        Arguments:
        - `gui`: The interface of GUI
        - `name`: The layout name
        """

        # On fourni 'gui' pour que le layout soit indépendant,
        # Pour qu'il puisse tout seul intérargir avec le gui.
        # Il n'est donc pas dépendant de le gui et le gui
        # n'a pas à gérer le contenu d'un layout.

        self.gui = gui
        self.name = name
        
        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder()
        self.interface.add_from_file('src/layouts/'+name+'/'+name+'.glade')
        self.interface.connect_signals(self)
        
        self.main_box = self.interface.get_object('main_box')
        self.main_box.unparent()
