# Collision-Severity-Analysis
Analysing key trends in collision severity using the Road Safety Open Dataset, creating a reproducible pipeline that spans data cleaning, analysis, and visualisation, which includes a Streamlit dashboard.

An important topic I have emphasised throughout the notebooks is the **responsible** use of AI to aid one's work, and how I myself have used it. My view is that students must internalise key technical concepts rather than simply feeding a prompt into AI to create a variety of fancy models without actually understanding what has been created, why it has been created, and how the data has been processed. I maintain that the most important aspect of this project was not the analysis or the visualisations, but rather the **handling of real-life, messy data**. 

## Notebooks: 

There are three Jupyter notebooks included in this folder: 

- Notebook 00 sets up the data, simply merging it and getting a better idea of what the data looks like
- Notebook 01 deals with essential data preprocessing, including cleaning, encoding, and splitting the data so that it is ready for analysis
- Notebook 02 includes analysis of the most important predictors of collision severity, using different models such a simple OLS regression, a gradient-boosted tree, and a feedforward neural network
- Notebook 03 focuses on essential EDA, producing visualisations that will be saved in the "Visualisations" folder in the "Dashboard" folder (these visualisations are later used by the dashboard)

**For all notebooks, you will have to edit the base path (i.e. the local path that from your computer all the way up to the WISE folder). Once this is done, the notebooks should run smoothly.**

## Dashboard: 

To run the dashboard: 
1. Open a new terminal in the same directory as the WISE folder 
2. Install the streamlit package 
3. Run the below code: 
    streamlit run dashboard_script_FINAL.py 

This should be all that is necessary, provided that the Visualisation folder is also present in the directory.     


## Acknowledgements: 

I thank Juliana Cunha Carneiro Pinto for providing me the opportunity to take on this project, further develop my skills in data analysis, and hopefully provide some insight into the Data Science module for future students. 
