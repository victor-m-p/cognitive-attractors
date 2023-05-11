'''
VMP 2023-05-09:
Calculating the stability index for traits.
'''

import numpy as np 
from fun import bin_states 
import pandas as pd 

# setup
def match_probabilities(question_idx: int,
                        states: np.array,
                        p: np.array):
    '''
    question_idx: column index of the question 
    '''

    n_states = states.shape[0]
    n_splits = 2**(question_idx+1)
    n_states_split = int(n_states/n_splits)

    p_neg = []
    p_pos = []
    n_states_running = 0
    while n_states_running < n_states: 

        idx_neg = np.array(range(n_states_running, 
                                n_states_split+n_states_running))

        idx_pos = np.array(range(n_states_running+n_states_split, 
                                n_states_running+n_states_split*2))

        p_neg += list(p[idx_neg])
        p_pos += list(p[idx_pos])

        n_states_running += n_states_split*2

    matched_p = np.column_stack((p_neg, p_pos))
    return matched_p 

# setup 
n_nodes = 20

# load data 
d = pd.read_csv('../data/preprocessing/data_flattened.csv')
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')

# function for calculating stability index
p = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
config = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# loop over all indexes: 
indexes = range(n_nodes)
matched_p_lst = []
for i in indexes: 
    matched_p = match_probabilities(i, config, p)
    matched_p_lst.append(matched_p)

## actually calculate the average stabiliy index ##
# first where we take base-probability into account
stability_idx_norm = []
for i in indexes: 
    pi = matched_p_lst[i]
    rowsum = np.sum(pi, axis=1)
    marginal = np.sum(rowsum * np.abs(np.log(pi[:, 0] / pi[:, 1])))
    stability_idx_norm.append(marginal)
stability_idx_norm = np.array(stability_idx_norm)

# then when we do not take base-rate probability into account
stability_idx_raw = []
for i in indexes:
    pi = matched_p_lst[i]
    rowsum = np.sum(np.abs(np.log(pi[:, 0] / pi[:, 1])))
    stability_idx_raw.append(rowsum)

stability_idx_raw = np.array(stability_idx_raw)/2**19

## try to plot it nicely ## 
import matplotlib.pyplot as plt
questions_shorthand = question_reference['question'].values

# for the normalized data
d_stability_norm = pd.DataFrame({
    'question': questions_shorthand,
    'stability_idx': stability_idx_norm
})
d_stability_norm = d_stability_norm.sort_values('stability_idx', ascending = False).reset_index()
fig, ax = plt.subplots(figsize=(5, 6.5), dpi=300)
plt.barh(d_stability_norm.index, d_stability_norm['stability_idx'])
plt.yticks(d_stability_norm.index, d_stability_norm['question'],
           size=15)
plt.xlabel(r'$\mathrm{rigidity(\sigma_i) = \sum_{c \in C} P(c) \; | \; log \; \frac{p(\sigma_i = -1|c)}{p(\sigma_i = +1|c)} \;|}$',
           size=15)
plt.savefig('../fig/pdf/rigidity_idx_normalized.pdf', bbox_inches = 'tight')
plt.savefig('../fig/svg/rigidity_idx_normalized.svg', bbox_inches = 'tight')

# for the non-normalized data (notice that labels are wrong from here on out; old convention)
d_stability_raw = pd.DataFrame({
    'question': questions_shorthand,
    'stability_idx': stability_idx_raw
})
d_stability_raw = d_stability_raw.sort_values('stability_idx', ascending = False).reset_index()
fig, ax = plt.subplots()
plt.barh(d_stability_raw.index, d_stability_raw['stability_idx'])
plt.yticks(d_stability_raw.index, d_stability_raw['question'])
plt.xlabel(r'stability index: $\frac{1}{|C|} \sum_{c \in C} | \; log \; \frac{p(\sigma = -1|c)}{p(\sigma = +1|c)} \;|$')
plt.suptitle('Stability Index')

# is it e**number: 
# does not seem like it for child sacrifice, unclear. 
x = matched_p_lst[16]
y = x[:, 0] / x[:, 1] # seems like in the 10-20, 0.1-0.2 range...
2.71**5 # 146 ....?

# temporary; 
# what is the base-rate for reincarnation in this world?
idx_reincarnation = 5
config_idx_reincarnation = np.where(config[:, idx_reincarnation] == 1)
p_reincarnation = p[config_idx_reincarnation]
p_reincarnation = np.sum(p_reincarnation)