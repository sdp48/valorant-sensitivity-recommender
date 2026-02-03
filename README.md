# Valorant Sensitivity Recommender

This project is a small web app that helps Valorant players find a reasonable in-game sensitivity based on professional player settings and basic aiming heuristics.

I built it mainly to better understand how sensitivity, eDPI, and cm/360 relate to each other, and to practice working with real-world data and APIs. The app is built with Python and Streamlit and pulls data from Liquipedia.

---

## What the app does

- Loads professional player sensitivity data from Liquipedia  
- Cleans and filters the dataset to remove unrealistic values  
- Uses aim style, goal, and mousepad size to choose a target cm/360 range  
- Converts that range into an in-game sensitivity for the user’s DPI  
- Compares the user’s sensitivity to pro players using eDPI  
- Shows where the user sits relative to pros using a simple distribution chart  

---

## How the recommendation works (high level)

- **eDPI** is calculated as:  
  `eDPI = DPI × in-game sensitivity`

- **cm/360** represents how far the mouse must move (in cm) to do a full 360° turn  

- Different aim styles (wrist vs arm) and goals (precision vs speed) tend to prefer different cm/360 ranges  

- The app selects a reasonable cm/360 range based on those inputs  

- That range is converted into a sensitivity value for the user’s DPI  

- Pro comparisons are done by finding players with the closest eDPI  

The logic is rule-based and explainable — no machine learning is used.

---

## Data source and filtering

- Source: Liquipedia Valorant pro settings  
- Data is fetched using a Python script and saved locally as a CSV  
- Each row includes:
  - player name  
  - sensitivity  
  - eDPI (as provided by Liquipedia)  

Basic sanity filters are applied, for example:
- sensitivity must be between 0.05 and 2.0  
- eDPI must be between 120 and 800  

This removes obvious parsing errors and outliers.

---

## Project structure

valorant-recommender/
├── app.py
├── README.md
├── data/
│ └── pro_sens.csv
├── recommender/
│ └── sens.py
├── scripts/
│ └── fetch_pro_sens_liquipedia.py
└── requirements.txt

---

## Running the app locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# fetch / refresh pro dataset
python3 scripts/fetch_pro_sens_liquipedia.py

# run the app
streamlit run app.py
```

---

## Limitations

- Sensitivity preference is subjective and the recommendation is meant to be a starting point
- Pro player data may be outdated or inconsistent depending on Liquipedia entries
- The system does not adapt based on user performance or feedback

---

## Why I built this

I wanted to build a project that combined real data, basic statistics, and user-focused design into something practical. This project helped me better understand data validation, distributions, and how to build an explainable recommendation system end-to-end.