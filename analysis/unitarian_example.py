import numpy as np 
import pandas as pd 

# loads
entry_config = pd.read_csv('../data/preprocessing/entry_configuration_master.csv')
question_reference = pd.read_csv('../data/preprocessing/question_reference.csv')
configs = np.loadtxt('../data/preprocessing/configurations.txt', dtype = int)

# find UUs
UU_idx = entry_config[entry_config['entry_name'].str.contains('Unitar')]['config_id'].values

# find out which features we have here that are not consistent internally
UU_fluid = []
for i in UU_idx: 
    A = configs[UU_idx[0]] == configs[i]
    difference = np.where(A == False)[0]
    UU_fluid.append(difference)

# 3, 4, 5 
questions = question_reference['question'].tolist()

questions[3] # spirit-body

''' Yes
Many Unitarian Universalists believe in a distinction between 
the body and mind or spirit, but this is not part of the doctrine 
of the organization. In my fieldwork there were several lectures 
given about Near Death Experiences, which were often accounts of 
validation that the mind can leave the body during these liminal moments.
'''

''' No
Because Unitarian Univeralists doctrine does not dictate an answer 
to the body/mind divide, there are also avowed materalists among 
the congregations. In my research I encountered many people who 
believed that the brain/body was the mind and that they were not f
undamentally able to be separated.
'''

questions[4] # belief in afterlife (actually coded as both yes / no)

''' Yes
Again, it is important to note that the Unitarian Universalist 
organizations do not specify beliefs or doctrine with respect 
to the afterlife. In my interviews with leadership within the UUA, 
they specified that their role was to facilitate individuals' 
personal beliefs about life after death and to not direct them 
in any particular direction. The only specific item that they 
would not support is a negative conception of afterlife that was 
harmful to the person (e.g. a belief in Hell).
'''
''' No
Some Unitarian Universalists do not belief in an afterlife. 
I interviewed several people who believed that when our 
physical bodies die we return to nothing. Unitarian Universalism 
only takes the stance that the afterlife is not negative, but does 
not affirm any particular form of afterlife beyond that.
'''
questions[5] # reincarnation in this world 

''' Yes
Some individuals within the Unitarian Universalist community 
self-describe as Buddhists and believe in reincarnation in that 
respect, but others believe in a more Westernized version of 
reincarnation. This is not a tenet of Unitarian Universalist doctrine, 
but is a common belief within the community.
'''

''' No
While some people do subscribe to notions of reincarnation, 
some people believe in a final resting place for an afterlife 
and others believe that nothing happens after death. Unitarian 
Universalist doctrine does not support or deny belief in reincarnation, 
but allows individuals to choose their own belief.
'''