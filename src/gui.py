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
Gui class with functions
"""

import pygtk, gtk, os


class WindowJustonefile():
    """
    The JustOneFile GUI
    """
    
    def __init__(self):
        """
        Initialize 
        """

        # On contruit le fenetre à partie du fichier glade
        self.interface = gtk.Builder()
        self.interface.add_from_file('justOneFile.glade')
        self.interface.connect_signals(self)

        # Initialisation des widgets de la fenetre
        self.controls_buttons = self.interface.get_object('hbox_controls_buttons')
        self.init_treeview_menu()
        self.init_treeview_dbl()
        self.init_toolbar()
        self.init_statusbar()



    def init_treeview_menu(self):
        """
        Init the window's treeview menu
        """
        
        # Le treeview_menu est en fait le treeview a gauche qui sert de menu.
        # A ne pas confondre avec le menu du haut.
        self.tree_menu = self.interface.get_object('treeview_menu')

        # On créé le modèle du menu
        self.modele_treemenu = gtk.TreeStore(str)
        self.tree_menu.set_model(self.modele_treemenu)

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("", cell, text=0)
        col.set_expand(True)
        self.tree_menu.append_column(col)

        # On modifie ces propriétés
        self.tree_menu.set_headers_visible(False)

        # On le remplit et on selectionne le premier item.
        self.update_treemenu_content()
        self.tree_menu.set_cursor (0)


    def init_treeview_dbl(self):
        """
        Initilize the treeview of duplicates files
        """
        
        # Ce treeview contient la liste des fichiers en doubles sous forme
        # d'arbre.

        self.tree_dbl = self.interface.get_object('treeview_dbl')

        # On créé le modèle du menu
        self.modele_treedbl = gtk.TreeStore(str)
        self.tree_dbl.set_model(self.modele_treedbl)

        # On créée la colone (texte)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Doublons", cell, text=0)
        col.set_expand(True)
        self.tree_dbl.append_column(col)

        # Et on le remplit
        iter = self.modele_treedbl.append(None, ['Fichier 1.txt'])
        self.modele_treedbl.append(iter, ['Autre fichier 1.txt'])
        iter = self.modele_treedbl.append(None, ['background.jpg'])
        self.modele_treedbl.append(iter, ['arbres.jpg'])



    def init_toolbar(self):
        """
        Input buttons in toolbar
        """
        
        toolbar = self.interface.get_object("toolbar")

        # On ajoute les boutons

        # Bouton nouvelle recherche
        tb = gtk.ToolButton(gtk.STOCK_NEW)
        tb.set_tooltip_text('Nouvelle recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        # Bouton suprimme recherche
        tb = gtk.ToolButton(gtk.STOCK_REMOVE)
        tb.set_tooltip_text('Supprime la recherche')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)

        # Bouton 'Stopper la recherche'. Si cliqué, ce bouton sera remplacé par
        # 'Reprendre la recherche'
        self.tb_stop_search = True
        tb = gtk.ToolButton(gtk.STOCK_MEDIA_STOP)
        tb.set_tooltip_text('Stopper la recherche')
        tb.connect("clicked", self.on_tb_stop_search_clicked)
        tb.show()
        toolbar.insert(tb, -1)

        # Séparateur
        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)
	
        # Bouton UNDO (Annuler)
        tb = gtk.ToolButton(gtk.STOCK_UNDO)
        tb.set_tooltip_text("Annuler l'action")
        tb.show()
        toolbar.insert(tb, -1)
        
        # Bouton REDO (Refaire)
        tb = gtk.ToolButton(gtk.STOCK_REDO)
        tb.set_tooltip_text("Refaire l'action")
        tb.show()
        toolbar.insert(tb, -1)
        
        # Séparateur
        sep = gtk.SeparatorToolItem()
        sep.show()
        toolbar.insert(sep, -1)
        
        # Bouton quitter
        tb = gtk.ToolButton(gtk.STOCK_QUIT)
        tb.set_tooltip_text('Quitter JustOneFile')
        tb.connect("clicked", gtk.main_quit)
        tb.show()
        toolbar.insert(tb, -1)


    def init_statusbar(self):
        """
        Initialize the windows status bar
        """
        
        sb = self.interface.get_object('statusbar')

        # Context à modifier, un context pour une recherche + contexte pour les
        # actions du programme (enregistrer ...)
        self.sb_context = sb.get_context_id('Search status bar')
        
        sb.push(self.sb_context, 'Construction de la liste ...')


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

        nb = self.interface.get_object('notebook_controlbar')

        # On fait un petit test pour savoir si il est utile de changer de page.
        cur_page = nb.get_current_page()
        if (visibility and cur_page == 1) or (not visibility and cur_page == 0):
            return

        if visibility:
            nb.next_page()
            self.interface.get_object('entry_search').grab_focus()
        else:
            nb.prev_page()


    def update_treemenu_content(self):
        """
        Set content of the treeview menu model with the main notebook.
        """
        
        # On prend touts les titres des onglets et on les mets dans le modèle du
        # treeview 'menu'.

        nb = self.interface.get_object('notebook_main')

        # On parcour tous les onglets et on prend son titre, que l'on place dans le
        # modèle. Les 4 premiers onglets sont à la base  0, les autre dans le 4em.
        self.modele_treemenu.clear()
        for i in xrange(0, 4):
            text = nb.get_tab_label_text(nb.get_nth_page(i))
            iter = self.modele_treemenu.append (None, [text])

        # On liste toutes les recherches. A noté que le premier onglet sera
        # toujour 'Nouvelle recherche' et que le dernier ne doit pas etre
        # affiché car il contient juste le modèle pour un onglet 'Recherche'.
        for i in xrange(4, nb.get_n_pages() - 1):
            text = nb.get_tab_label_text(nb.get_nth_page(i))
            self.modele_treemenu.append (iter, [text])

            
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
        
        gtk.main_quit()


    def on_treeview_menu_cursor_changed(self, widget):
        """
        Display the associated page in the main notebook.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """

        # On prend le chemin de la selection et si on additionne tout les numéros,
        # on obtient la position de la page qu'il faut afficher.
        # (Peut-etre qu'il y a une méthode encore plus simple.)

        path = widget.get_cursor()[0]
        pos = path[0]
        if len(path) > 1:
            pos += path[1] + 1
        
        self.interface.get_object('notebook_main').set_current_page(pos)


    def on_notebook_main_switch_page(self, widget, page, page_index):
        """
        Refresh and select the treeview menu.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # On prend la page et on construit le chemin en fonction.

        # Si la position est plus petite que 4, alors le chemin est simple
        # Sinon, cela veut dire que le chemin serait alors (3, page_index - 4)
        if page_index < 4:
            path = (page_index,)
        else:
            self.tree_menu.expand_row((3), False)
            path = (3, page_index - 4)

        # Si on ne gère pas sa, on a un appelle récursif (car le changement
        # de surseur ordonne un changement d'onglet, qui ordonne a nouveau un
        # changement de curseur ...).
        if self.tree_menu.get_cursor()[0] == path:
            return

        self.tree_menu.set_cursor(path)


    # -----------------------
    # Onglet de recherche
    # -----------------------

    def on_tb_search_toggled(self, widget):
        """
        Call when the search toggle button was toggle.

        Arguments:
        - `widget`: The widget who send the signal
        """

        self.set_searchbar_visibility(widget.get_active())


    def on_tb_stop_search_clicked(self, tb):
        """
        Call when the Stop search toolbutton's was clicked.
        """
        
        # Si l'état de la recherche est stopée, on affiche 'Reprendre'
        # sinon on affiche 'Stopper'.
        
        # Comme les mécanisme de recherche ne sont pas encore implémentés,
        # ce bouton est juste (pour le moment) un bouton de démonstration.
        # On vas donc juste inverser l'état du bouton lors du clic.
        # Penser à une meilleure implémentation.

        if self.tb_stop_search:
            # On vas afficher Reprendre.
            tb.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            tb.set_tooltip_text('Reprendre la recherche')
            self.tb_stop_search = False
        else:
            # On vas afficher Stopper
            tb.set_stock_id(gtk.STOCK_MEDIA_STOP)
            tb.set_tooltip_text('Stopper la recherche')
            self.tb_stop_search = True


    def on_treeview_dbl_focus_in_event(self, widget, event):
        """
        Call when the treeview_dbl get focus.
        Hide the search_bar
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # /!\ Fonction pas très propre, à réorganiser /!\

        # On test si la barre de recherche est active et on agit en fonction.
        ac = self.interface.get_object('notebook_controlbar').get_current_page()
        
        if ac == 1:
            self.interface.get_object('tb_search').clicked()


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
        self.interface.get_object('notebook_main').set_current_page(4)


    def on_button_home_preferences_clicked(self, widget):
        """
        Display the préférences tab's
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
        
        # L'onglet 'Préférence' est toujour en 2èm position.
        self.interface.get_object('notebook_main').set_current_page(1)


    # -----------------------
    # Onglet 'Nouvelle recherche'
    # -----------------------

    def on_button_start_search_clicked(self, widget):
        """
        Start a new search : add a tab and lauch search.
        
        Arguments:
        - `widget`: The widget who send the signal.
        """
