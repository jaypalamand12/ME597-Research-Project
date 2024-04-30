# ME597-Research-Project
Battery Swapping Software

Folder/File Descriptions

Data Folder:
- Transformed data streamed to dashboard

DeepLearningModels Folder
- Saved LSTM and ANN models for capacity prediction

Frontend Folder
- assets: Folder with alert images
- assets.py: Dataclass holding paths to alert images
- main.py: root of streamlit application, frontend code for sidebar, battery status boxes, and swap button functionality
- dataloader.py: data pipeline for loading, transforming, and incrementing through datasets in Data folder based on charge/discharge and cycle number.  Also constains frontend code displaying alerts
- load.py:  This is the code taking the .mat files for B0005-18 downloaded from the NASA website and transforming them into csv files saved in Data folder
 http://ti.arc.nasa.gov/project/prognostic-data-repository
- soc_calc.py: Coulomb counting algorithm, adds SOC_CC column to csv files in Data folder
- soh_prediction.py: loads LSTM model and adds SOH column to csv files in Data folder with SOH predictions for 'B0005', 'B0006', 'B0007', 'B0018'
- swap.py: Battery swapping logic for dashboard

SklearnModels Folder:
- Saved Machine learning models for capacity prediction

TransformedData Folder:
- Csv files in Data folder transformed into health indicators.

HIExtractor.py:
- Health Indicator calculations

feature_extraction.ipynb:
- Jupyter notebook for feature extraction, health indicator calculation, model training, testing and data visualization

train_deeplearning.py:
- training for LSTM and ANN

train_sklearn.py
- training for sklearn machin learning models
  
