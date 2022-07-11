# Acknowledgement.

This is the software infrastructure of ***the IAMU (International Association of Maritime Universities) research project titled “Data fusion and machine learning for ship fuel efficiency analysis: a small but essential step towards green shipping through data analytics” (Research Project No. 20210205_AMC). The materials and data in this project have been obtained through the support of IAMU and The Nippon Foundation in Japan.*** This project has the following investigators: Yuquan (Bill) Du (Coordinator, Lead Applicant), Peggy Shu-Ling Chen, Nataliya Nikolova, Prashant Bhaskar, and Jiangang Fei from University of Tasmania (UTAS); Alessandro Schönborn from World Maritime University (WMU) as WMU-side Chief Investigator; and Zhuo Sun from Dalian Maritime University (DMU) as DMU-side Chief Investigator. Dr Xiaohe Li laid a good Python code fundation during his University Associate role at UTAS and conducted some preliminary experiments. Ms Yanyu Chen is the main Research Assistant of this project who has major contributions to Python code and conducting experiments under the supervision of Dr Yuquan (Bill) Du. Mr Jean-Louis Bertholier developed the Python code of collecting meteorological data for ships during his Assistant Engineer internship at World Maritime University. Warm help are received from ECMWF (Centre for Medium-range Weather Forecasts) and Copernicus Marine Service (CMEMS) when we wanted to automate the download process of meteorological data. This study has been conducted using E.U. Copernicus Marine Service Information; https://doi.org/10.48670/moi-00050. Hersbach et al. (2018) was downloaded from the Copernicus Climate Change Service (C3S) Climate Data Store. The results of this study and trained machine learning models published contain modified Copernicus Climate Change Service information 2020. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

The following three papers explain the research work behind the Python code to be described. **Cite the following papers if you use the code and trained models in this project**. For an instruction on how to obtain the trained machine learning models in the following three papers and use them to estimate/forecast a mega containership's daily bunker fuel consumption, see "***Instructions on How to Use Trained Machine Learning Models.ipynb***" for details - this ".ipynb" file should be downloaded and run in Jupyter Notebook.

*Xiaohe Li, Yuquan Du, Yanyu Chen, Son Nguyen, Wei Zhang, Alessandro Schönborn, Zhuo Sun, 2022. "Data fusion and machine learning for ship fuel efficiency modeling: Part I – voyage report data and meteorological data". Communications in Transportation Research, 2, 100074.*

*Yuquan Du, Yanyu Chen, Xiaohe Li, Alessandro Schönborn, Zhuo Sun, 2022a. "Data fusion and machine learning for ship fuel efficiency modeling: Part II – voyage report data, AIS data and meteorological data". Communications in Transportation Research, 2, 100073.*

*Yuquan Du, Xiaohe Li, Yanyu Chen, Alessandro Schönborn, Zhuo Sun, 2022b. "Data fusion and machine learning for ship fuel efficiency modeling: Part III – sensor data and meteorological data". Communications in Transportation Research, 2, 100072.*


**References**

Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2018): ERA5 hourly data on single levels from 1979 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). (Accessed on 10-Sep-2021), 10.24381/cds.adbb2d47.

============================================================================================================================================

Our Python code in this project is explained as follows. There are four stages in conducting ship fuel efficiency experiments, including data dowload, data processing, data fusion, and model training and testing.

1. ***Data Download*** (in folder "data_download") 
    Two different meteorological datasets need to be dowloaded.

    1.1. "ear5_weather_information_download.py" downloads the data of wind, waves, and sea water temperature from ECMWF (Centre for Medium-range Weather Forecasts) (Hersbach et al., 2018).
   
    1.2. "copernicus_marine_ocean_wave_data_download.py" downloads the data of sea currents from Copernicus Marine Service (CMEMS, also a.k.a. “Copernicus”). This file was provided by XXX from XXXX. Yanyu Chen from ... and Jean-Louis Bertholier from World Maritime Unviersity revised the code according to data requirements of the above papers. The author of this Python file is "Copernicus Marine User Support Team". We obtained the permission from "Copernicus Marine User Support Team" to include this file to our GitHub project, with proper citation and acknowledgement.  

2. ***Data Processing*** (in folder "data_processing")
    Four different datasets need to be processed, including meterological data, voyage report data, AIS data and sensor data.
   
    2.1 **Meteorological Data**. Run the following Python files in order in the folder "data_processing\Meteorological data".
   
        · "ocean_current_nc.py" retrieves information of sea currents from <b>downloaded</b> Copernicus data stored in files (in the  data structure of Rubric), according to the input <timestamp, latitude, longitude>.
   
        · "ocean_wave_hour.py" retrieves information of wind, waves, and sea water temperature from downloaded ECMWF data stored in files (in the  data structure of Rubric), according to the input <timestamp, latitude, longitude>.
   
        · "ocean_import_nan.py" converts "nan" values of data (outputs of "ocean_current_nc.py" and "ocean_wave_hour.py") to "NaN" for the convience of further data cleaning. Run this file twice: once for the data output of "ocean_current_nc.py"; once for the data output of "ocean_wave_hour.py". 
   
        · "combine_ow_oc.py" combines Copernicus data (after running of "ocean_import_nan.py") and ECMWF data (after running of "ocean_import_nan.py"), and cleans the errors and noises.
   
    2.2 **Voyage Report Data**. Run the following Python files in order in the folder "data_processing\Voyage report".
   
        · "report_process_correct.py" and "report_process_checklist.py" are used to clean voyage report data. Note than different shipping companies use different data structures for voyage reports, and these code here might not be able to be directly used to clean the errors or noises of the voyage report you obtained from a shipping company.
   
        · "report_process_divid.py" claculates the hourly geographical positions of the ship: <timestamp, latitude, longitude>, according to Great Circle Route (rhumb line).
   
        · "report_cube.py" generates a data cube/container/rubric (file) that contains the hourly <timestamp, latitude, longitude> information obtained from "report_process_divid.py", and the columns names for machine learning features/variables (speed, displacement, wind direction, wind waves, swell,....), though the data for these variables/features are not populated in yet.
   
        · "report_cube_modification.py" rounds the longitute values of e.g. 180.05 degree to 179.9 degree, or rounds the longitute values of e.g. -180.05 degree to -179.9 degree, because downloaded meteorological data uses the longitude range [-179.975 degree, 179.975 degree].
   
    2.3 **AIS Data**. Run the following Python files in order in the folder "data_processing\AIS data".
   
        · "ais_cube_checklist.py" samples hourly data entries from raw AIS data because only hourly information of <timestamp, latitude, longitude, heading> is needed. In a rare situation where a time period (say 4 continous hours) doesn't have any AIS data entries, hourly timestamps are inserted. 
   
        · "ais_report_combine.py" corrects the "heading" information of the sampled AIS data entries: when "heading" information is absent from AIS data, "true course" in AIS data will be used; if "true course" is also absent from AIS data, "true course" informaiton from voyage report is used.
   
        · "ais_cube_divid_correct.py" generates hourly geographical postions of the ship for the rare situation in "ais_cube_checklist.py" where a time period (say 4 continous hours) doesn't have any AIS data entries.
   
        · "ais_cube_match.py" generates a data cube/container/rubric (file) that contains the hourly <timestamp, latitude, longitude> information obtained from "ais_cube_divid_correct.py", and the columns names for machine learning features/variables (speed, displacement, wind direction, wind waves, swell,....), though the data for these variables/features are not populated in yet.
   
    2.4 **Sensor Data**. Run the following Python files in order in the folder "data_processing\Sensor data".
   
        · "sensor_cube_selection.py" cleans sensor data.

3. ***Data Fusion*** (in folder "data_fusion")
    Data fusion apporaches used in three papers.
   
    3.1 **Data fusion solution 1 (Li et al., 2022)** - fusion of voyage report data and meteorological data. Run the following Python files in order in the folder "data_fusion\Voyage data fusion".
   
        · "voyage_weather_combination.py" fuses voyage report data and meteorological data, and make necessary calculations about wind, waves and current directions.
   
        · "voyage_weather_combinatioant_transfer.py" converts the precise values of wind speed, wind directions, wave directions, and sea currents directions to fuzzy values. See Li et al. (2022).  
   
    3.2 **Data fusion solution 2 (Du et al., 2022a)** - fusion of voyage report data, AIS data, and meteorological data. Run the following Python files in order in the folder "data_fusion\AIS data fusion".
   
        · "ais_weather_combination.py" fuses voyage report data, AIS data, and meteorological data, and make necessary calculations about wind, waves and current directions.
   
        · "ais_weather_combination_transfer.py" converts the precise values of wind speed, wind directions, wave directions, and sea currents directions to fuzzy values. See Li et al. (2022).  
   
    3.3 **Data fusion solution 3 (Du et al., 2022b)** - fusion of sensor data and meteorological data. Run the following Python files in order in the folder "data_fusion\Sensor data fusion".

        · "sensor_weather_combination.py" fuses sensor data and meteorological data, and make necessary calculations about wind, waves and current directions.
   

4. **Hyperparameter optimization/selection** (in folder "parameter_selection")

    · "ET_H.py" in the folder "parameter_selection\ET_Set3Precise": Given the best dataset *Set3Precise* found in Li et al. (2022) (Readers can use "data_sample\Set3Precise.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), this python file is used to optimize the hyperparameters of extremely randomized trees (ET) model.
   
    · "GB_H.py" in the folder "parameter_selection\GB_AIS5Precise": Given the best dataset *AIS5Precise* found in Du et al. (2022a) (Readers can use "data_sample\AIS5Precise.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), this python file is used to optimize the hyperparameters of gradient tree boosting (GB) model.
   
    · "XG_H.py" in the folder "parameter_selection\XG_Sensor2": Given the best dataset *Sensor2* found in Du et al. (2022b) (Readers can use "data_sample\Sensor2.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), this python file is used to optimize the hyperparameters of XGBoost (XG) model. 

5. **Model Training and Test** (in folder "model_training")
   
    After hyperparameter optimization/selection, documents/files that contain the optimized hyperparameter values will be generated. According to these parameter documents/files, run the following code to train and test machine learning models. For instance, 

    · "ET_Cycle_H.py" in the folder "model_training\ET_Set3Precise": train and test extremely randomized trees (ET) model given the best dataset *Set3Precise* (Readers can use "data_sample\Set3Precise.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), as discussed in Li et al. (2022).

    · "GB_Cycle_H.py" in the folder "model_training\GB_AIS5Precise": train and test gradient tree boosting (GB) model given the best dataset *AIS5Precise* (Readers can use "data_sample\AIS5Precise.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), as discussed in Du et al. (2022a).

    · "XG_Cycle_H.py" in the folder "model_training\XG_Sensor2": train and test XGBoost (XG) model given the best dataset *Sensor2* (Readers can use "data_sample\Sensor2.xlsx" for experiments, but keep in mind that this is a fake dataset we randomely generated), as discussed in Du et al. (2022b).
