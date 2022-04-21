# -*- coding: utf-8 -*-
# Finding the best parameters for Extra Trees

import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import cross_val_score
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, partial, rand
import time
import openpyxl
import os

# Loading data
path = './data_management/Ship_S3_Voyage_Weather_Combination.xlsx'
path_save = './data_para/Ship_S3_Voyage_Weather_Combination_Para.xlsx'


columns_s = ['Sailing speed', 'Displacement', 'Trim', 
             'Wind speed', 'Wind direction (Rel.)', 
             'Swell height', 'Swell direction (Rel.)',
             'Wind wave height', 'Wind wave direction (Rel.)'
             'Combined wave height', 'Combined wave direction (Rel.)',  
             'Sea current speed', 'Sea current direction (Rel.)',
             'Sea water temperature', 'Fuel consumption rate']

# read data
data_o = pd.read_excel(path)

# select data
Train = data_o[columns_s]

# Load variable data and target data
x = np.array(Train.iloc[:, 0:14])                                   # Load variable data
y = np.array(Train.iloc[:, -1])                                     # Load target data
 
n_features = x.shape[1]
A = range(10,301)
B = range(2,31)
C = range(1,21)
D = range(2,21)
# E = range(1, n_features+1)
E = n_features

space = {'n_estimators':hp.choice('n_estimators', A),
         'max_depth':hp.choice('max_depth', B),
         'min_samples_leaf':hp.choice('min_samples_leaf', C),
         'min_samples_split':hp.choice('min_samples_split', D),
         'max_features':E}
         # 'max_features':hp.choice('max_features', E)}

# Cross validation, parameter optimization
def fun(params):
    rfr = ExtraTreesRegressor(**params, random_state = 7, n_jobs = -1)
    met = cross_val_score(rfr, x_train, y_train, cv = 10, scoring = 'r2', n_jobs = -1).mean()
    return -met

List_1 = []
List_2 = []
List_3 = []
List_4 = []
# List_5 = []
List_6 = []
List_7 = []
random_seed = []

for i in range(1,21):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = i)
    
    start = time.perf_counter()
    rstate = np.random.RandomState(7)
    trials = Trials()
    best = fmin(fun, space, algo = tpe.suggest, max_evals = 400, trials = trials, rstate = rstate)
    
    print("hyperopt", best)
    print("hyperopt",A[best['n_estimators']],
          B[best['max_depth']],C[best['min_samples_leaf']],
          D[best['min_samples_split']]), # E[best['max_features']])
    
    best_params = {'n_estimators': A[best['n_estimators']],
                   'max_depth': B[best['max_depth']], 
                   # 'max_features': E[best['max_features']], 
                   'min_samples_leaf': C[best['min_samples_leaf']], 
                   'min_samples_split': D[best['min_samples_split']]}
    
    acc = -fun(best_params)
    
    end = time.perf_counter()
    run_time = end-start
    print('Running time: %s Seconds'%(run_time))
    random_seed.append(i)
    List_1.append(A[best['n_estimators']])
    List_2.append(B[best['max_depth']])
    List_3.append(C[best['min_samples_leaf']])
    List_4.append(D[best['min_samples_split']])
    # List_5.append(E[best['max_features']])
    List_6.append(acc)
    List_7.append(run_time)

ET_H = pd.DataFrame()
ET_H['Random_seed'] = random_seed
ET_H['n_estimators'] = List_1
ET_H['max_depth'] = List_2
ET_H['min_samples_leaf'] = List_3
ET_H['min_samples_split'] = List_4
# ET_H['max_features'] = List_5
ET_H['score'] = List_6
ET_H['time'] = List_7

ET_H.to_excel(path_save, index=False)

print('Results saved')
