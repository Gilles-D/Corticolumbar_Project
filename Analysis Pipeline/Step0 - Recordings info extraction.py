# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 22:20:13 2023

@author: Gilles Delbecq


Extract TTL indexes from intan files for a given animal
Saves it as a pickle file (recording_info) in the signal folder

Parameters to edit :
    - pipeline_path : folder containing intanutils folder
    - session_folder_path : animal folder containing intan recordings session


Update 19/11 :seems to be working well with spikeinterface version 0.100.8

"""

import os

"""
############ Parameters to edit ############
"""

pipeline_path = r"C:\Users\Gil\Documents\GitHub\Corticolumbar_Project\Analysis Pipeline"
session_folder_path = r'I:/8513'

#%%Functions

def Get_TTL_idx(file_list):
    """
Gets the indexes of TTL pulses in the recordings and saves the information in a pickle file.

Args:
    file_list (list): A list of strings containing the file paths of the recordings.

Returns:
    saves it in a pickle file ttl_idx.pickle
"""
    import sys
    import time
    import os
    import numpy as np
    import pickle
    #load intan class
    sys.path.append(pipeline_path)

    from intanutil.read_header import read_header
    from intanutil.get_bytes_per_data_block import get_bytes_per_data_block
    from intanutil.read_one_data_block import read_one_data_block
    from intanutil.notch_filter import notch_filter
    from intanutil.data_to_result import data_to_result
    
    def read_data(filename):
        tic = time.time()
        fid = open(filename, 'rb')
        filesize = os.path.getsize(filename)
        header = read_header(fid)
        print('Found {} amplifier channel{}.'.format(
            header['num_amplifier_channels'], plural(header['num_amplifier_channels'])))
        print('Found {} auxiliary input channel{}.'.format(
            header['num_aux_input_channels'], plural(header['num_aux_input_channels'])))
        print('Found {} supply voltage channel{}.'.format(
            header['num_supply_voltage_channels'], plural(header['num_supply_voltage_channels'])))
        print('Found {} board ADC channel{}.'.format(
            header['num_board_adc_channels'], plural(header['num_board_adc_channels'])))
        print('Found {} board digital input channel{}.'.format(
            header['num_board_dig_in_channels'], plural(header['num_board_dig_in_channels'])))
        print('Found {} board digital output channel{}.'.format(
            header['num_board_dig_out_channels'], plural(header['num_board_dig_out_channels'])))
        print('Found {} temperature sensors channel{}.'.format(
            header['num_temp_sensor_channels'], plural(header['num_temp_sensor_channels'])))
        print('')
        # Determine how many samples the data file contains.
        bytes_per_block = get_bytes_per_data_block(header)
        # How many data blocks remain in this file?
        data_present = False
        bytes_remaining = filesize - fid.tell()
        if bytes_remaining > 0:
            data_present = True
        if bytes_remaining % bytes_per_block != 0:
            raise Exception(
                'Something is wrong with file size : should have a whole number of data blocks')
        num_data_blocks = int(bytes_remaining / bytes_per_block)
        num_amplifier_samples = header['num_samples_per_data_block'] * \
            num_data_blocks
        num_aux_input_samples = int(
            (header['num_samples_per_data_block'] / 4) * num_data_blocks)
        num_supply_voltage_samples = 1 * num_data_blocks
        num_board_adc_samples = header['num_samples_per_data_block'] * \
            num_data_blocks
        num_board_dig_in_samples = header['num_samples_per_data_block'] * \
            num_data_blocks
        num_board_dig_out_samples = header['num_samples_per_data_block'] * \
            num_data_blocks
        record_time = num_amplifier_samples / header['sample_rate']
        if data_present:
            print('File contains {:0.3f} seconds of data.  Amplifiers were sampled at {:0.2f} kS/s.'.format(
                record_time, header['sample_rate'] / 1000))
        else:
            print('Header file contains no data.  Amplifiers were sampled at {:0.2f} kS/s.'.format(
                header['sample_rate'] / 1000))
        if data_present:
            # Pre-allocate memory for data.
            print('')
            print('Allocating memory for data...')
            data = {}
            if (header['version']['major'] == 1 and header['version']['minor'] >= 2) or (header['version']['major'] > 1):
                data['t_amplifier'] = np.zeros(
                    num_amplifier_samples, dtype=np.int_)
            else:
                data['t_amplifier'] = np.zeros(
                    num_amplifier_samples, dtype=np.uint)
            data['amplifier_data'] = np.zeros(
                [header['num_amplifier_channels'], num_amplifier_samples], dtype=np.uint)
            data['aux_input_data'] = np.zeros(
                [header['num_aux_input_channels'], num_aux_input_samples], dtype=np.uint)
            data['supply_voltage_data'] = np.zeros(
                [header['num_supply_voltage_channels'], num_supply_voltage_samples], dtype=np.uint)
            data['temp_sensor_data'] = np.zeros(
                [header['num_temp_sensor_channels'], num_supply_voltage_samples], dtype=np.uint)
            data['board_adc_data'] = np.zeros(
                [header['num_board_adc_channels'], num_board_adc_samples], dtype=np.uint)
            # by default, this script interprets digital events (digital inputs and outputs) as booleans
            # if unsigned int values are preferred(0 for False, 1 for True), replace the 'dtype=np.bool_' argument with 'dtype=np.uint' as shown
            # the commented line below illustrates this for digital input data; the same can be done for digital out
            #data['board_dig_in_data'] = np.zeros([header['num_board_dig_in_channels'], num_board_dig_in_samples], dtype=np.uint)
            data['board_dig_in_data'] = np.zeros(
                [header['num_board_dig_in_channels'], num_board_dig_in_samples], dtype=np.bool_)
            data['board_dig_in_raw'] = np.zeros(
                num_board_dig_in_samples, dtype=np.uint)
            data['board_dig_out_data'] = np.zeros(
                [header['num_board_dig_out_channels'], num_board_dig_out_samples], dtype=np.bool_)
            data['board_dig_out_raw'] = np.zeros(
                num_board_dig_out_samples, dtype=np.uint)
            # Read sampled data from file.
            print('Reading data from file...')
            # Initialize indices used in looping
            indices = {}
            indices['amplifier'] = 0
            indices['aux_input'] = 0
            indices['supply_voltage'] = 0
            indices['board_adc'] = 0
            indices['board_dig_in'] = 0
            indices['board_dig_out'] = 0
            print_increment = 10
            percent_done = print_increment
            for i in range(num_data_blocks):
                read_one_data_block(data, header, indices, fid)
                # Increment indices
                indices['amplifier'] += header['num_samples_per_data_block']
                indices['aux_input'] += int(
                    header['num_samples_per_data_block'] / 4)
                indices['supply_voltage'] += 1
                indices['board_adc'] += header['num_samples_per_data_block']
                indices['board_dig_in'] += header['num_samples_per_data_block']
                indices['board_dig_out'] += header['num_samples_per_data_block']
                fraction_done = 100 * (1.0 * i / num_data_blocks)
                if fraction_done >= percent_done:
                    print('{}% done...'.format(percent_done))
                    percent_done = percent_done + print_increment
            # Make sure we have read exactly the right amount of data.
            bytes_remaining = filesize - fid.tell()
            if bytes_remaining != 0:
                raise Exception('Error: End of file not reached.')
        # Close data file.
        fid.close()
        if (data_present):
            print('Parsing data...')
            # Extract digital input channels to separate variables.
            for i in range(header['num_board_dig_in_channels']):
                data['board_dig_in_data'][i, :] = np.not_equal(np.bitwise_and(
                    data['board_dig_in_raw'], (1 << header['board_dig_in_channels'][i]['native_order'])), 0)
            # Extract digital output channels to separate variables.
            for i in range(header['num_board_dig_out_channels']):
                data['board_dig_out_data'][i, :] = np.not_equal(np.bitwise_and(
                    data['board_dig_out_raw'], (1 << header['board_dig_out_channels'][i]['native_order'])), 0)
            # Scale voltage levels appropriately.
            data['amplifier_data'] = np.multiply(
                0.195, (data['amplifier_data'].astype(np.int32) - 32768))      # units = microvolts
            data['aux_input_data'] = np.multiply(
                37.4e-6, data['aux_input_data'])               # units = volts
            data['supply_voltage_data'] = np.multiply(
                74.8e-6, data['supply_voltage_data'])     # units = volts
            if header['eval_board_mode'] == 1:
                data['board_adc_data'] = np.multiply(
                    152.59e-6, (data['board_adc_data'].astype(np.int32) - 32768))  # units = volts
            elif header['eval_board_mode'] == 13:
                data['board_adc_data'] = np.multiply(
                    312.5e-6, (data['board_adc_data'].astype(np.int32) - 32768))  # units = volts
            else:
                data['board_adc_data'] = np.multiply(
                    50.354e-6, data['board_adc_data'])           # units = volts
            data['temp_sensor_data'] = np.multiply(
                0.01, data['temp_sensor_data'])               # units = deg C
            # Check for gaps in timestamps.
            num_gaps = np.sum(np.not_equal(
                data['t_amplifier'][1:]-data['t_amplifier'][:-1], 1))
            if num_gaps == 0:
                print('No missing timestamps in data.')
            else:
                print('Warning: {0} gaps in timestamp data found.  Time scale will not be uniform!'.format(
                    num_gaps))
            # Scale time steps (units = seconds).
            data['t_amplifier'] = data['t_amplifier'] / header['sample_rate']
            data['t_aux_input'] = data['t_amplifier'][range(
                0, len(data['t_amplifier']), 4)]
            data['t_supply_voltage'] = data['t_amplifier'][range(
                0, len(data['t_amplifier']), header['num_samples_per_data_block'])]
            data['t_board_adc'] = data['t_amplifier']
            data['t_dig'] = data['t_amplifier']
            data['t_temp_sensor'] = data['t_supply_voltage']
            # If the software notch filter was selected during the recording, apply the
            # same notch filter to amplifier data here.
            if header['notch_filter_frequency'] > 0 and header['version']['major'] < 3:
                print('Applying notch filter...')
                print_increment = 10
                percent_done = print_increment
                for i in range(header['num_amplifier_channels']):
                    data['amplifier_data'][i, :] = notch_filter(
                        data['amplifier_data'][i, :], header['sample_rate'], header['notch_filter_frequency'], 10)
                    fraction_done = 100 * (i / header['num_amplifier_channels'])
                    if fraction_done >= percent_done:
                        print('{}% done...'.format(percent_done))
                        percent_done += print_increment
        else:
            data = []
        # Move variables to result struct.
        result = data_to_result(header, data, data_present)
        print('Done!  Elapsed time: {0:0.1f} seconds'.format(time.time() - tic))
        return result
    def plural(n):
        if n == 1:
            return ''
        else:
            return 's'

    def TTL_detection(TTL_starts_idx, sampling_rate):
        """
        Detects start indexes and times of TTL pulses.

        Args:
            TTL_starts_idx (numpy.ndarray): A 1D numpy array containing the start indexes of TTL pulses.
            sampling_rate (float): The sampling rate of the recording.

        Returns:
            tuple: A tuple containing two arrays:
                - start_indexes (numpy.ndarray): A 1D numpy array containing the start indexes of each phase of TTL pulses.
                - start_times (numpy.ndarray): A 1D numpy array containing the start times (in seconds) of each phase of TTL pulses.
        """
        # Calculate the difference between consecutive elements
        diff_indices = np.diff(TTL_starts_idx)
        phase_indices = np.where(diff_indices != 1)[0]
        
        phase_end_indices = np.where(diff_indices != 1)[0]
        
        start_indexes = TTL_starts_idx[phase_indices] #fin de ttl
        
        start_indexes = np.insert(start_indexes, 0, TTL_starts_idx[0])
        start_times = start_indexes / sampling_rate

        return start_indexes, start_times
    


    def trouver_changements_indices(tableau):
        diff = np.diff(tableau.astype(int))
        return np.where(diff != 0)[0] + 1
   
    
    save_dir = os.path.dirname((os.path.dirname(file_list[0])))
    save_path= rf"{save_dir}/ttl_idx.pickle"
    
    if os.path.exists(save_path):
        print("Recordings info file exists")
        print("Loading info file...")
        TTL_info = pickle.load(open(save_path, "rb"))
        
    else:
        print("Recordings info file does not exist")
        print("Getting info...")

        
        # RHD file reading
        multi_recordings, recordings_lengths, multi_stim_idx, multi_frame_idx, frame_start_delay = [], [], [], [], []
        
        # Concatenate recordings
        for record in file_list:
            reader = read_data(record)
            signal = reader['amplifier_data']
            recordings_lengths.append(len(signal[0]))
            multi_recordings.append(signal)
            
            stim_idx = reader['board_dig_in_data'][0]  # Digital data for stim of the file
            multi_stim_idx.append(stim_idx)  # Digital data for stim of all the files
            
            frame_idx = reader['board_dig_in_data'][1]  # Get digital data for mocap ttl
            multi_frame_idx.append(frame_idx)  # Digital data for mocap ttl of all the files
        
                
        # Get sampling freq
        sampling_rate = reader['frequency_parameters']['amplifier_sample_rate']
        
        anaglog_signal_concatenated = np.hstack(multi_recordings)  # Signal concatenated from all the files
        digital_stim_signal_concatenated = np.hstack(multi_stim_idx)  # Digital data for stim concatenated from all the files
        digital_mocap_signal_concatenated = np.hstack(multi_frame_idx)
        
        try:
            # stim_ttl_on = TTL_detection((np.where(digital_stim_signal_concatenated == True))[0], sampling_rate)
            stim_ttl_on_off = trouver_changements_indices(digital_stim_signal_concatenated)
            
        except:
            print("No stim ttl")
            stim_ttl_on_off=np.array([])
        
        try:
            # mocap_ttl_on = TTL_detection((np.where(digital_mocap_signal_concatenated == True))[0], sampling_rate)
            mocap_ttl_on_off  = trouver_changements_indices(digital_mocap_signal_concatenated)
        except:
            print("No video ttl")
            mocap_ttl_on_off=np.array([])

        
        recordings_lengths_cumsum = np.cumsum(np.array(recordings_lengths) / sampling_rate)
                                              
        # Return: recording length, recording length cumsum, digital signals 1 and 2 (in full or logical?)
        # Save them in a pickle
        
        recordings_info = {
            "recordings_files" : file_list,
            'recordings_length': recordings_lengths,
            'recordings_length_cumsum': recordings_lengths_cumsum,
            'sampling_rate': sampling_rate,
            'digital_stim_signal_concatenated': digital_stim_signal_concatenated,
            'digital_mocap_signal_concatenated': digital_mocap_signal_concatenated,
            'stim_ttl_on':stim_ttl_on_off,
            'mocap_ttl_on':mocap_ttl_on_off 
        }
    
    try:
        pickle.dump(recordings_info, open(save_path, "wb"))
    except:
        print("Can't save. ttl_idx.pickle already exists ?")
    
    print('Done')
    return 


def list_recording_folders(path):
    """
    List all recording files (.rhd) in the specified directory and its subdirectories.
    
    Parameters:
        path (str): The directory path to search for recording files.
        
    Returns:
        list: A list of paths to all recording files found.
    """
    import os
    import glob
    subfolders = [ f.path for f in os.scandir(path) if f.is_dir() ]
    
    return subfolders


def list_recording_files(path):
    """
    List all recording files (.rhd) in the specified directory and its subdirectories.
    
    Parameters:
        path (str): The directory path to search for recording files.
        
    Returns:
        list: A list of paths to all recording files found.
    """
    import os
    import glob
    fichiers = [fichier for fichier in glob.iglob(path + '/**/*', recursive=True) if not os.path.isdir(fichier) and fichier.endswith('.rhd')]
    
    return fichiers

#%% Main script
recording_folders = list_recording_folders(session_folder_path)

for folder in recording_folders:
    print(folder)
    file_list = list_recording_files(folder)
    Get_TTL_idx(file_list)
    
