'''
Supplementary information plots.
VMP 2023-02-08: light refactoring, should be cleaned more (has been re-run)
'''

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import configuration as cn
from tqdm import tqdm 

# preprocessing 
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
configurations = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# find probability for different attributes
probability_list = []
for i in range(20): 
    column_n = configurations[:, i]
    column_n_idx = np.where(column_n > 0)
    column_probs = configuration_probabilities[column_n_idx]
    mean_prob = np.mean(column_probs)
    std_prob = np.std(column_probs)
    probability_list.append((i+1, mean_prob, std_prob))
probability_df = pd.DataFrame(probability_list, columns = ['question_id', 'mean(prob)', 'std(prob)'])

# match with questions 
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')
question_reference = question_reference[['question_id', 'question']]
question_probability = question_reference.merge(probability_df, on = 'question_id', how = 'inner')
question_probability = question_probability.sort_values('mean(prob)').reset_index()

global_mean = np.mean(configuration_probabilities)

fig, ax = plt.subplots(dpi = 300, figsize = (4, 6))
for i, row in question_probability.iterrows(): 
    x = row['mean(prob)']
    x_err = row['std(prob)']
    plt.scatter(x, i, color = 'tab:blue')
plt.yticks(np.arange(0, 20, 1), 
           question_probability['question'].values,
           size = 15)
plt.vlines(global_mean, ymin = 0, ymax = 20, color = 'tab:red', ls = '--')
plt.xlabel('Mean probability')
plt.savefig('../fig/pdf/feature_stability.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/feature_stability.svg', bbox_inches = 'tight')

## look at standard deviation (much larger than actual difference?) ##
# ...

# most enforced practices
d_enforcement = pd.read_csv('../data/analysis/enforcement_observed.csv')
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')
observed_configs = d_enforcement['config_id'].unique().tolist()

# takes a couple of minutes
# not the most efficient approach
top_five_list = []
for config_idx in tqdm(observed_configs): 
    ConfObj = cn.Configuration(config_idx, 
                            configurations, 
                            configuration_probabilities)

    df = ConfObj.transition_probs_to_neighbors(question_reference)
    df = df.sort_values('transition_prob', ascending = False).head(5).reset_index()
    df = df[['question_id', 'question']]
    df['config_id'] = config_idx 
    top_five_list.append(df)

top_five_df = pd.concat(top_five_list)
top_five_df = top_five_df.groupby('question').size().reset_index(name = 'count')
top_five_df = top_five_df.sort_values('count', ascending = True).reset_index()

# plot this 
fig, ax = plt.subplots(dpi = 300, figsize = (4, 6))
for i, row in top_five_df.iterrows(): 
    x = row['count']
    plt.scatter(x, i, color = 'tab:blue')
plt.yticks(np.arange(0, 20, 1), 
           top_five_df['question'].values, 
           size = 15)
plt.xlabel('n(enforced first five)')
plt.savefig('../fig/pdf/number_enforced_first_five.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/number_enforced_first_five.svg', bbox_inches = 'tight')

top_five_df = top_five_df.assign(percent_top_five = lambda x: (x['count']/260)*100)
top_five_df.sort_values('count', ascending = False)

# tables
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')