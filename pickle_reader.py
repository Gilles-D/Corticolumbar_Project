# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:51:36 2024

@author: Gil

Load a pickle file
To see the content : check or print the dict 'recording_info'

"""

import pickle
import tkinter as tk
from tkinter import filedialog

# Création d'une instance de Tkinter
root = tk.Tk()
# root.withdraw()  # Cacher la fenêtre principale de Tkinter

# Ouvrir la fenêtre de dialogue pour choisir un fichier
pickle_path = filedialog.askopenfilename(
    title="Sélectionnez un fichier pickle",
    filetypes=[("Pickle files", "*.pickle;*.pkl")]  # Vous pouvez adapter les types de fichiers
)

# Vérification si un chemin a été sélectionné
if pickle_path:
    # Chargement des informations depuis le fichier pickle
    with open(pickle_path, "rb") as file:
        recording_info = pickle.load(file)
    # Vous pouvez ajouter des opérations avec recording_info ici
else:
    print("Aucun fichier sélectionné.")

