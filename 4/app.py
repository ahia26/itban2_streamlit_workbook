import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Title
st.title("Public API Data Dashboard")

# Select API Source
api_choice = st.sidebar.selectbox("Choose API", ["Weather", "COVID-19 Stats"])

# Fetch Data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve data")
        return None

if api_choice == "Weather":
    city = st.sidebar.text_input("Enter City", "New York")
    api_url = f"https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={city}"
    data = fetch_data(api_url)

    if data:
        st.subheader(f"Weather in {city}")
        st.write(f"Temperature: {data['current']['temp_c']}°C")
        st.write(f"Condition: {data['current']['condition']['text']}")

        # Visualization
        df = pd.DataFrame({
            "Category": ["Temperature", "Humidity", "Wind Speed"],
            "Value": [data['current']['temp_c'], data['current']['humidity'], data['current']['wind_kph']]
        })
        fig1 = px.bar(df, x="Category", y="Value", title="Weather Metrics")
        st.plotly_chart(fig1)

elif api_choice == "COVID-19 Stats":
    country = st.sidebar.text_input("Enter Country", "USA")
    api_url = f"https://disease.sh/v3/covid-19/countries/{country}"
    data = fetch_data(api_url)

    if data:
        st.subheader(f"COVID-19 Stats in {country}")
        st.write(f"Total Cases: {data['cases']}")
        st.write(f"Recovered: {data['recovered']}")
        st.write(f"Deaths: {data['deaths']}")

        # Visualization
        df = pd.DataFrame({
            "Metric": ["Cases", "Recovered", "Deaths", "Active"],
            "Value": [data['cases'], data['recovered'], data['deaths'], data['active']]
        })
        fig2 = px.pie(df, names="Metric", values="Value", title="COVID-19 Distribution")
        st.plotly_chart(fig2)

st.subheader("Additional Charts")
df_sample = pd.DataFrame({
    "X": range(1, 11),
    "Y": [x**2 for x in range(1, 11)]
})
fig3 = px.line(df_sample, x="X", y="Y", title="Line Chart Example")
fig4 = px.scatter(df_sample, x="X", y="Y", title="Scatter Chart Example")
fig5 = px.area(df_sample, x="X", y="Y", title="Area Chart Example")

st.plotly_chart(fig3)
st.plotly_chart(fig4)
st.plotly_chart(fig5)