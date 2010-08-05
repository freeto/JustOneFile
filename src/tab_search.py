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
        Initilize the tab's search.
        
        Arguments:
        - `title`: The tab title
        """
        
        # On contruit l'onglet à partir du fichier 'tab_search.glade'.
        # On prend juste les widgets qu'il y a dans la fenetre.

        self.interface = gtk.Builder ()
        self.interface.add_from_file ('tab_search.glade')
        self.interface.connect_signals (self)

        # Le calque principale s'appelle 'main_box'.
        self.main_box = self.interface.get_object ('main_box')
        self.main_box.unparent () # Afin de le mettre dans un autre calque.

        self.label_title = gtk.Label (title)
        self.init_treeview_dbl ()
        self.interface.get_object ('checkb_control_toggle_files').set_active (True)


    def init_treeview_dbl(self):
        """
        Initilize the treeview of duplicates files.
        """
        
        # Ce treeview contient la liste des fichiers en doubles sous forme
        # d'arbre.

        tree = self.interface.get_object ('treeview_dbl')

        # On créé le modèle.
        model = gtk.TreeStore (str, gobject.TYPE_BOOLEAN)
        tree.set_model (model)

        # On créée la première colone. (texte) (Nom du fichier ou doublon)
        cell = gtk.CellRendererText ()
        cell.set_property ('ellipsize', pango.ELLIPSIZE_START)
        col = gtk.TreeViewColumn ("Doublons", cell, text=0)
        col.set_cell_data_func (cell, self.cell_file_render)
        col.set_expand (True)
        tree.append_column (col)
        
        # On créé la colone qui contient la case à cocher (toggle).
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
        self.display_toggle_files = True
        self.control_toggle_files = True
            

    def set_searchbar_visibility(self, visibility):
        """
        Hide or show the searchbar.
        
        Arguments:
        - `visibility`: A boolean, True for show.
        """

        # On affiche ou cache la barre de recherche.
        # Les différents calques sont contenu dans une boite à onglet. Pour
        # afficher la barre de recherche, on a juste à changer de page.
        # page 0 = Barre de bouton
        # page 1 = Barre de recherche
        # page 2 = Préférences

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
        - `visibility`: A boolean, True for show.
        """

        # On affiche ou enlève la barre de préférence.
        # Les différents calques sont contenu dans une boite à onglet. Pour
        # afficher la barre de recherche, on a juste à changer de page.
        # page 0 = Barre de bouton
        # page 1 = Barre de recherche
        # page 2 = Préférences

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
        Set the label_search_path text.
        
        Arguments:
        - `text`: The new text of the label
        """
        
        self.interface.get_object ('label_search_path').set_text (text)
        

    def set_title(self, title):
        """
        Set the new title of the tab's search.
        
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

        # Contient un un ou plusieur ensembles de doublons.
        for list_dbl in lists_dbl:
            
            # Contient une liste de doublons.
            for list_file in list_dbl:
                # On affiche juste le nom du fichier avec le nb de doublons.
                name = os.path.basename (list_file[0])
                name += ' (' + str (len (list_file)) + ')'
                iter = model.append (None, [name, False])
                
                # On affiche tout les doublons.
                for file in list_file:
                    model.append (iter, [file, False])


    def  _toggle_file(self, model, path):
        """
        Toggle a file (and a dbl if all files was toggle).
        
        Arguments:
        - `model`: The treeview_dbl model.
        - `path`: A path pointing to the file.
        """
        
        # Si la ligne est un doublon, on ne peut pas la cocher.
        if model.iter_depth (model.get_iter (path)) == 1:
            model[path][1] = not model[path][1]

        # Si tous les fichiers du doublon sont cochés, on désactive le doublon.
        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            iter = model.get_iter_from_string (str (path[0]) + ':' + str (i))
            if not model.get_value (iter, 1):
                model[path[0]][1] = False
                return
        
        # Si on arrive la, c'est que tout les fichiers sont cochés. On désactive
        # le doublon.
        model[path[0]][1] = True


    def _get_first_file_index(self, dbl):
        """
        Return None if the dbl has not uncheck file else return the first file
        index.
        
        Arguments:
        - `dbl`: The dbl index.
        """

        # On sélectionne le doublon précédent.
        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        first_file = None

        # On détermine l'index du premier fichier du doublon :
        # Si on ne control pas les fichiers cochés, le premier fichier est 0.
        # Sinon, on test quel est le premier fichier.

        if self.control_toggle_files:
            first_file = 0

        else:
            # Le premier fichier non coché est le premier fichier du doublon.
            for i in xrange (model.iter_n_children (model.get_iter ((dbl,)))):
                if not model[(dbl, i)][1]:
                    first_file = i
                    break

        return first_file


    # -----------------------
    # Signaux
    # -----------------------

    def on_tb_search_toggled(self, widget):
        """
        Hide or show the searchbar.
        """

        if self.interface.get_object ('notebook_controlbar').get_current_page () == 2:
            self.interface.get_object ('tb_file_preferences').clicked ()
        self.set_searchbar_visibility (widget.get_active ())


    def on_treeview_dbl_focus_in_event(self, widget, event):
        """
        Show the control buttons.
        """

        # On détermine quel est la page affichée, on désactive le bouton
        # correspondant afin de ne pas avoir de différences entre l'état des
        # boutons et la page affichée. Le fait de désactiver un bouton affichera
        # automatiquement les boutons de control.

        ac = self.interface.get_object ('notebook_controlbar').get_current_page ()
        
        if ac == 1:
            self.interface.get_object ('tb_search').clicked ()
        if ac == 2:
            self.interface.get_object ('tb_file_preferences').clicked ()
            

    def on_button_prev_dbl_clicked(self, widget):
        """
        Go to the previous dbl.
        """
        
        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        path = tree.get_cursor ()[0]

        # On vérifie si on est pas sur le premier doublon.
        if path == (0,):
            return

        # On regarde si le premier fichier est plus bas dans la liste des
        # fichiers, dans ce cas on met le curseur dessus.
        first_file = self._get_first_file_index (path[0])
        if len (path) == 2 and first_file < path[1]:
            tree.set_cursor ((path[0], first_file))
            return
        elif path <= (0, first_file):
            return

        # On parcour ensuite les doublons précédent, et si le premier fichier est
        # trouvé, on lui donne le curseur.
        first_file = None
        while first_file is None:
            path = (path[0] - 1,)
            first_file = self._get_first_file_index (path[0])
            if first_file is None and path[0] == 0: # Premier doublon, on sort.
                return

        tree.expand_row (path[0], False)
        tree.set_cursor ((path[0], first_file))


    def on_button_prev_file_clicked(self, widget):
        """
        Select the previous file.
        """

        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        path = tree.get_cursor ()[0]

        # On fait une petite vérification pour éviter les déplacements inutiles.
        if path == (0,) or path == (0, 0): return
        
        # 2 possibilités :
        #  -Soit le curseur est sur un fichier placé après le premier fichier de
        # ce doublon.
        #  -Sinon le curseur est sur ou avant le premier fichier du doublon.

        first_file = self._get_first_file_index (path[0])

        if path > (path[0], first_file):
            # On est sur un fichier après le premier fichier.
            # On selectionne le fichier précédent, en fonction de l'option
            # self.control_toggled_file .
            if not self.control_toggle_files:
                for i in xrange (path[1] - 1, -1, -1):
                    if not model[(path[0], i)][1]:
                        tree.set_cursor ((path[0], i))
                        return

            tree.set_cursor ((path[0], path[1] - 1))

        elif path > (0, first_file):
            # On prend le premier doublon précédent qui a au moin un fichier non
            # coché.
            path = (path[0] - 1,)
            while model[path][1]:
                if path == (0,):
                    return
                path = (path[0] - 1,)

            iter = model.get_iter ((path[0]))
            tree.expand_row (path[0], False)
            lenght = model.iter_n_children (iter) - 1

            if not self.control_toggle_files:
                # On prend le premier fichier que l'ont trouve en partant de la
                # fin qui n'est pas coché.
                for i in xrange (lenght, -1, -1):
                    if not model[(path[0], i)][1]:
                        tree.set_cursor ((path[0], i))
                        return
            else:
                # On met le curseur sur dernier fichier.
                tree.set_cursor ((path[0], lenght))
            

    def on_button_next_file_clicked(self, widget):
        """
        Go to the next file.
        """

        tree = self.interface.get_object ('treeview_dbl')
        model = tree.get_model ()
        path = tree.get_cursor ()[0]
        last_path = model.iter_n_children (model.get_iter ((path[0]))) - 1
        
        # On fait une petite vérification pour éviter les déplacements inutiles.
        if path == (len (model) - 1, last_path): return

        # 3 possibilités :
        #  -Soit le curseur est actuellement sur un doublon.
        #  -Soit le curseur est sur le dernier fichier d'un doublon.
        #  -Soit le curseur est sur un fichier.

        if len (path) == 1:
            # On place le curseur sur le premier fichier de ce doublon.
            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], 0))
            
        elif path[1] == last_path:
            # On place le curseur sur le premier fichier du doublon suivant.
            tree.expand_row (path[0] + 1, False)
            tree.set_cursor ((path[0] + 1, 0))
            
        else:
            # On sélectionne le fichier suivant.
            tree.set_cursor ((path[0], path[1] + 1))
        

    def on_button_next_dbl_clicked(self, widget):
        """
        Go to the next dbl.
        """
        
        # On sélectionne le doublon suivant.

        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()
        last_dbl = len (model) - 1
        
        # 3 possibilités :
        #  -Soit on est sur un fichier du dernier doublon.
        #  -Soit on est sur un doublon.
        #  -Sinon, on est forcément sur un fichier quelquonque.
        
        if len (path) == 2 and path[0] == last_dbl:
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
        Toggle all files except the selected file.
        """

        # On coche toute les lignes sauf celle qui est selectionnée.

        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()

        # Si la ligne selectionnée est un doublon, alors on considère que c'est
        # le premier fichier qui est selectionné.
        if len (path) == 1:
            path = (path[0], 0)

        # On parcour touts les fichiers du doublon et on les coche tous sauf le
        # fichier sélectionné.
        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            if i == path[1]:
                model[(path[0], i)][1] = False
                
            else:
                model[(path[0], i)][1] = True

                # On enlève la ligne du modèle si l'option 'Afficher' est
                # désactivée.
                if not self.display_toggle_files:
                    self.remove_files.append ((model[(path[0], i)][0], path[0]))
                    self.need_remove.append (model.get_iter ((path[0], i)))

        # On enlève tout les fichiers à enlever.
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

        # On n'affiche pas la case à cocher si c'est un doublon.
        if model.iter_depth (iter) == 0:
            cell.set_property ('visible', False)
        else:
            cell.set_property ('visible', True)


    def on_tb_file_preferences_toggled(self, widget):
        """
        Hide or show the préférences bar.
        """

        # Si c'est la barre de recherche qui était active, on désactive le bouton
        # car celui ci restera enfoncé.
        if self.interface.get_object ('notebook_controlbar').get_current_page () == 1:
            self.interface.get_object ('tb_search').clicked ()
            
        self.set_preferencesbar_visibility (widget.get_active ())

        
    def on_checkb_control_toggle_files_toggled(self, widget):
        """
        Enabled or disabled option 'Control toggle files'.
        """

        self.control_toggle_files = widget.get_active ()
