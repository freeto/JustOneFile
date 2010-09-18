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
Functions for get informations of the selected file.
"""

import Image, os, hashlib, subprocess, mimetypes, gio, gtk

def get_thumbnail(file_path):
    """
    Return a gtk.gdk.pixbuf who contain the thumbnail of the file.
    
    Arguments:
    - `file_path`: The file to get the thumbnail.
    """

    file_path = os.path.expanduser (file_path)
    file_path = os.path.abspath (file_path)

    # Vérifie tout d'abord si le fichier éxiste.
    if not os.path.exists (file_path): return False
    # Vérifie que l'on ne veut pas créer une miniature d'une miniature.
    if file_path.find ('.thumbnails/') > 0: return False
    
    file_name = os.path.basename (file_path)

    # Cherche si la miniature éxiste déjà.
    file_hash = hashlib.md5 ('file://' + file_path).hexdigest ()
    tb_filename = os.path.join (os.path.expanduser ('~/.thumbnails/normal'),
                               file_hash) + '.png'
    if os.path.exists (tb_filename):
        return tb_filename

    try:
        # Marchera si le fichier est une image.
        im = Image.open (file_path)
        im.thumbnail ((128, 128), Image.ANTIALIAS)
        im.save (tb_filename, 'PNG')
    except IOError:
        try:
            # Marchera si le fichier est une vidéo.
            # On fait appelle si possible au programme 'totem-video-thumbnailer'.
            result = subprocess.Popen (['totem-video-thumbnailer',
                                       file_path, tb_filename],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE).wait ()
            if result != 0: return False
        except OSError:
            return False
        

    # Retourne un objet de type gtk.gdk.Pixbuf.
    return gtk.Image ().set_from_file (tb_filename).get_pixbuf ()



def get_mimeicon(file_path):
    """
    Return a gtk.gdk.Pixbuf who contain the mime-type icon.

    Arguments:
    - `file_path`: The file to get the icon.
    """
    
    if not os.path.exists (file_path): return False

    # Prend le mimetype du fichier.
    mime = mimetypes.guess_type (os.path.basename (file_path))[0]
    if mime is None:
        mime = 'text/plain'

    theme = gtk.icon_theme_get_default () # Charge le thème.
    icon = gio.content_type_get_icon (mime)
    icon = theme.lookup_by_gicon (icon, 128, gtk.ICON_LOOKUP_USE_BUILTIN)

    if icon is None:            # L'icone n'éxiste pas.
        icon = gio.content_type_get_icon ('text/plain')
        icon = theme.lookup_by_gicon (icon, 128, gtk.ICON_LOOKUP_USE_BUILTIN)

    return icon.load_icon ()
