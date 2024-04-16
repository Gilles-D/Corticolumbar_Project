## <u>Step0- Recordings info extraction</u>

<u>Usage :</u>

- Extract TTL indexes from intan files for a given animal

- Saves it as a pickle file (recording_info) in the signal folder

<u>Parameters to edit :</u>

- pipeline_path : folder containing intanutils folder

- session_folder_path : animal folder containing intan recordings session

<u>Output :</u>

- **ttl_idx.pickle** containing :
  
  - recordings_files
  
  - recordings_length
  
  - recordings_length_cumsum
  
  - sampling_rate
  
  - digital_stim_signal_concatenated
  
  - digital_mocap_signal_concatenated
  
  - stim_ttl_on
  
  - mocap_ttl_on

## <u>Step1- Concatenate</u>

<u>Usage :</u>

- Concatenate signal from intan files for a given session

- Saves concatenated signal for spikeinterface analysis in binary format 

<u>Parameters to edit :</u>

- animal_id, session_name, saving_name : identification information for the animal and session

- rhd_folder : folder containing the raw intan data

- probe_path : json file containing information of the probe

- saving_dir : folderto save concatenated signals

- freq_min, freq_max : Filtering frequencies

- MOCAP_200Hz_notch : Notch filtering for the MOCAP artefacts

- remove_stim_artefact : Stim artefacts removing for opto-stimulations

- OPTIONAL : excluded_sites : to exclude problematic channels
  (can be identified during a first concatenation using the signal plottings)

<u>Output :</u>

- **Concatenated signal** of the session, readable by spikeinterface



## <u>Step2- Spikesorting</u>

<u>Usage :</u>

- Perform spikinterface spikesorting

<u>Parameters to edit :</u>

- concatenated_signals : concatenated signals in binary format (one or multiple sessions)

- spikesorting_results_folder, concatenated_files_folder

<u>Output :</u>

- **Sorting results** (spikeinterface)



## <u>Step3- Curation</u>

<u>Usage :</u>

- 

<u>Parameters to edit :</u>

- 

- 

<u>Output :</u>

- 
