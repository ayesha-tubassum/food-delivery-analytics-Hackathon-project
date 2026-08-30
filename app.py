"""Interactive dashboard for the Food Delivery Analytics Challenge."""

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Food Delivery Analytics", page_icon="🍔", layout="wide")
DATA_FILE = Path(__file__).with_name("food_delivery_dataset.csv")


@st.cache_data
def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Load the CSV and reproduce the notebook's cleaning approach."""
    data = pd.read_csv(file_path)
    # The notebook fills these two missing values using median values.
    data["Delivery_person_Age"] = pd.to_numeric(data["Delivery_person_Age"], errors="coerce")
    data["Delivery_person_Ratings"] = pd.to_numeric(data["Delivery_person_Ratings"], errors="coerce")
    data["Delivery_person_Age"] = data["Delivery_person_Age"].fillna(data["Delivery_person_Age"].median())
    data["Delivery_person_Ratings"] = data["Delivery_person_Ratings"].fillna(data["Delivery_person_Ratings"].median())
    # An order time is essential, so the notebook removes rows where it is absent.
    data = data.dropna(subset=["Time_Orderd"]).copy()
    for column in ["Time_taken (min)", "distance_km"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    # Speed labels in the CSV are replaced with the notebook's calculated km/h value.
    data["delivery_speed"] = (data["distance_km"] / data["Time_taken (min)"]) * 60
    return data.dropna(subset=["Time_taken (min)", "distance_km", "delivery_speed"])


def average_by(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return sorted average delivery times for a category or category pair."""
    return (data.groupby(columns, as_index=False)["Time_taken (min)"].mean()
            .sort_values("Time_taken (min)", ascending=False))


def show_competition_answers(data: pd.DataFrame) -> None:
    """Calculate and show the three hackathon questions from the active filter."""
    st.header("🏆 Competition questions — live answers")
    st.caption("These results update instantly whenever you change a sidebar filter.")
    traffic = average_by(data, ["Road_traffic_density"])
    worst_traffic = traffic.iloc[0]
    correlation = data["distance_km"].corr(data["Time_taken (min)"])
    distance_data = data.copy()
    distance_data["Distance band"] = pd.cut(
        distance_data["distance_km"], bins=[0, 5, 10, 15, 20, float("inf")],
        labels=["0–5 km", "5–10 km", "10–15 km", "15–20 km", "20+ km"], include_lowest=True)
    distance_summary = average_by(distance_data, ["Distance band"])
    weather_traffic = average_by(data, ["Weather_conditions", "Road_traffic_density"])
    worst_combo = weather_traffic.iloc[0]
    first, second, third = st.columns(3)
    first.info(f"**1. Traffic impact**\n\n**{worst_traffic['Road_traffic_density']}** traffic has the highest average delivery time: **{worst_traffic['Time_taken (min)']:.1f} min**.")
    second.info(f"**2. Distance impact**\n\nDistance and time have a **{correlation:.2f}** correlation. The distance-band table below shows average time at each distance.")
    third.info(f"**3. Weather + traffic**\n\n**{worst_combo['Weather_conditions']} + {worst_combo['Road_traffic_density']}** is slowest at **{worst_combo['Time_taken (min)']:.1f} min** on average.")
    st.dataframe(distance_summary.rename(columns={"Time_taken (min)": "Average delivery time (min)"}), use_container_width=True, hide_index=True)


def build_ai_prompt(data: pd.DataFrame) -> str:
    """Summarise filtered data for an easy-to-read AI recommendation."""
    traffic = average_by(data, ["Road_traffic_density"]).iloc[0]
    combo = average_by(data, ["Weather_conditions", "Road_traffic_density"]).iloc[0]
    correlation = data["distance_km"].corr(data["Time_taken (min)"])
    return f"""You are a senior food-delivery business analyst. Give exactly 3 short, practical, beginner-friendly bullet-point recommendations. Base them only on these filtered dashboard results:
- Deliveries: {len(data):,}
- Average delivery time: {data['Time_taken (min)'].mean():.2f} minutes
- Average distance: {data['distance_km'].mean():.2f} km
- Average speed: {data['delivery_speed'].mean():.2f} km/h
- Slowest traffic: {traffic['Road_traffic_density']} ({traffic['Time_taken (min)']:.2f} minutes)
- Slowest weather + traffic: {combo['Weather_conditions']} + {combo['Road_traffic_density']} ({combo['Time_taken (min)']:.2f} minutes)
- Distance/time correlation: {correlation:.2f}
Do not invent statistics or mention machine learning."""


st.title("🍔 Food Delivery Analytics Challenge")
st.caption("Interactive operational insights for faster, more reliable food deliveries.")
st.warning("Free hosting note: if the app has been inactive, it may take a moment to wake up.")
data = load_and_clean_data(str(DATA_FILE))

st.sidebar.header("🔎 Filters")
st.sidebar.caption("Select one or more values. Leave a filter empty to include everything.")
filtered = data.copy()
for column in ["City", "Weather_conditions", "Road_traffic_density", "Type_of_vehicle"]:
    selected = st.sidebar.multiselect(column.replace("_", " "), options=sorted(data[column].dropna().unique().tolist()))
    if selected:
        filtered = filtered[filtered[column].isin(selected)]
if filtered.empty:
    st.error("No deliveries match this filter combination. Please select different values.")
    st.stop()

st.header("📌 Key metrics")
metric_values = [
    ("Total deliveries", f"{len(filtered):,}"), ("Avg delivery time", f"{filtered['Time_taken (min)'].mean():.1f} min"),
    ("Min delivery time", f"{filtered['Time_taken (min)'].min():.0f} min"), ("Max delivery time", f"{filtered['Time_taken (min)'].max():.0f} min"),
    ("Avg distance", f"{filtered['distance_km'].mean():.2f} km"), ("Avg speed", f"{filtered['delivery_speed'].mean():.1f} km/h"),
    ("Avg rating", f"{filtered['Delivery_person_Ratings'].mean():.2f} / 5"), ("Avg courier age", f"{filtered['Delivery_person_Age'].mean():.1f} years"),
]
for metric_column, (label, value) in zip(st.columns(8), metric_values):
    metric_column.metric(label, value)

show_competition_answers(filtered)
st.header("📊 Interactive visualizations")
st.caption("Hover, zoom, and use the chart toolbar to explore the filtered data.")
traffic_chart = average_by(filtered, ["Road_traffic_density"])
fig_traffic = px.bar(traffic_chart, x="Road_traffic_density", y="Time_taken (min)", color="Road_traffic_density", text_auto=".1f", title="Average delivery time by traffic density", labels={"Road_traffic_density": "Traffic density", "Time_taken (min)": "Average minutes"})
fig_traffic.update_layout(showlegend=False)
fig_scatter = px.scatter(filtered, x="distance_km", y="Time_taken (min)", color="Road_traffic_density", hover_data=["City", "Weather_conditions", "Type_of_vehicle"], opacity=0.55, title="Distance versus delivery time", labels={"distance_km": "Distance (km)", "Time_taken (min)": "Delivery time (min)"})
city_chart = average_by(filtered, ["City"])
fig_city = px.bar(city_chart, x="City", y="Time_taken (min)", color="City", text_auto=".1f", title="Average delivery time by city", labels={"Time_taken (min)": "Average minutes"})
fig_city.update_layout(showlegend=False)
vehicle_chart = average_by(filtered, ["Type_of_vehicle"])
fig_vehicle = px.bar(vehicle_chart, x="Type_of_vehicle", y="Time_taken (min)", color="Type_of_vehicle", text_auto=".1f", title="Average delivery time by vehicle type", labels={"Type_of_vehicle": "Vehicle type", "Time_taken (min)": "Average minutes"})
fig_vehicle.update_layout(showlegend=False)
left, right = st.columns(2)
left.plotly_chart(fig_traffic, use_container_width=True)
right.plotly_chart(fig_scatter, use_container_width=True)
left, right = st.columns(2)
left.plotly_chart(fig_city, use_container_width=True)
right.plotly_chart(fig_vehicle, use_container_width=True)

st.header("⬇️ Download filtered data")
st.download_button("Download filtered deliveries as CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_food_deliveries.csv", mime="text/csv")
chart_export = pd.concat([traffic_chart.assign(chart="Average time by traffic"), city_chart.assign(chart="Average time by city"), vehicle_chart.assign(chart="Average time by vehicle")], ignore_index=True, sort=False)
st.download_button("Download chart summary data as CSV", data=chart_export.to_csv(index=False).encode("utf-8"), file_name="food_delivery_chart_summaries.csv", mime="text/csv")

st.header("✨ AI Business Insights")
st.caption("Uses Groq only when you click the button. Your API key is read from `GROQ_API_KEY`.")
if st.button("Generate AI recommendation", type="primary"):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY is not set. Add it as an environment variable, then restart the app.")
    else:
        try:
            from groq import Groq
            with st.spinner("Asking Groq for practical recommendations..."):
                response = Groq(api_key=api_key).chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "system", "content": "You provide concise, evidence-based business advice."}, {"role": "user", "content": build_ai_prompt(filtered)}])
            st.markdown(
                f"<div style='background:#eef8ff;color:#1a1a1a;border-left:6px solid #2563eb;"
                f"padding:1rem;border-radius:0.5rem;line-height:1.6'>"
                f"<h4 style='color:#0b3d91;margin-top:0'>AI-generated recommendation</h4>"
                f"<div style='color:#1a1a1a'>{response.choices[0].message.content}</div></div>",
                unsafe_allow_html=True,
            )
        except Exception as error:
            st.error(f"Groq could not generate an insight: {error}")
