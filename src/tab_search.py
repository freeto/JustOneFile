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


import gtk, pygtk, os, gobject, pango, hashlib, gnomevfs, datetime, shutil

class TabSearch():
    """
    Function of a search's tab
    """
    
    def __init__(self, title='Recherche'):
        """
        Initilize the tab's search.
        
        Arguments:
        - `title`: The tab title.
        """
        
        # On contruit l'onglet à partir du fichier 'tab_search.glade'.
        # On prend juste les widgets qu'il y a dans la fenetre.

        self.interface = gtk.Builder ()
        self.interface.add_from_file ('tab_search.glade')
        self.interface.connect_signals (self)

        # On prend le calque principal.
        self.main_box = self.interface.get_object ('window_tab_search')
        self.main_box = self.main_box.get_child ()
        self.main_box.unparent () # Pour l'inserer plus tard dans un onglet.

        self.label_title = gtk.Label (title)
        self.init_treeview_dbl ()
        self.interface.get_object ('checkb_control_toggle_files').set_active (True)
        self.context = self.interface.get_object ('statusbar').get_context_id (
            title)


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


    def set_pb(self, progress):
        """
        Set the progress bar with a new value.
        
        Arguments:
        - `progress`: The new value.
        """

        pb = self.interface.get_object ('pb_search')
        if progress < 0:
            pb.pulse ()
        else:
            pb.set_fraction (progress)
            pb.set_text (str (int (progress * 100)) + '%')


    def set_action(self, action):
        """
        Set the statusbar message.
        
        Arguments:
        - `action`: The new statusbar message.
        """

        sb = self.interface.get_object ('statusbar')
        sb.push (self.context, action)


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
        
        # Si le curseur est sur un fichier, on le coche. Si le curseur est sur
        # un doublon, on coche si possible le premier fichier de ce doublon.
        if model.iter_depth (model.get_iter (path)) == 1:
            model[path][1] = not model[path][1]

        # Si tous les fichiers du doublon sont cochés, on désactive le doublon.
        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            iter = model.get_iter_from_string (str (path[0]) + ':' + str (i))
            if not model.get_value (iter, 1):
                # Il reste au moin un fichier non coché.
                model[path[0]][1] = False
                return
        
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
        if path == (0,) or path is None:
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
        if path == (0,) or path == (0, 0) or path is None: return
        
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

        if path is None: return

        # On prend l'index du dernier fichier du doublon.
        if not self.control_toggle_files:
            last_file = None
            for i in xrange (model.iter_n_children (model.get_iter ((path[0]))) - 1,
                             0,
                             -1):
                if not model[(path[0], i)][1]:
                    last_file = i
                    break
        else:
            last_file = model.iter_n_children (model.get_iter ((path[0]))) - 1


        # Si last_file est égal à None, ou que le curseur est après le dernier
        # fichier, on doit mettre le curseur sur le premier fichier du premier
        # doublon suivant non coché.
        if last_file is None or len (path) == 1 or path[1] >= last_file:
            nb_of_dbl = len (model) - 1
            first_file = None   # Le premier fichier du doublon.

            # Si on est sur un doublon, alors on doit d'abord chercher sur ce
            # doublon avant de passer au suivant.
            if len (path) == 1:
                path = (path[0] -1,)

            # Cherche le premier doublon qui contient au moin un fichier non
            # coché.
            while (first_file is None):
                if path[0] == nb_of_dbl:
                    return      # Il n'y a pas de fichier suivant.
                path = (path[0] + 1,)
                first_file = self._get_first_file_index (path[0])

            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], first_file))

        else:
            # On prend le fichier suivant.
            if self.control_toggle_files:
                tree.set_cursor ((path[0], path[1] + 1))
                return

            # On prend le premier fichier suivant qui n'est pas coché.
            for i in xrange (path[1] + 1, model.iter_n_children (model.get_iter ((path[0],)))):
                if not model[(path[0], i)][1]:
                    tree.set_cursor ((path[0], i))
                    return
                

    def on_button_next_dbl_clicked(self, widget):
        """
        Go to the next dbl.
        """
        
        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        if path is None: return
        model = tree.get_model ()
        last_dbl = len (model) - 1
        first_file = self._get_first_file_index (path[0])

        # 3 possibilités :
        #  -Soit on est sur un fichier du dernier doublon.
        #  -Soit on est sur un doublon.
        #  -Sinon, on est forcément sur un fichier quelquonque.
        
        if len (path) == 2 and path[0] == last_dbl:
            # On est sur le dernier doublon, on place le curseur à la fin.
            iter = model.get_iter (path[0])
            lenght = model.iter_n_children (iter) - 1

            if not self.control_toggle_files:
                for i in xrange (lenght, 0, -1):
                    if not model[(path[0], i)][1]: # Le fichier n'est pas coché.
                        tree.set_cursor ((path[0], i))
                        return

            else:
                tree.set_cursor ((path[0], lenght))
            
        elif len (path) == 1:
            # On deplit la ligne et on se place à première position.
            while (first_file is None):
                if path[0] == last_dbl:
                    return

                path = (path[0] + 1,)
                first_file = self._get_first_file_index (path[0])
                
            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], first_file))
            
        else:
            # On deplit la ligne suivante et on ce place à la première position.
            first_file = None

            while (first_file is None):
                if path[0] == last_dbl:
                    return

                path = (path[0] + 1,)
                first_file = self._get_first_file_index (path[0])

            tree.expand_row (path[0], False)
            tree.set_cursor ((path[0], first_file))

            
    def on_button_keep_only_clicked(self, widget):
        """
        Toggle all files except the selected file.
        """

        # On coche toute les lignes sauf celle qui est selectionnée.

        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()

        if path is None: return

        # Si la ligne selectionnée est un doublon, alors on considère que c'est
        # le premier fichier qui est selectionné.
        if len (path) == 1:
            path = (path[0], 0)
            # On deplie le doubon et on le selectionne.
            tree.expand_row (path[0], False)
            tree.set_cursor (path)

        # On parcour touts les fichiers du doublon et on les coche tous sauf le
        # fichier sélectionné.
        for i in xrange (model.iter_n_children (model.get_iter (path[0]))):
            if i == path[1]:
                model[(path[0], i)][1] = False
                
            else:
                model[(path[0], i)][1] = True

        # On met la case à cocher de l'élément parent à False puisqu'il y a un
        # fichier de coché.
        model[path[0]][1] = False

        self.on_button_next_dbl_clicked (None)


    def on_button_delete_file_clicked(self, widget):
        """
        Toggle a file.
        """

        tree = self.interface.get_object ('treeview_dbl')
        path = tree.get_cursor ()[0]
        model = tree.get_model ()

        if path is None: return

        self._toggle_file (model, path)
        self.on_button_next_file_clicked (None)


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


    def on_treeview_dbl_cursor_changed(self, tree):
        """
        Get the mimetype of the selected file and update the survey.
        """

        path = tree.get_cursor ()[0]
        # Si le curseur est sur un doublon, l'aperçu n'est pas actualisé.
        if len (path) == 1: return

        model = tree.get_model ()
        file_path = model[path][0]
        file_path = os.path.abspath (file_path)
        survey = self.interface.get_object ('image_survey')

        # On tente d'afficher une miniature du fichier. La taille d'une
        # miniature est au maximum : 128x128.
        file_hash = hashlib.md5 ('file://' + file_path).hexdigest ()
        tb_filename = os.path.join (os.path.expanduser ('~/.thumbnails/normal'),
                                   file_hash) + '.png'
        if os.path.exists (tb_filename):
            survey.set_from_file (tb_filename)
            return

        # Sinon, on affiche l'image correspondant au mime-type du fichier.
        mime = (gnomevfs.get_mime_type (file_path)).replace ('/', '-')
        survey.set_from_icon_name (mime, gtk.ICON_SIZE_DIALOG)

        # (INFO) Il faudrait trouver un moyen de savoir si le mime-type éxiste,
        # comme ca, on pourrait quand meme afficher une image si le mime-type
        # n'éxiste pas.
        survey.set_pixel_size (128) # Taille non dynamique pour l'instant.

        return


    def on_button_apply_clicked(self, widget):
        """
        Apply change : remove the checked files.
        """

        def remove_checked_files(model, path, iter):
            """Remove the checked files."""

            if len (path) > 1 and model[path][1]:
                # La corbeille sous Gnome est situé dans ~/.local/share/Trash .
                # Un fichier d'infos pour une possible restauration est stocké
                # fans le dossier info. Les fichiers sont quand à eux dans le
                # dossier files.
                # Le fichier d'infos est sous cette forme :
                # [Trash Info]
                # path=/home/timothee/Documents/Projet/Glista Python/file
                # DeletionDate=2010-08-28T00:13:59

                file_path = os.path.abspath (model[path][0])
                file_name = os.path.basename (file_path)
                trash_dir = os.path.expanduser ('~/.local/share/Trash/')

                # On écrit le fichier d'info.
                with open (trash_dir + 'info/' + file_name + '.trashinfo', 'w') as f:
                    d = datetime.datetime
                    date_t = str (d.today ()).split (' ')
                    date_t[1] = date_t[1].split ('.')[0]

                    f.write ('[Trash Info]\n')
                    f.write ('Path=' + file_path + '\n')
                    f.write ('DeletionDate={0[0]}T{0[1]}\n'.format (date_t))

                # Déplace le fichier.
                shutil.move (file_path, trash_dir + 'files/' + file_name)
                need_remove.append (iter)

            
        need_remove = []
        model = self.interface.get_object ('treeview_dbl').get_model ()
        model.foreach (remove_checked_files)

        for iter in need_remove:
            model.remove (iter)
