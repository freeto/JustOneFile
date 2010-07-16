#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	tab_search.py
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
The interface of a search's tab.
"""


import gtk, pygtk, os, gobject, pango

class TabSearch():
    """
    Function of a search's tab
    """
    
    def __init__(self, title='Recherche'):
        """
        Initilize the tab's search
        
        Arguments:
        - `title`: The tab title
        """
        
        # On contruit l'onglet à partir du fichier Glade
        # On prend juste les widgets qu'il y a dans la fenetre

        self.interface = gtk.Builder ()
        self.interface.add_from_file ('tab_search.glade')

        self.interface.connect_signals (self)

        # Le calque principale s'appelle 'main_box'
        self.main_box = self.interface.get_object ('main_box')
        self.main_box.unparent () # Afin de pouvoir l'inserer dans un autre calque.

        self.label_title = gtk.Label (title)
        self.init_treeview_dbl ()
        self.interface.get_object ('checkb_display_toggled_files').set_active (True)


    def init_treeview_dbl(self):
        """
        Initilize the treeview of duplicates files
        """
        
        # Ce treeview contient la liste des fichiers en doubles sous forme
        # d'arbre.

        tree = self.interface.get_object ('treeview_dbl')

        # On créé le modèle
        model = gtk.TreeStore (str, gobject.TYPE_BOOLEAN)
        tree.set_model (model)

        # On créée la première colone (texte)
        cell = gtk.CellRendererText ()
        cell.set_property ('ellipsize', pango.ELLIPSIZE_START)
        col = gtk.TreeViewColumn ("Doublons", cell, text=0)
        col.set_cell_data_func (cell, self.cell_file_render)
        col.set_expand (True)
        tree.append_column (col)
        
        # On créée la colone qui contient la case à coché (toggle).
        cell = gtk.CellRendererToggle ()
        cell.set_property ('activatable', True)
        cell.connect ('toggled', self.on_cell_toggled, model)
        col = gtk.TreeViewColumn ("", cell)
        col.set_cell_data_func (cell, self.cell_toggle_render)
        col.add_attribute (cell, 'active', 1)
        tree.append_column (col)

        # On définit le champ de recherche.
        tree.set_search_entry (self.interface.get_object ('entry_search'))

        # On initialise les variables.
        self.remove_files = []  # Contiendra les donnés des fichiers enlevés.
        self.need_remove = [] # Contiendra les lignes à enlever.
            

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
        # page 2 = barre de recherche

        nb = self.interface.get_object ('notebook_controlbar')

        # On fait un petit test pour savoir si il est utile de changer de page.
        cur_page = nb.get_current_page ()
        if (visibility and cur_page == 1) or (not visibility and cur_page == 0):
            return

        if visibility:
            nb.set_current_page (1)
            self.interface.get_object ('entry_search').grab_focus ()
        else:
            nb.set_current_page (0)


    def set_preferencesbar_visibility(self, visibility):
        """
        Hide or show the preferencebar.
        
        Arguments:
        - `visibility`: A boolean, False -> Hide, True -> Show
        """

        # On affiche ou enlève la barre de préférence.
        # Les différents calques sont contenu dans un notebook. Pour afficher
        # la barre de préférence, on a juste à changer de page !
        # page 0 = barre de bouton
        # page 1 = barre de recherche
        # page 2 = barre de recherche

        nb = self.interface.get_object ('notebook_controlbar')

        # On fait un petit test pour savoir si il est utile de changer de page.
        cur_page = nb.get_current_page ()
        if (visibility and cur_page == 2) or (not visibility and cur_page == 0):
            return

        if visibility:
            nb.set_current_page (2)
        else:
            nb.set_current_page (0)


    def set_label(self, text):
        """
        Set the label_search_path text
        
        Arguments:
        - `text`: The new text of the label
        """
        
        label = self.interface.get_object ('label_search_path')
        label.set_text (text)


    def set_title(self, title):
        """
        Set the new title of the tab's search
        
        Arguments:
        - `title`: The new title of the tab's search
        """
        
        self.label_title.set_text (title)


    def add_dbl(self, lists_dbl):
        """
        Add the new duplicates files into the list.
        
        Arguments:
        - `list_dbl`: A list who contain the new duplicates files.
        """
        
        if lists_dbl == []: return
        model = self.interface.get_object ('treeview_dbl').get_model ()

        # Contient une liste de liste de liste de doublons
        for list_dbl in lists_dbl:
            
            # Contient une liste de liste de doublons
            for list_file in list_dbl:
                # On affiche juste le nom di fichier avec le nb de doublons.
                name = os.path.basename (list_file[0])
                name += ' (' + str (len (list_file)) + ')'
                iter = model.append (None, [name, False])
                
                # On affiche tout les doublons.
                for file in list_file:
                    model.append (iter, [file, False])


    def set_toggled_files_visibility(self, visibility):
        """
        Remove or add the toggled files in the treeview_dbl.
        
        Arguments:
        - `visibility`: A boolean to set the toggled files visibility.
        """

        # Les fichiers sont stockés dans self.remove_files . Chaque élément est
        # un tuple de cette forme :
        # (nom_fichier, parent_path)

        # On test si la fonction est inutile dans la configuration donnée.
        if (visibility and self.remove_files == []) or (
            not visibility and not self.remove_files == []):
            return

        model = self.interface.get_object ('treeview_dbl').get_model ()

        if not visibility:      # On enlève les fichiers cochés.
            model.foreach (self._remove_toggled_files)

            # La fonction a remplit self.need_remove. Il ne reste plus qu'à
            # enlever les lignes indiquées.
            for row_iter in self.need_remove:
                model.remove (row_iter)
            self.need_remove = []
            
        else:                   # On met dans le modèle le fichiers enlevés.
            # (Pour l'instant, l'ordre n'est pas conservé.)
            for (file_name, parent_path) in self.remove_files:
                model.insert (model.get_iter (parent_path), -1, (file_name, True))

            self.remove_files = []



    def _remove_toggled_files(self, model, path, iter):
        """
        Set self.remove_files and self.need_remove.
        
        Arguments:
        - `model`: A TreeModel. (Here, the treeview_dbl model.)
        - `path`: The current path.
        - `iter`: The TreeIter pointing to path.
        """
        
        # On regarde dans le modèle tous les fichiers cochés. On les enlève
        # et on stock les informations qui permettront de les remettre.

        # On vérifie si la case à coché est activée et si c'est bien un fichier.
        if model[path][1] and  model.iter_depth (iter) == 1:
            file_name = model[path][0]
            self.remove_files.append  ((file_name, path[0]))
            self.need_remove.append (iter)


    def _remove_row(self, model, path):
        """
        Remove a row from a model, and set her information into
        self.remove_files .
        
        Arguments:
        - `model`: a gtk.TreeStore . (The treeview_dbl model)
        - `path`: The row path.
        """

        # On regarde si ont doit enlever les lignes cochées.
        if not self.display_toggled_files:
            self.remove_files.append ((model[path][0], path[0]))
            model.remove (model.get_iter (path))


    def  _toggle_file(self, model, path):
        """
        Toggle a file (and a dbl if all files was toggled).
        
        Arguments:
        - `model`: The treeview_dbl model.
        - `path`: A path pointing to the file.
        """
        
        # Si la ligne est un doublon, on ne peut pas la cocher.
        if model.iter_depth (model.get_iter (path)) == 1:
            model[path][1] = not model[path][1]
            self._remove_row (model, path)

        # Si tous les fichiers du doublon sont cochés, on désactive le doublon.
        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            iter = model.get_iter_from_string (str (path[0]) + ':' + str (i))
            if not model.get_value (iter, 1):
                model[path[0]][1] = False
                return
        
        # Si on arrive la, c'est que tout les fichiers sont cochés.
        model[path[0]][1] = True



    # -----------------------
    # signaux
    # -----------------------

    def on_tb_search_toggled(self, widget):
        """
        Call when the search toggle button was toggle.
        """

        if self.interface.get_object ('notebook_controlbar').get_current_page () == 2:
            self.interface.get_object ('tb_file_preferences').clicked ()
        self.set_searchbar_visibility (widget.get_active ())


    def on_treeview_dbl_focus_in_event(self, widget, event):
        """
        Call when the treeview_dbl get focus.
        Hide the search_bar
        """
        
        # On test si la barre de recherche est active et on agit en fonction.
        ac = self.interface.get_object ('notebook_controlbar').get_current_page ()
        
        if ac == 1:
            self.interface.get_object ('tb_search').clicked ()
        if ac == 2:
            self.interface.get_object ('tb_file_preferences').clicked ()
            

    def on_button_prev_dbl_clicked(self, widget):
        """
        Go to the previous dbl.
        """
        
        # On selectionne le doublon précédent.
        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        
        # On vérifie avant de selectionner que l'on pas sur le premier
        # fichier.
        if (len (path) == 1 and path[0] == 0) or path == (0,0): return
        elif len (path) == 2 and path[1] == 0:
            # On est sur le premier fichier du doublon, on peut aller au suivant
            tree.expand_row (path[0] - 1, False)
            tree.set_cursor ((path[0] - 1, 0))
        elif len (path) == 2 and path[1] > 0:
            # On ce place sur le premier fichier du doublon.
            tree.set_cursor ((path[0], 0))
        else:
            # On ce place dans le doublon précédent et sur le premier fichier.
            tree.expand_row (path[0] - 1, False)
            tree.set_cursor ((path[0] - 1, 0))


    def on_button_prev_file_clicked(self, widget):
        """
        Select the next file.
        """

        # On selectionne le fichier suivant.
        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        path = tree.get_cursor ()[0]

        # 3 possibilité : soit le curseur est actuellement sur un doublon
        # soit le curseur est sur un fichier
        # soit le curseur est sur le premier fichier d'un doublons
        if (len (path) == 1 and path[0] > 0) or (len (path) == 2 and path[1] == 0
                                                and path[0] > 0):
            # On prend le doublons précédent, on compte le nombre d'enfant
            # et on place le curseur sur le dernier.
            iter = model.get_iter ((path[0] - 1))
            tree.expand_row (path[0] - 1, False)
            lenght = model.iter_n_children (iter)
            tree.set_cursor ((path[0] - 1, lenght -1))
        elif len (path) == 2 and path[1] > 0:
            tree.set_cursor ((path[0], path[1] - 1))


    def on_button_next_file_clicked(self, widget):
        """
        Go to next file
        """

        # On selectionne le fichier suivant.
        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        path = tree.get_cursor ()[0]
        last_path = model.iter_n_children (model.get_iter ((path[0]))) - 1

        if path == (len (model) - 1, last_path): return

        # 3 possibilité : soit le curseur est actuellement sur un doublon
        # soit le curseur est sur un fichier
        # soit le curseur est sur le dernier fichier d'un doublon
        if len (path) == 1 and path[0] < len (model):
            # On place le curseur sur le premier fichier.
            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], 0))
        elif len (path) == 2 and path[1] == last_path:
            # On place le curseur sur le premier fichier du doublon suivant.
            tree.expand_row (path[0] + 1, False)
            tree.set_cursor ((path[0] + 1, 0))
        elif len (path) == 2 and path[1] < last_path:
            tree.set_cursor ((path[0], path[1] + 1))
        

    def on_button_next_dbl_clicked(self, widget):
        """
        Go to next dbl.
        """
        
        # On selectionne le fichier précédent.
        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()
        last_path = len (model) - 1
        
        # On vérifie avant de selectionner que l'on pas sur le dernier
        # doublon.
        if len (path) == 2 and path[0] == last_path:
            # On est sur le dernier doublon, on place le curseur à la fin.
            iter = model.get_iter (path[0])
            lenght = model.iter_n_children (iter) - 1
            tree.set_cursor ((path[0], lenght))
        elif len (path) == 1:
            # On deplit la ligne et on se place à a première position.
            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], 0))
        else:
            # On deplit la ligne suivante et on ce place à la première position.
            tree.expand_row (path[0] + 1, False)
            tree.set_cursor ((path[0] + 1, 0))

            
    def on_button_keep_only_clicked(self, widget):
        """
        Disabled all files except the selected file.
        """

        # On coche toute les lignes sauf celle qui est selectionnée.
        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()

        # Si la ligne selectionnée est un doublon, alors on considère que c'est
        # le premier fichier qui est selectionné.
        if len (path) == 1:
            path = (path[0], 0)

        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            if i == path[1]:
                model[(path[0], i)][1] = False
            else:
                model[(path[0], i)][1] = True
                # On enlève la ligne du modèle si l'option 'Afficher' est
                # désactivée.
                if not self.display_toggled_files:
                    self.remove_files.append ((model[(path[0], i)][0], path[0]))
                    self.need_remove.append (model.get_iter ((path[0], i)))

        for iter in self.need_remove:
            model.remove (iter)

        # On met la case à cocher de l'élément parent à False puisqu'il y a un
        # fichier de coché.
        model[path[0]][1] = False


    def on_button_delete_file_clicked(self, widget):
        """
        Toggle a file.
        """

        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()

        self._toggle_file (model, path)


    def on_cell_toggled(self, cell, path, model):
        """
        Call when the cell was toggled
        """

        self._toggle_file (model, path)


    def cell_file_render(self, col, cell, model, iter):
        """
        Call when a cell need renderer.
        """

        # On grise la cellule si la ligne est cochée.
        if model.get_value (iter, 1):
            cell.set_property ('foreground', 'grey')
        else:
            cell.set_property ('foreground', 'black')


    def cell_toggle_render(self, col, cell, model, iter):
        """
        Call when a cell need renderer.
        """

        if model.iter_depth (iter) == 0:
            cell.set_property ('visible', False)
        else:
            cell.set_property ('visible', True)


    def on_tb_file_preferences_toggled(self, widget):
        """
        Hide/Show the préférences bar.
        """
        
        if self.interface.get_object ('notebook_controlbar').get_current_page () == 1:
            self.interface.get_object ('tb_search').clicked ()        
        self.set_preferencesbar_visibility (widget.get_active ())


    def on_checkb_display_toggled_files_toggled(self, widget):
        """
        Active options.
        """

        # On désactive et décoche 'Controler' si ce check button n'est pas
        # coché. (Car on ne peut pas controler des objets invisibles)

        cb = self.interface.get_object ('checkb_control_toggled_files')
        if not widget.get_active ():
            cb.set_active (False)
            
        cb.set_sensitive (widget.get_active ())

        # On met à jour la variable et on enlève tous les fichiers cochés.
        self.display_toggled_files = widget.get_active ()
        self.set_toggled_files_visibility (widget.get_active ())
        

    def on_checkb_control_toggled_files_toggled(self, widget):
        """
        Enabled or disabled options.
        """

        self.control_toggled_files = widget.get_active ()
