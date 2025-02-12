# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 16:55:51 2023

@author: MOCAP
"""

import pandas as pd
import numpy as np
import os

# df_instantaneous_rate = pd.read_excel('D:/ePhy/SI_Data/spikesorting_results/0026_02_08/kilosort3/curated/processing_data/instantaneous_rates.xlsx')

#%% Functions

def Check_Save_Dir(save_path):
    """
    Check if the save folder exists. If not, create it.

    Args:
        save_path (str): Path to the save folder.

    """
    import os
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)  # Create folder for the experiment if it does not already exist

    return

def Get_recordings_info(session_name, concatenated_signals_path, spikesorting_results_path):
    """
    Cette fonction récupère les informations d'enregistrement à partir d'un fichier de métadonnées
    dans le dossier de signaux concaténés.

    Args:
        session_name (str): Le nom de la session d'enregistrement.
        concatenated_signals_path (str): Le chemin vers le dossier contenant les signaux concaténés.
        spikesorting_results_path (str): Le chemin vers le dossier des résultats du tri des spikes.

    Returns:
        dict or None: Un dictionnaire contenant les métadonnées si la lecture est réussie,
        ou None si la lecture échoue.

    Raises:
        Exception: Si une erreur se produit pendant la lecture du fichier.

    """
    import pickle
    
    try:
        # Construire le chemin complet vers le fichier de métadonnées
        path = rf'{concatenated_signals_path}/{session_name}/'
        
        # Lire le fichier de métadonnées à l'aide de la bibliothèque pickle
        print("Lecture du fichier ttl_idx dans le dossier Intan...")
        metadata = pickle.load(open(rf"{path}/ttl_idx.pickle", "rb"))
        
    except Exception as e:
        # Gérer toute exception qui pourrait se produire pendant la lecture du fichier
        print("Aucune information d'enregistrement trouvée dans le dossier Intan. Veuillez exécuter l'étape 0.")
        metadata = None  # Aucune métadonnée disponible en cas d'erreur
    
    print('Terminé')
    return metadata


def list_recording_files(path, session):
    """
    List all CSV files containing the specified session in the name
    in the specified directory and its subdirectories.

    Parameters:
        path (str): The directory path to search for CSV files.
        session (str): The session to search for in the file names.

    Returns:
        list: A list of paths to CSV files containing the session in their name.
    """
    import os
    
    session = rf"_{session}_"

    csv_files = []
    for folderpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.lower().endswith(".xlsx") and session in filename and "Analysis" in filename:
                csv_files.append(os.path.join(folderpath, filename))

    return csv_files


#%%Parameters
session_name = '0022_01_08'
mocap_session = "01"

spikesorting_results_path = r"\\equipe2-nas1\Public\DATA\Gilles\Spikesorting_August_2023\SI_Data\spikesorting_results"
concatenated_signals_path = r'\\equipe2-nas1\Public\DATA\Gilles\Spikesorting_August_2023\SI_Data\concatenated_signals'

sorter_name = "kilosort3"

sorter_folder = rf'{spikesorting_results_path}/{session_name}/{sorter_name}'

mocap_data_folder = '//equipe2-nas1/Public/DATA/Gilles/Spikesorting_August_2023/SI_Data/mocap_files/Auto-comp'

sampling_rate = 20000
mocap_freq = 200
mocap_delay = 45 #frames


instantaneous_rate_bin_size = 1 #s
trageted_instantaneous_rate_bin_size = 0.005 #s


#%%
recordings_info = Get_recordings_info(session_name,concatenated_signals_path,spikesorting_results_path)

"""
Load mocap infos and TTL
"""
#Get animal number
animal = session_name.split('_')[0]        
print(rf"Loading MOCAP data for Mocap session {animal}_{mocap_session}")


#Get mocap_files from analysis folder (formated from previous step)
mocap_files = list_recording_files(rf"{mocap_data_folder}/{animal}/Analysis",mocap_session)
# print(rf"{len(mocap_files)} trials found")


#Get Mocap TTL indexes (slices one on two because 1 TTL appears twice with start and end of the ttl) and transform them in times
mocap_ttl = recordings_info['mocap_ttl_on'][::2]
mocap_ttl_times = mocap_ttl/sampling_rate
# print(rf"{len(mocap_ttl)} TTL found in recordings info")


#Compare the number of ttl with the number of files
if len(mocap_ttl) > len(mocap_files):
    print(rf"Be careful ! there are more TTL ({len(mocap_ttl)}) than mocap files ({len(mocap_files)})")
elif len(mocap_ttl) < len(mocap_files):
    print(rf"Be careful ! there are less TTL ({len(mocap_ttl)}) than mocap files ({len(mocap_files)})")
    
    
"""
Load Mocap data
"""

#Create a list that will regroup all the mocap data from each trial
whole_data_mocap = []

#Loop on all the ttl times
for i,ttl_time in enumerate(mocap_ttl_times):
    mocap_file = None
    trial = i+1         #i+1 because enumerates starts at 0 and trials at 1
    
    print(rf"Trial {trial}")
    
    #Loop on all mocap files    
    for file_path in mocap_files:
        trial_file = int(file_path.split("_")[-1].split('.')[0])    #Get the trial number of the FILE
        if trial_file == trial:                                     #and take it equals the current trial number of ttl
            mocap_file = file_path
         
    #If there is a mocap file for this trial, append it to the list whole_data_mocap
    if mocap_file is not None:
        mocap_data = pd.read_excel(mocap_file).iloc[:, 1:]
        
        #Create a time axis for this trial that starts at the ttl time of the trial
        #The mocap delay is removed here (time between the TTL is sent and the mocap starts)        
        trial_time_axis = (np.array(range(len(mocap_data)))/mocap_freq)+ttl_time-mocap_delay/mocap_freq
        
        mocap_data.insert(0,'time_axis',trial_time_axis)
        whole_data_mocap.append(mocap_data)
             

#Transform the list of dataframe in one big dataframe        
df_mocap_data_all = pd.concat(whole_data_mocap, axis=0)
        
savepath = rf"{sorter_folder}\curated\processing_data\Mocap_data.xlsx"
Check_Save_Dir(os.path.dirname((savepath)))

df_mocap_data_all.to_excel(savepath)


#%%Split by obstacle / catwalk
recordings_info = Get_recordings_info(session_name,concatenated_signals_path,spikesorting_results_path)

trial_info_path=rf"{spikesorting_results_path}/{session_name}/sessions_infos.xlsx"

trials_info = pd.read_excel(trial_info_path)

catwalk_trials = trials_info['trials'][trials_info['type'] == 'catwalk']
obstacle_trials = trials_info['trials'][trials_info['type'] == 'obstacle']
ladder_trials = trials_info['trials'][trials_info['type'] == 'ladder']


"""
Load Mocap data
"""
animal = session_name.split('_')[0]
print(rf"Loading MOCAP data for Mocap session {animal}_{mocap_session}")
mocap_files = list_recording_files(rf"{mocap_data_folder}/{animal}/Analysis",mocap_session)
# print(rf"{len(mocap_files)} trials found")

mocap_ttl = recordings_info['mocap_ttl_on'][::2]
# print(rf"{len(mocap_ttl)} TTL found in recordings info")

if len(mocap_ttl) > len(mocap_files):
    print(rf"Be careful ! there are more TTL ({len(mocap_ttl)}) than mocap files ({len(mocap_files)})")
elif len(mocap_ttl) < len(mocap_files):
    print(rf"Be careful ! there are less TTL ({len(mocap_ttl)}) than mocap files ({len(mocap_files)})")
    
mocap_ttl_times = mocap_ttl/sampling_rate



catwalk_data_mocap,obstacle_data_mocap,ladder_data_mocap = [],[],[]
for i,ttl_time in enumerate(mocap_ttl_times):
    mocap_file = None
    trial = i+1
    
    print(rf"Trial {trial}")
        
    for file_path in mocap_files:
        trial_file = int(file_path.split("_")[-1].split('.')[0])
        if trial_file == trial:
            mocap_file = file_path         
    
    if mocap_file is not None and trial in catwalk_trials:
        mocap_data = pd.read_excel(mocap_file).iloc[:, 1:]
                
        trial_time_axis = (np.array(range(len(mocap_data)))/mocap_freq)+ttl_time-mocap_delay/mocap_freq
        
        mocap_data.insert(0,'time_axis',trial_time_axis)
        catwalk_data_mocap.append(mocap_data)
        
    elif mocap_file is not None and trial in obstacle_trials:
        mocap_data = pd.read_excel(mocap_file).iloc[:, 1:]
                
        trial_time_axis = (np.array(range(len(mocap_data)))/mocap_freq)+ttl_time-mocap_delay/mocap_freq
        
        mocap_data.insert(0,'time_axis',trial_time_axis)
        obstacle_data_mocap.append(mocap_data)
        
    elif mocap_file is not None and trial in ladder_trials:
        mocap_data = pd.read_excel(mocap_file).iloc[:, 1:]
                
        trial_time_axis = (np.array(range(len(mocap_data)))/mocap_freq)+ttl_time-mocap_delay/mocap_freq
        
        mocap_data.insert(0,'time_axis',trial_time_axis)
        ladder_data_mocap.append(mocap_data)

if len(catwalk_data_mocap) > 0:
    df_mocap_catwalk = pd.concat(catwalk_data_mocap, axis=0)
    savepath_catwalk = rf"{sorter_folder}\curated\processing_data\Mocap_data_catwalk.xlsx"
    Check_Save_Dir(os.path.dirname((savepath_catwalk)))
    df_mocap_catwalk.to_excel(savepath_catwalk)    


if len(obstacle_data_mocap) > 0:
    df_mocap_obstacle = pd.concat(obstacle_data_mocap, axis=0)
    savepath_obstacle = rf"{sorter_folder}\curated\processing_data\Mocap_data_obstacle.xlsx"
    Check_Save_Dir(os.path.dirname((savepath_obstacle)))
    df_mocap_obstacle.to_excel(savepath_obstacle)    

    
if len(ladder_data_mocap) > 0:
    df_mocap_ladder = pd.concat(ladder_data_mocap, axis=0)
    savepath_ladder = rf"{sorter_folder}\curated\processing_data\Mocap_data_ladder.xlsx"
    Check_Save_Dir(os.path.dirname((savepath_ladder)))
    df_mocap_ladder.to_excel(savepath_ladder)   




 
