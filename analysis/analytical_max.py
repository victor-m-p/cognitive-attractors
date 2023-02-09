'''
Find the analytical maximum likelihood path and terminations.
VMP 2023-02-07: Refactored from original code. 
VMP 2023-02-07: Re-run with refactored code. 
'''

# import packages
import pandas as pd 
import numpy as np 
import configuration as cn 
from tqdm import tqdm 

# load documents
entry_maxlikelihood = pd.read_csv('../data/preprocessing/entry_maxlikelihood.csv')
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
configurations = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# get all unique maxlikelihood configurations 
unique_configurations = entry_maxlikelihood['config_id'].unique().tolist()

# helper function to get neighbor index
def get_neighbor_idx(configuration, index):
    """get neighbors of a configuration

    Args:
        configuration (cn.Configuration): instance of the Configuration class
        index (int): index at which to flip

    Returns:
        np.Array: array of neighbor indices
    """
    flip = configuration.flip_at_index(index)
    flipid = np.array([np.where((configuration.states == flip).all(1))[0][0]])[0]
    return flipid 

# function to find analytical max likelihood path
def find_analytical_ml_path(unique_configurations, configurations, configuration_probabilities, threshold=0.5, max_timestep=100):
    """find all analytical max likelihood paths for all unique configurations

    Args:
        unique_configurations (lst): list of unique (maximum likelihood) configurations
        configurations (np.Array): Array of all 2**20 configurations
        configuration_probabilities (np.Array): Array of all 2**20 configuration probabilities
        threshold (float, optional): threshold for transition. Defaults to 0.5.
        max_timestep (int, optional): maximum number of timesteps (never hits 100). Defaults to 100.
    """
    
    for focal_idx in tqdm(unique_configurations): 
        original_idx = focal_idx
        sample_list = []
        for t in range(max_timestep):
            ConfObj = cn.Configuration(focal_idx,
                                       configurations, 
                                       configuration_probabilities)
            p_move = ConfObj.p_move(summary = False)
            # find indices and values 
            index = np.argmax(p_move)
            value = p_move[index]
            # if there are indices then log, otherwise pass 
            if value > threshold: 
                neighbor_idx = get_neighbor_idx(ConfObj,
                                                index)
                # we log information
                sample_list.append((t, focal_idx, neighbor_idx, value))
                focal_idx = neighbor_idx
            else: 
                break 
        sample_df = pd.DataFrame(sample_list,
                                 columns = ['timestep', 'config_from', 
                                            'config_to', 'weight'])
        sample_df.to_csv(f'../data/analysis/max_attractor/idx{original_idx}.csv', index = False)
    
find_analytical_ml_path(unique_configurations, configurations, configuration_probabilities, threshold=0.5, max_timestep=100)