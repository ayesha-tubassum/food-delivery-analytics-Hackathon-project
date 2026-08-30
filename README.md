# Food Delivery Analytics Challenge

An end-to-end hackathon project that studies food-delivery performance using Python, Pandas, and an interactive Streamlit dashboard. It turns delivery, traffic, weather, distance, and courier data into practical operational recommendations—without machine learning.

## Objective

Analyse delivery performance, identify the conditions linked to slower deliveries, and help an operations team make clearer decisions about customer ETAs, routing, and capacity planning.

## Dataset

`food_delivery_dataset.csv` contains 38,964 delivery records and 22 columns. It includes courier age and rating, restaurant and delivery coordinates, weather, traffic density, vehicle and order type, city, delivery time, distance, and delivery-speed labels.

The notebook and dashboard use the same cleaning logic: fill missing courier age and rating with their median; drop rows missing `Time_Orderd`; convert calculation fields to numeric values; and calculate speed as `distance_km / Time_taken (min) * 60`. After cleaning, the analysis contains 38,129 delivery records.

## Folder structure

```text
.
├── Food_Delivery_Analytics_Hackathon.ipynb  # Original analysis notebook
├── food_delivery_dataset.csv                # Original source dataset
├── app.py                                   # Interactive Streamlit dashboard
├── requirements.txt                         # Python packages
├── README.md                                # Project documentation
└── screenshots/                             # Add your own screenshots here
```

## Competition questions and answers

The Streamlit dashboard recalculates all answers from the active filters. For the complete cleaned dataset, the answers are:

1. **Traffic impact:** `Jam` traffic has the highest average delivery time: **31.42 minutes**.
2. **Distance impact:** distance has a **0.32 positive correlation** with delivery time. Average time rises from **22.43 minutes** for 0–5 km to about **30.16 minutes** for 20+ km deliveries, so distance matters but is not the only delay factor.
3. **Weather + traffic:** `Fog` with `Jam` traffic is the slowest combination, averaging **36.88 minutes**.

## Business insights

- Treat traffic as a major ETA signal: Jam traffic is almost 10 minutes slower on average than Low traffic (31.42 vs. 21.50 minutes).
- Use distance-aware dispatch and ETAs, especially beyond 10 km, while also addressing other causes of delay because the distance relationship is moderate rather than decisive.
- Add contingency plans for fog plus traffic jams: communicate longer ETAs early, prioritise route updates, and consider delivery incentives during these difficult conditions.

## Tools and technologies

- Python and Pandas for loading, cleaning, grouping, and statistics
- Jupyter Notebook with Matplotlib/Seaborn for the original exploratory analysis
- Streamlit for the interactive dashboard and filters
- Plotly for interactive charts
- Groq API (`openai/gpt-oss-20b`) for optional AI-generated business recommendations

## Run the notebook

1. Install the project packages: `pip install -r requirements.txt`
2. Start Jupyter: `jupyter notebook`
3. Open `Food_Delivery_Analytics_Hackathon.ipynb` and run its cells in order.

The notebook expects `food_delivery_dataset.csv` to remain in the project folder.

## Run the Streamlit app locally

1. Install dependencies: `pip install -r requirements.txt`
2. From this project folder, run: `streamlit run app.py`
3. Open the local URL Streamlit displays in your browser.

The app includes cached loading, sidebar filters for City, Weather conditions, Traffic density, and Vehicle type; live metrics and competition answers; four Plotly charts; and CSV downloads for the filtered delivery rows and chart summaries.

## AI integration (Groq API)

AI recommendations are optional and generated only after clicking **Generate AI recommendation**. The app never stores or hardcodes the API key. Set the `GROQ_API_KEY` environment variable before starting Streamlit.

PowerShell example:

```powershell
$env:GROQ_API_KEY = "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"
streamlit run app.py
```

The dashboard sends only the current filtered summary statistics to Groq using `openai/gpt-oss-20b` and displays the response as a business recommendation.

## Screenshots

See the `/screenshots` folder. Add your own images there, such as notebook-output and running-dashboard screenshots.
