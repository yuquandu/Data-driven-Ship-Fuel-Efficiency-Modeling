# -*- coding: utf-8 -*-
# XGradient boost regression

from sklearn.model_selection import learning_curve
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, explained_variance_score
import joblib
import openpyxl
import os
import xgboost as xgb
from xgboost.sklearn import XGBRegressor
import time

# Loading data
path_rep  = './data_management/Sensor_2_Sensor_Weather_Combination.xlsx'
path_hyp  = './data_para/Sensor_2_Sensor_Weather_Combination_Para.xlsx'
path_save = './data_result/'

filename = path_rep.split('/')[-1].split('.')[0]

# import data
data_o = pd.read_excel(path_rep) 

# select data    
columns_s = ['Sailing speed', 'Displcement', 'Trim', 
             'Wind speed', 'Wind direction (Rel.)', 
             'Combined wave height', 'Combined Wave period','Combined wave direction (Rel.)', 
             'Sea current speed', 'Sea current direction (Rel.)',
             'Sea water temperature', 'Fuel consumption rate']
        
Train_data  = data_o[columns_s]


# Load variable data and target data   
x = np.array(Train_data.iloc[:, 0:11])                                   # Load variable data
y = np.array(Train_data.iloc[:, 11])                                     # Load target data

# load parameter data
Hyper = pd.read_excel(path_hyp)
Hyper_data = pd.DataFrame(Hyper)
Hyper_data.drop(Hyper_data.columns[0], axis=1, inplace=True)                   # Delete the first column (index)
best_n = Hyper_data['n_estimators']
best_rate = Hyper_data['learning_rate']
best_depth = Hyper_data['max_depth']
best_weight = Hyper_data['min_child_weight']
best_gamma = Hyper_data['gamma']
best_bytree = Hyper_data['colsample_bytree']
best_subsample = Hyper_data['subsample']
best_reg_alpha = Hyper_data['reg_alpha']
best_reg_lambda = Hyper_data['reg_lambda']

random_seed = []
E_0_Train = []
E_0_Test = []
E_1_Train = []
E_1_Test = []
E_2_Train = []
E_2_Test = []
E_3_Train = []
E_3_Test = []
E_4_Train = []
E_4_Test = []
E_5_Train = []
E_5_Test = []
E_6_Train = []
E_6_Test = []
E_7_Train = []
E_7_Test = []
time_list = []
impor = np.zeros(shape=(20,11))

def mape(y_true, y_pred):
    return np.mean(np.abs((y_pred - y_true) / y_true)) * 100

for i in range(1,21):
    # Segment training and test datasets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = i)
    start = time.perf_counter()
    # XGradient boost regression model
    rfr = XGBRegressor(n_estimators = int(best_n[i-1]), random_state = 7, learning_rate = float(best_rate[i-1]),
                       max_depth = int(best_depth[i-1]), min_child_weight = float(best_weight[i-1]), 
                       gamma = float(best_gamma[i-1]), colsample_bytree = float(best_bytree[i-1]), 
                       subsample = float(best_subsample[i-1]), reg_alpha = float(best_reg_alpha[i-1]), 
                       reg_lambda = float(best_reg_lambda[i-1]), n_jobs = -1)
    # train
    rfr.fit(x_train, y_train)                                              # Change y_train to 1 line, regression training
    # save model to file
    model_name = path_save + filename + '_XG_' + str(i)
    print(model_name)
    joblib.dump(rfr, path_save+model_name)
    # test
    rfr_ytrain = rfr.predict(x_train)
    rfr_y_predict = rfr.predict(x_test)                                            # Regression prediction
    end = time.perf_counter()
    run_time = end-start
    # Variable importance
    importances = rfr.feature_importances_
    # Evaluation of XGradient boost regression models
    ACC = rfr.score(x_train,y_train)                                               # Train dataset accuracy
    EV = rfr.score(x_test, y_test)                                                 # Test dataset accuracy
    
    Train_R2 = r2_score(y_train, rfr_ytrain)                                       # Train dataset R-squared
    Train_A_R2 = 1-(((1-Train_R2)*(len(x_train)-1))/(len(x_train)-x_train.shape[1]-1))
    R2 = r2_score(y_test, rfr_y_predict)                                           # Test dataset R-squared
    A_R2 = 1-(((1-R2)*(len(x_test)-1))/(len(x_test)-x_test.shape[1]-1))
    
    Train_MSE = mean_squared_error(y_train, rfr_ytrain)
    MSE = mean_squared_error(y_test,rfr_y_predict)                                 # Test dataset mean square error
    
    Train_MAE = mean_absolute_error(y_train, rfr_ytrain)
    MAE = mean_absolute_error(y_test,rfr_y_predict)                                # Test dataset mean absolute error
    
    Train_EVS = explained_variance_score(y_train, rfr_ytrain)
    EVS = explained_variance_score(y_test,rfr_y_predict)                           # Explain variance score in the test dataset, the best case score is 1, the lower the score, the worse the evaluation result.

    Train_MAPE = mape(y_train, rfr_ytrain)
    MAPE = mape(y_test,rfr_y_predict)
    
    print("Train dataset accuracy:",ACC)
    print("Test dataset accuracy:", EV)
    print('\n')
    print("Train dataset R-squared:", Train_R2)
    print("Test dataset R-squared:", R2)
    print('\n')
    print("Train dataset mean square error MSE:", Train_MSE)
    print("Test dataset mean square error MSE:", MSE)
    print('\n')
    print("Root mean square error of train data set RMSE:", Train_MSE**0.5)
    print("Root mean square error of test data set RMSE:", MSE**0.5)
    print('\n')
    print("Train dataset mean absolute error MAE:", Train_MAE)
    print("Test dataset mean absolute error MAE:", MAE)
    print('\n')
    print("Train explain variance score EVS:", Train_EVS)
    print("Test explain variance score EVS:", EVS)
    print('\n')
    print("Train dataset mean absolute percentage error MAPE:", Train_MAPE)
    print("Test dataset mean absolute percentage error MAPE:", MAPE)
    print('\n')
    print( "Variable importance:",importances)
    print('\n')
    random_seed.append(i)
    E_0_Train.append(ACC)
    E_0_Test.append(EV)    
    E_1_Train.append(Train_R2)
    E_1_Test.append(R2)
    E_2_Train.append(Train_MSE)
    E_2_Test.append(MSE)
    E_3_Train.append(Train_MSE**0.5)
    E_3_Test.append(MSE**0.5)
    E_4_Train.append(Train_MAE)
    E_4_Test.append(MAE)
    E_5_Train.append(Train_EVS)
    E_5_Test.append(EVS)
    E_6_Train.append(Train_MAPE)
    E_6_Test.append(MAPE)
    E_7_Train.append(Train_A_R2)
    E_7_Test.append(A_R2)
    time_list.append(run_time)
    for j in range(0,11):
        impor[i-1,j] = importances[j]

random_seed.append('Average')
E_0_Train.append(np.mean(E_0_Train))
E_0_Test.append(np.mean(E_0_Test))    
E_1_Train.append(np.mean(E_1_Train))
E_1_Test.append(np.mean(E_1_Test))
E_2_Train.append(np.mean(E_2_Train))
E_2_Test.append(np.mean(E_2_Test))
E_3_Train.append(np.mean(E_3_Train))
E_3_Test.append(np.mean(E_3_Test))
E_4_Train.append(np.mean(E_4_Train))
E_4_Test.append(np.mean(E_4_Test))
E_5_Train.append(np.mean(E_5_Train))
E_5_Test.append(np.mean(E_5_Test))
E_6_Train.append(np.mean(E_6_Train))
E_6_Test.append(np.mean(E_6_Test))
E_7_Train.append(np.mean(E_7_Train))
E_7_Test.append(np.mean(E_7_Test))
time_list.append(np.mean(time_list))

# Save result
XG_Result = pd.DataFrame()
XG_Result['Random_seed'] = random_seed
XG_Result['Train ACC'] = E_0_Train
XG_Result['Test ACC'] = E_0_Test
XG_Result['Train R2'] = E_1_Train
XG_Result['Test R2'] = E_1_Test
XG_Result['Train MSE'] = E_2_Train
XG_Result['Test MSE'] = E_2_Test
XG_Result['Train RMSE'] = E_3_Train
XG_Result['Test RMSE'] = E_3_Test
XG_Result['Train MAE'] = E_4_Train
XG_Result['Test MAE'] = E_4_Test
XG_Result['Train EVS'] = E_5_Train
XG_Result['Test EVS'] = E_5_Test
XG_Result['Train MAPE'] = E_6_Train
XG_Result['Test MAPE'] = E_6_Test
XG_Result['Train_A_R2'] = E_7_Train
XG_Result['A_R2'] = E_7_Test
XG_Result['run time'] = time_list
XG_importance = pd.DataFrame(impor)
XG_importance.columns = Train_data.columns.values[0:11]

XG_Result.to_excel(path_save+filename+'_XG_Result.xlsx', index=False) 
XG_importance.to_excel(path_save+filename+'_XG_Impor.xlsx', index=False)
print('Results saved')



