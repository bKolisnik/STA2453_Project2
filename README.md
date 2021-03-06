# Project #2 Data Visualization
This repo contains our STA 2453 Project 2 dashboard code.

Framework: Plotly Dash

Data sets: https://github.com/ccodwg/Covid19Canada, https://data.ontario.ca/dataset/covid-19-cases-in-hospital-and-icu-by-ontario-health-region, https://data.ontario.ca/dataset/status-of-covid-19-cases-in-ontario/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11, https://data.ontario.ca/dataset/status-of-covid-19-cases-in-ontario-by-public-health-unit-phu/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc, https://data.ontario.ca/dataset/covid-19-vaccine-data-in-ontario/resource/8a89caa9-511c-4568-af89-7f2174b4378c

Auxillary Data sets: https://geohub.lio.gov.on.ca/datasets/ministry-of-health-public-health-unit-boundary?geometry=-89.272%2C42.218%2C-68.343%2C45.001

Audience: General Ontario Population

## Analytical Pipeline: Data Access, Ingestion, and Presentation
With the exception of one geojson file which has been inlcuded in the repo, the most recent versions of all required data sets are downloaded at server startup. The data sets are sourced from the provincial government of Ontario and the federal government of Canada respectively and downloaded as CSVs. Following the downloads, the data is cleaned and preprocessed. Much of the preprocessing includes filtering for relevant dates and joinging different data sets. Statistics and metrics are calulcated using the cleaned datasets. The data is stored in globally scoped Pandas dataframes which are accssible to the Dash application. The visualizations of the dashboard use these dataframes for their source data. 

## Installation Instructions
After pulling the repo to run the dashboard please complete the following steps.

1. Install the required packages using 

```
pip install -r requirements.txt
```

2. Run the dashboard. All relevant files will be downloaded.
```
python app.py
```
3. Go to http://127.0.0.1:8050/
