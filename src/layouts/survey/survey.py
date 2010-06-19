#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	survey.py
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
A layout for panel, survey display file survey and file informations
"""

from src import layout

# Ce layout pour le panneau permet d'afficher un aperçu du fichier actuelement
# selectionné, et affiche quelques informations sur ce dernier.

class Layout(layout.Layout):
    """
    Survey layout class
    """
    
    def __init__(self, gui, name):
        """
	Initialize variables
        
        Arguments:
        - `gui`: The interface of GUI
        - `name`: The layout name
        """

        layout.Layout.__init__(self, gui, name)

        # On initialize les variables
        self.current_filepath = ''

