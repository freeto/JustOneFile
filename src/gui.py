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
from src import search, preferences, treemenu


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

        treeview = treemenu.TreeMenu (self.interface.get_object ('notebook_main'))
        self._treemenu = treeview
        treeview = treeview.get_treeview ()

        self.interface.get_object ('scrolledwin_menu').add_with_viewport (treeview)
        return


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
        
        def new_search (tb):
            self.interface.get_object ('notebook_main').set_current_page (3)

        def call_set_search_state (tb):
            self.set_search_state (tb.get_active ())
            
        def show_aboutdialog (widget):
            # Méthode qui permet de rendre la boite de dialogue non-bloquante.
            def on_response (dialog, response):
                dialog.hide ()
            
            about = self.interface.get_object ('aboutdialog')
            about.connect ('response', on_response)
            about.show ()
            

        # -----------------------
        # Barre de gauche
        # -----------------------

        toolbar = self.interface.get_object ("toolbar_left")

        # Bouton 'Nouvelle recherche'
        tb = self.interface.get_object ('left_tb_new_search')
        tb.connect ('clicked', new_search)

        # (RECHERCHE) Bouton 'Mettre en pause la recherche'
        tb = self.interface.get_object ('left_tb_control_search')
        tb.connect ('toggled', call_set_search_state)
        self.set_search_state (False)
        self.toolbar_search_buttons.append (toolbar.get_item_index (tb))        

        # (RECHERCHE) Bouton 'Valider la recherche'
        tb = self.interface.get_object ('left_tb_apply')
        self.toolbar_search_buttons.append (toolbar.get_item_index (tb))

        # -----------------------
        # Barre de droite
        # -----------------------

        toolbar = self.interface.get_object ("toolbar_right")

        # Bouton 'À propos'
        tb = self.interface.get_object ('right_tb_about')
        tb.connect ("clicked", show_aboutdialog)

        # Bouton 'Quitter'
        tb = self.interface.get_object ('right_tb_quit')
        tb.connect ("clicked", self.on_windowJustonefile_destroy)

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

        # Met à jour la liste des recherches.
        self.update_treeview_list_search ()
        self._treemenu.refresh ()
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


    def set_search_state(self, state):
        """
        Set the selected search state's.
        
        Arguments:
        - `state`: The new search state's.
        """        

        # Si l'état de la recherche est stopée, on affiche 'Reprendre'
        # sinon on affiche 'Suspendre'.
        
        # Comme les mécanisme de recherche ne sont pas encore implémentés,
        # ce bouton est juste (pour le moment) un bouton de démonstration.
        # On vas donc juste inverser l'état du bouton lors du clic.
        # Penser à une meilleure implémentation.

        tb = self.interface.get_object ('left_tb_control_search')
        if state:
            tb.set_tooltip_text ('Reprendre la recherche')
        else:
            tb.set_tooltip_text ('Suspendre la recherche')


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
        self.interface.get_object ('notebook_main').set_current_page (3)


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


        # Test si le chemin est valide.
        if not os.path.isdir (path):
            print 'Erreur : le chemin doit etre un dossier.'
            return

        s = search.Search (path)
        s.tab.set_title (str (int (s.progress)) + '%  ' + path)
        self.list_search.append (s)

        nb.append_page (s.tab.main_box, s.tab.label_title)

        nb.set_current_page (-1) # Selectionne la page.
        s.start ()               # Démarre la recherche.


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
 
