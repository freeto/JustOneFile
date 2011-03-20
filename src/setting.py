#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       setting.py
#       
#       Copyright 2011 RADISSON Olivier <oly@oly-portable>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


#########
# - Contains 
#		* Classes : _PrefSetting(path=None)
#		* Variable : Preference _DefaultPrefPath _ReservedAttribute _DefaultPref
#
# - Description
#
#   Le but est d'avoir une variable accessible partout contenant tout les paramètres de l'utilisateur
#		Pour cela une classe s'occupe de sérializer toutes les variables comprises dans l'objet PrefSetting
#   et de l'enregistrer
#
#  - How To 
#
#		Preference.MA_VAR = VALUE   # assigne VALUE à MA_VAR
#   Preference.save(path=None) # Sauvegarde la convelle configuration des preferences
#   Preference.load(path=None) # Charge la configuration 
#		Preference.autosave(True) # Sauvegarde la configuration à chaque changement
###########

import cPickle as Pickle
from os.path import exists

_DefaultPrefPath = ".jofi.conf"
_ReservedAttribute = ["_reserved","_path","_autosave","_dict"] # liste des paramètre interne
_DefaultPref = {"prefpath":_DefaultPrefPath}

class _PrefSetting(object):
	""" Classe premettant de gérer facilement les préférences utilsiateur """
	
	def __init__(self,path=None):
		if path is None:
			path = _DefaultPrefPath
		self._path = path
		self._autosave = False # If true, save for all changes 
		self._dict = dict()
		
	def load(self,path=None):
		if path is None:
			path = self._path
		with open(path,'r') as fichier:
			try:
				obj = Pickle.load(fichier) # Charge l'objet du fichier dans obj
				if obj.is_setting_object():
					self = obj 	# Si l'objet charger est bien un objet setting alors on remplace le courant par celui chargé
				return True
			except:
				return False
		return False

	def save(self,path=None):
		if path is None:
			path = self._path
		with open(path,'w') as fichier:
			try:
				Pickle.dump(self,fichier,protocol=-1) # Charge l'objet courant dans le fichier
				return True
			except:
				return False
		return False
		
	def is_setting_object(self):
		""" To know if the pickle object is a setting object or not """
		return True

	def __getattr__(self,name): # Acces aux attributs 
		if name in self._dict.keys():
			return self._dict[name]
		else:
			return None
	
	def autosave(self,etat):
			self._autosave = etat
	
	def __setattr__(self,name,value): # Modification d'un attribut
		if name not in _ReservedAttribute:
			self._dict[name] = value
			if self._autosave:
				self.save()
		else:
			object.__setattr__(self,str(name),value)

def CreateDefaultPreference():
	""" Crée le fichier de configuration si celui-ci n'existe pas """
	pref = _PrefSetting()
	pref._dict = _DefaultPref
	return pref 

if exists(_DefaultPrefPath):
	Preference = _PrefSetting()
else:
	Preference = CreateDefaultPreference()

if __name__ == '__main__': pass

