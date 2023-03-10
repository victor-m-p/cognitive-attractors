'''
VMP: Updated data. 
Number of fixed traits. 
VMP 2023-02-08: light cleanup
'''

# COGSCI23
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import arviz as az
import configuration as cn 

# plotting setup
small_text = 12
large_text = 18

# read data
d_enforcement = pd.read_csv('../data/analysis/enforcement_observed.csv')
d_enforcement['prob_remain'] = (1-d_enforcement['prob_move'])*100

# we need the median as well
median_remain = d_enforcement.groupby('n_fixed_traits')['prob_remain'].median().tolist()

# label some points 
highlight_configs = [1027975, 652162]
entry_maxlikelihood = pd.read_csv('../data/preprocessing/entry_maxlikelihood.csv')
entry_maxlikelihood = entry_maxlikelihood[['config_id', 'entry_name']]
entry_maxlikelihood = entry_maxlikelihood[entry_maxlikelihood['config_id'].isin(highlight_configs)]
entry_sample = entry_maxlikelihood.groupby('config_id').sample(n=1, random_state = 1)
entry_sample = entry_sample.merge(d_enforcement, on = 'config_id', how = 'inner')
upper_line = entry_sample[entry_sample['config_id'] == highlight_configs[0]]
lower_line = entry_sample[entry_sample['config_id'] == highlight_configs[1]]

# HDI plot 
hdi_list = []
for n_traits in d_enforcement['n_fixed_traits'].unique(): 
    n_traits_subset = d_enforcement[d_enforcement['n_fixed_traits'] == n_traits]
    n_traits_remain = n_traits_subset['prob_remain'].values
    hdi_95 = list(az.hdi(n_traits_remain, hdi_prob = 0.95))     
    hdi_50 = list(az.hdi(n_traits_remain, hdi_prob = 0.5))
    data_list = [n_traits] + hdi_95 + hdi_50 
    hdi_list.append(data_list)
hdi_df = pd.DataFrame(hdi_list, columns = ['n_fixed_traits',
                                           'hdi_95_l',
                                           'hdi_95_u',
                                           'hdi_50_l',
                                           'hdi_50_u'])
n_fixed_traits = hdi_df['n_fixed_traits'].tolist()
hdi_95_l = hdi_df['hdi_95_l'].tolist()
hdi_95_u = hdi_df['hdi_95_u'].tolist()
hdi_50_l = hdi_df['hdi_50_l'].tolist()
hdi_50_u = hdi_df['hdi_50_u'].tolist()

# hdi plot
fig, ax = plt.subplots(figsize = (7, 5), dpi = 300)
plt.fill_between(n_fixed_traits, hdi_95_l, hdi_95_u, color = 'tab:blue', alpha = 0.3)
plt.fill_between(n_fixed_traits, hdi_50_l, hdi_50_u, color = 'tab:blue', alpha = 0.5)
plt.plot(lower_line['n_fixed_traits'].values, 
         lower_line['prob_remain'].values, 
         color = '#152238',
         ls = '--'
         )
plt.plot(n_fixed_traits, median_remain, color = '#152238', linewidth = 2)
plt.annotate('Santal', 
             (6.4, 84), 
             color = '#152238', 
             size = 15,
             #rotation = 53
             )
plt.xticks(np.arange(0, 20, 1))
plt.xlabel('Number of traits fixed', size = small_text)
plt.ylabel(r'$\mathrm{P_{remain}}$', size = small_text)
plt.savefig('../fig/pdf/enforcement_hdi.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/enforcement_hdi.svg', bbox_inches = 'tight')

# find medians and HDI intervals 
hdi_df['median'] = median_remain

# load documents
configuration_probabilities = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
configurations = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')

configuration = 652162
conf = cn.Configuration(configuration,
                        configurations, 
                        configuration_probabilities)
p_move = conf.p_move(summary = False)

question_reference['p_move'] = p_move
question_reference['held_belief'] = conf.configuration
question_reference = question_reference.drop(columns = ['question_id', 'question_id_drh', 'question_drh'])
question_reference = question_reference.sort_values('p_move', ascending = False)