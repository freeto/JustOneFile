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
Class for manage GUI.
"""

import pygtk, gtk, os, gobject, pango
from src import search, preferences


class WindowJustonefile():
    """
    The JustOneFile GUI
    """
    
    def __init__(self):
        """
        Initialize 
        """

        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder ()
        self.interface.add_from_file ('src/glade/justOneFile.glade')
        self.interface.connect_signals (self)

        # Initialisation des widgets de la fenetre
        self.init_preferences ()
        self.list_search = []
        self.init_toolbar ()
        self.init_treeview_menu ()
        self.init_treeview_list_search ()
        self.init_newsearch ()

        self.apply_prefs ()

        gobject.timeout_add (200, self.update_searchs_infos)


    def init_treeview_menu(self):
        """
        Init the window's treeview menu
        """
        
        # Le treeview_menu est en fait le treeview a gauche qui sert de menu.
        # A ne pas confondre avec le menu du haut.
        tree = self.interface.get_object ('treeview_menu')

        # On créé le modèle du menu.
        model = gtk.TreeStore (str)
        tree.set_model (model)

        # On créée la colone (texte).
        cell = gtk.CellRendererText ()
        cell.set_property ('ellipsize', pango.ELLIPSIZE_END)
        col = gtk.TreeViewColumn ("", cell, text=0)
        col.set_expand (True)
        tree.append_column (col)

        # On modifi ces propriétés.
        tree.set_headers_visible (False)

        # On le remplit et on selectionne le premier item.
        # On prend touts les titres des onglets et on les mets dans le modèle du
        # treeview 'menu'.
        nb = self.interface.get_object ('notebook_main')
        
        # On parcour tous les onglets et on prend son titre, que l'on place dans le
        # modèle. Les 4 premiers onglets sont à la base  0, les autre dans le 4em.
        for i in xrange (0, 4):
            text = nb.get_tab_label_text (nb.get_nth_page (i))
            self.search_iter = model.append  (None, [text])

        # On liste toutes les recherches. A noté que le premier onglet sera
        # toujour 'Nouvelle recherche'.
        for i in xrange (4, nb.get_n_pages ()):
            text = nb.get_tab_label_text (nb.get_nth_page (i))
            model.append (self.search_iter, [text])

        # On deplit l'onglet 'Recherches'.
        tree.expand_row (3, False)
        # On affiche l'onglet de démarrage (A partir de la boite à onglet, car
        # ca évite de faire des conversions de position, ex : 5 -> (3, 1) )
        self.interface.get_object ('notebook_main').set_current_page (self.prefs['tab_start'])


    def init_treeview_list_search(self):
        """
        Initialize the treeview list_search.
        """
        
        # Le treeview 'list_search' est le treeview de l'onglet 'Recherches', qui
        # contient une liste détaillé de toutes les recherches.

        tree = self.interface.get_object ('treeview_list_search')

        # On créé le modèle du menu
        model = gtk.ListStore (str, str, int)
        tree.set_model (model)

        # On créée la première colone (texte)
        cell = gtk.CellRendererText ()
        col = gtk.TreeViewColumn ("Recherches", cell, text=0)
        col.set_expand (True)
        tree.append_column (col)

        # On créée deuxième colone (texte)
        cell = gtk.CellRendererText ()
        col = gtk.TreeViewColumn ("Progression", cell, text=1)
        tree.append_column (col)

        # On créée la colone (texte)
        cell = gtk.CellRendererText ()
        col = gtk.TreeViewColumn ("Doublons", cell, text=2)
        tree.append_column (col)

        # On met en couleur une ligne sur 2.
        tree.set_rules_hint (True)

        # On le remplit et on selectionne le premier élément.
        self.update_treeview_list_search ()



    def init_toolbar(self):
        """
        Set toolbar properties and buttons.
        """
        
        # Les positions des boutons spécifiques à une recherche sont stockés
        # dans un tableau pour etre ensuite activé/désactivé par la fonction
        # set_toolbar_search_mode(). Ils sont marqués (RECHERCHE) .
        self.toolbar_search_buttons = []

        # -----------------------
        # Fonctions
        # -----------------------
        
        def new_search (widget):
            self.interface.get_object ('notebook_main').set_current_page (4)

        def show_help (widget):
            self.interface.get_object ('notebook_main').set_current_page (2)

        def show_aboutdialog (widget):
            # On créé une fonction qui sera appellée lorsque la boite de dialog
            # sera fermée. Nous procédons de cette manière pour ne pas bloquer
            # la fenetre principale lors de l'apparation de la boite de dialog.
            def on_response (dialog, response):
                dialog.hide ()
            
            about = self.interface.get_object ('aboutdialog')
            about.connect ('response', on_response)
            about.show ()

        def add_separator (toolbar, pos=-1):
            # Ajouter un séparateur.
            sep = gtk.SeparatorToolItem ()
            sep.show ()
            toolbar.insert (sep, pos)
            

        # -----------------------
        # Barre de gauche
        # -----------------------

        toolbar = self.interface.get_object ("toolbar_left")

        # Bouton nouvelle recherche.
        tb = gtk.ToolButton (gtk.STOCK_NEW)
        tb.set_tooltip_text ('Nouvelle recherche')
        tb.connect ("clicked", new_search)
        tb.show ()
        toolbar.insert (tb, -1)

        # (RECHERCHE) Bouton 'Suspendre la recherche'. Si cliqué, ce bouton sera
        # remplacé par 'Reprendre la recherche'.
        self.tb_stop_search = True
        tb = gtk.ToolButton (gtk.STOCK_MEDIA_PAUSE)
        tb.set_tooltip_text ('Suspendre la recherche')
        tb.connect ("clicked", self.on_tb_stop_search_clicked)
        tb.show ()
        toolbar.insert (tb, -1)
        self.toolbar_search_buttons.append (toolbar.get_item_index (tb))

        # Séparateur.
        add_separator (toolbar)
	
        # Bouton UNDO (Annuler).
        tb = gtk.ToolButton (gtk.STOCK_UNDO)
        tb.set_tooltip_text ("Annuler l'action")
        tb.show ()
        toolbar.insert (tb, -1)
        
        # Bouton REDO (Refaire).
        tb = gtk.ToolButton (gtk.STOCK_REDO)
        tb.set_tooltip_text ("Refaire l'action")
        tb.show ()
        toolbar.insert (tb, -1)

        # Séparateur.
        add_separator (toolbar)

        # (RECHERCHE) Bouton 'Valider la recherche'.
        tb = gtk.ToolButton (gtk.STOCK_APPLY)
        tb.set_label ("Appliquer les changements")
        tb.set_tooltip_text ('Valider la recherche')
        tb.set_is_important (True)
        tb.show ()
        toolbar.insert (tb, -1)
        self.toolbar_search_buttons.append (toolbar.get_item_index (tb))

        # -----------------------
        # Barre de droite
        # -----------------------

        toolbar = self.interface.get_object ("toolbar_right")

        # Bouton aide
        tb = gtk.ToolButton (gtk.STOCK_HELP)
        tb.set_tooltip_text ("Consulter l'aide")
        tb.connect ("clicked", show_help)
        tb.show ()
        toolbar.insert (tb, -1)

        # Bouton à propos.
        tb = gtk.ToolButton (gtk.STOCK_ABOUT)
        tb.set_tooltip_text ('A propos de JustOneFile')
        tb.connect ("clicked", show_aboutdialog)
        tb.show ()
        toolbar.insert (tb, -1)

        add_separator (toolbar)

        # Bouton quitter.
        tb = gtk.ToolButton (gtk.STOCK_QUIT)
        tb.set_tooltip_text ('Quitter JustOneFile')
        tb.connect ("clicked", self.on_windowJustonefile_destroy)
        tb.show ()
        toolbar.insert (tb, -1)

        self.set_toolbar_search_mode (False)


    def init_preferences(self):
        """
        Initialize the self.prefs variable.
        """

        self.prefs = preferences.load ('./.preferences.cfg')
        
        if not self.prefs:
            print 'Impossible de charger la configuration.'
            print 'Arret du programme.'
            exit (0)


    def init_newsearch(self):
        """
        Initialize the new search tab widgets.
        """

        # On ajoute un FileChooserButton au notebook_choosedir.
        dialog = gtk.FileChooserDialog ('Choisir un dossier',
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        button = gtk.FileChooserButton (dialog)
        button.show ()

        nb = self.interface.get_object ('notebook_choosedir')
        nb.prepend_page (button)
        nb.set_current_page (0)


    def update_treemenu_content(self):
        """
        Update the treemenu content.
        """
        
        # On prend touts les titres des onglets et on les mets dans le modèle du
        # treeview 'menu'.

        nb = self.interface.get_object ('notebook_main')
        tree = self.interface.get_object ('treeview_menu')
        model = tree.get_model ()
        cursor = tree.get_cursor ()[0]

        if not tree.row_expanded (3):
            return

        # On supprime toute les recherches.
        for i in xrange (1, model.iter_n_children (self.search_iter)):
            it = model.get_iter_from_string ('3:1')
            model.remove (it)

        # Et on ajoute toutes les recherche, a partir des onglets. Donc si il y à
        # des nouvelles, elles seront rajoutées.
        for i in xrange (5, nb.get_n_pages ()):
            text = nb.get_tab_label_text (nb.get_nth_page (i))
            model.append (self.search_iter, [text])

        # On replace le curseur. Si il n'y en avais pas, on le met au début.
        if cursor is None:
            tree.set_cursor (0)
        else:
            tree.set_cursor (cursor)


    def update_treeview_list_search(self):
        """
        Get the list of all search and display it in the treeview.
        """
        
        tree = self.interface.get_object ('treeview_list_search')
        model = tree.get_model ()
        show_done = self.interface.get_object ('tb_search_done').get_active ()
        show_runing = self.interface.get_object ('tb_search_runing').get_active ()
        
        # On sauvegarde le curseur
        cursor = tree.get_cursor ()[0]

        # On liste toutes les recherches et ont les affiches dans le treeview
        # avec les informations nécéssaires.
        model.clear ()
        for s in self.list_search:
            # On détermine si la recherche doit etre afficher selon les critères
            # de tri.
            if s.done and show_done: pass
            elif not s.done and show_runing: pass
            else: continue

            # Et construit les informations à afficher.
            name = s.path
            if s.done: name += ' (Terminée)'
            else: name += ' (En cours ...)'
            progress = str (int (s.progress * 100)) + '%'
            
            model.append ([name, progress, s.nb_dbl])

        # On restaure le curseur.
        if len (model) > 0:
            if cursor is None:
                tree.set_cursor (0)
            else:
                tree.set_cursor (cursor)


    def set_toolbar_search_mode(self, mode):
        """
        Enabled or disabled the search controls buttons.
        
        Arguments:
        - `mode`: A boolean for enabled or disabled the mode.
        """

        # Les boutons de controls de recherche sont les boutons spécifiques
        # a un onglet de recherche. Ils sont définit lors de l'initialisation
        # de la toolbar. La liste de leur position est stocké dans
        # self.toolbar_search_buttons

        toolbar = self.interface.get_object ('toolbar_left')
        for pos in self.toolbar_search_buttons:
            item = toolbar.get_nth_item (pos)
            item.set_sensitive (mode)


    def update_searchs_infos(self):
        """
        Update the search infos and display its into the interface.
        """

        # (Cette fonction est appellée à intervalles régulier.)

        for s in self.list_search:
            s.update_infos ()

            # Si la recherche est terminée, on enlève le processus.
            if s.done: s.join ()

            # On modifie le titre de l'onglet en fonction de la progression.
            if s.progress < 0:
                title = '(...)'
            else:
                title = str (int (s.progress * 100)) + '%'

            s.tab.set_pb (s.progress)
            s.tab.set_action (s.action)
            title += '  ' + s.path
            s.tab.set_title (title)
            
            s.tab.add_dbl (s.new_dbl)

        # On rafraichit le menu et la liste des recherches.
        self.update_treemenu_content ()
        self.update_treeview_list_search ()
        
        return True


    def apply_prefs(self):
        """
        Apply the préférences.
        """

        # On applique les préférences.
        # Pour chaque entrée dans self.prefs, on change les choses associées en
        # fonction de la valeur.
        
        # -----------------------
        # Affichage
        # -----------------------

        # La barre de menu (True -> visible, False -> cachée).
        widget = self.interface.get_object ('menubar')
        if self.prefs['menu_bar']:
            widget.show ()
        else:
            widget.hide ()


        # La barre d'outils (True -> visible, False -> cachée).
        widget = (self.interface.get_object ('toolbar_left'),
                  self.interface.get_object ('toolbar_right'))
        if self.prefs['tool_bar']:
            widget[0].show ()
            widget[1].show ()
        else:
            widget[0].hide ()
            widget[1].hide ()


        # Mode 'Onglets' : on enlève le treeview menu et on affiche les onglets.
        widget = self.interface.get_object ('notebook_main')
        widget.set_show_tabs (self.prefs['tabs_mode'])

        widget = self.interface.get_object ('treeview_menu')
        if self.prefs['tabs_mode']:
            widget.hide ()
        else:
            widget.show ()


    # -----------------------
    # Signaux
    # -----------------------


    # -----------------------
    # Fenetre
    # -----------------------

    def on_windowJustonefile_destroy(self, widget):
        """
        Call when the window was destroy
        
        Arguments:
        - `widget`: The widget who send the signal
        """

        # On termine toutes les recherches
        for s in self.list_search:
            s.terminate ()

        gtk.main_quit ()


    def on_treeview_menu_cursor_changed(self, widget):
        """
        Display the associated page in the main notebook.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """

        # On prend le chemin de la selection et si on additionne tout les
        # numéros, on obtient la position de la page qu'il faut afficher.

        path = widget.get_cursor ()[0]
        if path is None:
            return

        pos = (path[0])
        if len (path) > 1:
            pos += (path[1] + 1)

        nb = self.interface.get_object ('notebook_main')
        if pos == nb.get_current_page ():
            return

        nb.set_current_page (pos)

        # On active ou désactive le toolbar search mode si l'onglet est
        # un onglet de recherche.
        if pos > 4:
            self.set_toolbar_search_mode (True)
        else:
            self.set_toolbar_search_mode (False)


    def on_notebook_main_switch_page(self, widget, page, page_index):
        """
        Refresh and select the treeview menu.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # On prend la page et on construit le chemin en fonction.

        tree = self.interface.get_object ('treeview_menu')
        # Si la position est plus petite que 4, alors le chemin est simple
        # Sinon, cela veut dire que le chemin serait alors (3, page_index - 4)
        if page_index < 4:
            path = (page_index,)
        else:
            tree.expand_row ((3), False)
            path = (3, page_index - 4)

        # Si on ne gère pas sa, on a un appelle récursif (car le changement
        # de surseur ordonne un changement d'onglet, qui ordonne a nouveau un
        # changement de curseur ...).
        if tree.get_cursor ()[0] == path:
            return

        tree.set_cursor (path)


    # -----------------------
    # Onglet de recherche
    # -----------------------

    def on_tb_stop_search_clicked(self, tb):
        """
        Call when the Stop search toolbutton's was clicked.
        """
        
        # Si l'état de la recherche est stopée, on affiche 'Reprendre'
        # sinon on affiche 'Suspendre'.
        
        # Comme les mécanisme de recherche ne sont pas encore implémentés,
        # ce bouton est juste (pour le moment) un bouton de démonstration.
        # On vas donc juste inverser l'état du bouton lors du clic.
        # Penser à une meilleure implémentation.

        if self.tb_stop_search:
            # On affiche 'Reprendre'
            tb.set_stock_id (gtk.STOCK_MEDIA_PLAY)
            tb.set_tooltip_text ('Reprendre la recherche')
            self.tb_stop_search = False
        else:
            # On affiche 'Suspendre'
            tb.set_stock_id (gtk.STOCK_MEDIA_PAUSE)
            tb.set_tooltip_text ('Suspendre la recherche')
            self.tb_stop_search = True


    # -----------------------
    # Onglet 'Accueil'
    # -----------------------

    def on_button_home_begin_new_search_clicked(self, widget):
        """
        Display the new search's tab.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """

        # L'onglet 'Nouvelle recherche' est toujour en 5èm position.
        self.interface.get_object ('notebook_main').set_current_page (4)


    def on_button_home_preferences_clicked(self, widget):
        """
        Display the préférences tab's
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # L'onglet 'Préférence' est toujour en 2èm position.
        self.interface.get_object ('notebook_main').set_current_page (1)


    # -----------------------
    # Onglet 'Nouvelle recherche'
    # -----------------------
    
    def on_button_start_search_clicked(self, widget):
        """
        Start a new search : add a tab and lauch search.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """

        nb = self.interface.get_object ('notebook_main')
        nb_path = self.interface.get_object ('notebook_choosedir')

        # Selon la page active, on prend la valeur du champ de texte ou la valeur
        # du filechooserbutton.
        if nb_path.get_current_page () == 0:
            path = nb_path.get_nth_page (0).get_filename ()
        else:
            path = self.interface.get_object ('entry_textpath').get_text ()


        # On test si le chemin est valide.
        if not os.path.isdir (path):
            print 'Erreur : le chemin doit etre un dossier.'
            return

        s = search.Search (path)
        s.tab.set_title (str (int (s.progress)) + '%  ' + path)
        self.list_search.append (s)

        nb.append_page (s.tab.main_box, s.tab.label_title)

        # On selectionne la page
        self.update_treemenu_content ()
        nb.set_current_page (-1)

        s.start ()              # On commence la recherche.


    def on_tb_textpath_toggled(self, widget):
        """
        Display/hide the entry 'textpath' and set his value.
        """

        if widget.get_active ():
            self.interface.get_object ('notebook_choosedir').set_current_page (1)
        else:
            self.interface.get_object ('notebook_choosedir').set_current_page (0)

        # On change le chemin.
        cb = self.interface.get_object ('notebook_choosedir').get_nth_page (0)
        self.interface.get_object ('entry_textpath').set_text (cb.get_filename ())
 
