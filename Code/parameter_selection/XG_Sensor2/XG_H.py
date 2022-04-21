# -*- coding: utf-8 -*-
# Finding the best parameters for XGradient boost

import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, partial, rand
from xgboost.sklearn import XGBRegressor
import time
import openpyxl
import os


# Loading data
path = './data_management/Sensor_2_Sensor_Weather_Combination.xlsx'
path_save = './data_para/Sensor_2_Sensor_Weather_Combination_Para.xlsx'
     
columns_s = ['Sailing speed', 'Displcement', 'Trim', 
             'Wind speed', 'Wind direction (Rel.)', 
             'Combined wave height', 'Combined Wave period','Combined wave direction (Rel.)', 
             'Sea current speed', 'Sea current direction (Rel.)',
             'Sea water temperature', 'Fuel consumption rate']

# read data
data_o = pd.read_excel(path)

# select data 
Train_data = data_o[columns_s]    
data_len   = len(Train_data)
delete_len = int(data_len*0.1)

# Load variable data and target data
x = np.array(Train_data.iloc[:, 0:11])                        # Load variable data
y = np.array(Train_data.iloc[:, 11])                          # Load target data
   
# set parameters
A = range(10,301)
B = range(2,17)

space = {'n_estimators':hp.choice('n_estimators', A),
         'learning_rate':hp.uniform('learning_rate', 0.00001,1.0),
         'max_depth':hp.choice('max_depth', B),
         'min_child_weight':hp.uniform('min_child_weight', 0,10),
         'gamma':hp.uniform('gamma',0,2.0),
         'colsample_bytree':hp.uniform('colsample_bytree',0.1,1.0),
         'subsample':hp.uniform('subsample', 0.4,1.0),
         'reg_alpha':hp.uniform('reg_alpha', 0.0,2.0),
         'reg_lambda':hp.uniform('reg_lambda', 0.0,2.0)}

# Cross validation, parameter optimization
def fun(params):
    rfr = XGBRegressor(**params, random_state = 7, n_jobs = -1)
    met = cross_val_score(rfr, x_train, y_train, cv = 10, scoring = 'r2', n_jobs = -1).mean()
    return -met

List_1 = []
List_2 = []
List_3 = []
List_4 = []
List_5 = []
List_6 = []
List_7 = []
List_8 = []
List_9 = []
List_10 = []
List_11 = []
random_seed = []

for i in range(1,21):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = i)
    start = time.perf_counter()
    rstate = np.random.RandomState(7)
    trials = Trials()
    best = fmin(fun, space, algo = tpe.suggest, max_evals = 300, trials = trials, rstate = rstate)
    
    print("hyperopt", best)
    print("hyperopt",A[best['n_estimators']],best['learning_rate'],
          B[best['max_depth']],best['min_child_weight'],
          best['gamma'],best['colsample_bytree'], best['subsample'],
          best['reg_alpha'], best['reg_lambda'])
    
    best_params = {'n_estimators': A[best['n_estimators']],
                   'learning_rate': best['learning_rate'],
                   'max_depth': B[best['max_depth']], 
                   'gamma': best['gamma'], 
                   'min_child_weight': best['min_child_weight'], 
                   'colsample_bytree': best['colsample_bytree'],
                   'subsample': best['subsample'],
                   'reg_alpha':best['reg_alpha'],
                   'reg_lambda':best['reg_lambda']}
    
    acc = -fun(best_params)
    
    end = time.perf_counter()
    run_time = end-start
    print('Running time: %s Seconds'%(run_time))
    random_seed.append(i)
    List_1.append(A[best['n_estimators']])
    List_2.append(best['learning_rate'])
    List_3.append(B[best['max_depth']])
    List_4.append(best['min_child_weight'])
    List_5.append(best['gamma'])
    List_6.append(best['colsample_bytree'])
    List_7.append(best['subsample'])
    List_8.append(best['reg_alpha'])
    List_9.append(best['reg_lambda'])
    List_10.append(acc)
    List_11.append(run_time)


XG_H = pd.DataFrame()
XG_H['Random_seed'] = random_seed
XG_H['n_estimators'] = List_1
XG_H['learning_rate'] = List_2
XG_H['max_depth'] = List_3
XG_H['min_child_weight'] = List_4
XG_H['gamma'] = List_5
XG_H['colsample_bytree'] = List_6
XG_H['subsample'] = List_7
XG_H['reg_alpha'] = List_8
XG_H['reg_lambda'] = List_9
XG_H['score'] = List_10
XG_H['time'] = List_11

XG_H.to_excel(path_save, index=False)

print('Results saved')



