#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	preferences.py
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
A function for load preferences.
"""

import os, ConfigParser, gtk


# Le dictionnaire des options.
_options = {}
_options['Display'] = [{'name': 'tool_bar',
                        'def': 'Afficher/Cacher la barre d\'outils',
                        'type': bool}]


def load(file_path):
    """
    Load preferences from a file and return they.
    
    Arguments:
    - `file_path`: A path to the preferences's file.
    """

    # On vérifie que le fichier éxiste.
    if not os.path.exists (file_path):
        print "Le fichier de configuration '" + file_path + "' n'éxiste pas."
        return False

    # Le fichier de préférences est organisé de cette façon :
    # clé: valeur

    config = ConfigParser.RawConfigParser ()

    try:
        config.read (file_path) # On parse le fichier.
    except ConfigParser.missingSectionHeaderError:
        print 'ConfParser: Aucune section déclarée'
        return False
    except ConfigParser.ParsingError:
        print 'ConfParser: Impossible de parser le fichier de configuration.'
        return False

    prefs = {}

    # Pour chaque section, on vérifie si elle éxiste, puis on vérifie si toute
    # les options sont présentent et si tout est bon, on prend leur valeur.
    for section_name in _options.keys ():
        if not config.has_section (section_name):
            print "La section '" + section_name + "' n'éxiste pas."
            return False

        for option_dict in _options[section_name]:
            if not config.has_option (section_name, option_dict['name']):
                print "L'option '" + option_dict['name'] + "' est manquante."
                return False

            prefs[option_dict['name']] = {'value': config.get (section_name, option_dict['name']),
                                          'def': option_dict['def']}

            # Convertit la valeur.
            if option_dict['type'] == bool: # Boolean
                if prefs[option_dict['name']]['value'] in (0, 'False'):
                    prefs[option_dict['name']]['value'] = False
                else:
                    prefs[option_dict['name']]['value'] = True

    return prefs


def get_vbox():
    """
    Construct a graphical view for prefs.
    """

    # [ > Expander 1 (Section_name) ]
    #   [Alignement]
    #     [Widget (CheckButton, RadioButtons ...]
    
    vbox = gtk.VBox ()
    vbox.show ()

    for section_name, option_list in _options.iteritems ():
        vbox_expand = gtk.VBox ()
        vbox_expand.show ()

        align = gtk.Alignment ()
        align.set_padding (0, 0, 10, 0)
        align.add (vbox_expand)
        align.show ()

        expander = gtk.Expander ()
        expander.set_label (section_name)
        expander.add (align)
        expander.set_expanded (True)
        expander.show ()

        for option_dict in option_list:

            if option_dict['type'] == bool:
                widget = gtk.CheckButton (option_dict['def'])
            else:
                return False

            widget.show ()
            vbox_expand.pack_start (widget, False)

        vbox.pack_start (expander)

    return vbox
                
                
        
