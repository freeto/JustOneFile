#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	treemenu.py
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
A menu in a treeview.
"""

import gtk, pango

class TreeMenu():
    """
    A menu in a treeview to control a notebook.
    """
    
    def __init__(self, notebook):
        """
        Arguments:
        - `notebook`: The notebook to control.
        """

        self._notebook = notebook

        self.init_model ()
        self.init_treeview ()
        notebook.connect ('page-added', self.insert_item)
        notebook.connect ('switch-page', self._on_switch_page)


    def init_model(self):
        """
        Initialize and construct the model.
        """

        # Titre, stock-icone, weight.  
        self._model = gtk.ListStore (str, str, int)

        for page_num in range (0, self._notebook.get_n_pages ()):
            child = self._notebook.get_nth_page (page_num)
            title = self._notebook.get_tab_label_text (child)

            self._model.append ([title, "", 400])


    def init_treeview(self):
        """
        Create a treeview.
        """

        # Créé un treeview avec une colone contenant 2 CellRenderer.
        treeview = gtk.TreeView ()
        cell_pix = gtk.CellRendererPixbuf ()
        cell_text = gtk.CellRendererText ()

        # Modifie les propriétés.
        treeview.set_headers_visible (False)
        cell_text.set_property ('ellipsize', pango.ELLIPSIZE_END)
        cell_text.set_property ('weight-set', True)

        # Créé la colone.
        column = gtk.TreeViewColumn ('')
        column.pack_start (cell_pix, False)
        column.pack_start (cell_text, True)
        column.add_attribute (cell_text, "text", 0)
        column.add_attribute (cell_pix, "stock-id", 1)
        column.add_attribute (cell_text, "weight", 2)        

        treeview.append_column (column)
        treeview.set_model (self._model)
        treeview.connect ('cursor-changed', self._on_cursor_change)
        treeview.set_cursor ((0,))
        treeview.show ()

        self._treeview = treeview


    def _on_cursor_change(self, treeview):
        """
        Call when the cursor change in the treemenu.
        Change the the notebook's current page.
        """
        
        self._notebook.set_current_page (treeview.get_cursor ()[0][0])


    def get_treeview(self):
        """
        Return the treeview
        """
        return self._treeview


    def _on_switch_page(self, notebook, page, page_num):
        """
        Call when the notebook page is changed.
        """

        # Place le curseur à la bonne position si besoin.
        cursor = self._treeview.get_cursor ()[0]
        if cursor is None or page_num != cursor[0]:
            self._treeview.set_cursor ((page_num,))


    def insert_item(self, notebook, child, page_num):
        """
        Insert an item into the treemenu.
        """

        # Ajoute une entré dans le modèle.
        title = notebook.get_tab_label_text (child)
        self._model.insert (page_num, [title, "", 400])


    def refresh(self):
        """
        Refresh the treeview content.
        """

        for page_num in range (0, self._notebook.get_n_pages ()):
            child = self._notebook.get_nth_page (page_num)
            title = self._notebook.get_tab_label_text (child)

            self._model[page_num][0] = title


    def set_item_stock(self, pos, stock):
        """
        Set the item's icon with the stock icon 'stock'.
        
        Arguments:
        - `pos`: The item's position.
        - `stock`: The stock icon.
        """
        self._model[pos][1] = stock


    def set_important(self, pos, imp):
        """
        Set the item's icon with the stock icon 'stock'.
        
        Arguments:
        - `pos`: The item's position.
        - `imp`: A boolean.
        """
        if imp:
            self._model[pos][2] = 1000
        else:
            self._model[pos][2] = 400
