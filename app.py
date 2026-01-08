import streamlit as st
import pandas as pd
import sqlite3
import joblib

# LOAD THE MODEL
try:
    model = joblib.load('player_value_model.pkl')
    model_loaded = True
except:
    st.error("Model file not found. Please run 'train_model.py' to create the model.")
    model_loaded = False

st.title("Football Player Market Value Predictor")

# USER INPUTS
st.sidebar.header("Select League")
league_name = st.sidebar.selectbox("League", options=["Premier League (England)", "Serie A (Italy)", "La Liga (Spain)", "Bundesliga (Germany)",
                                                      "Ligue 1 (France)", "Eredivisie (Netherlands)", "Liga Nos (Portugal)", "Jupiler Pro (Belgium)",
                                                      "Super Lig (Turkey)", "Super League (Greece)", "Superliga (Denmark)", "SPFL (Scotland)",
                                                      "Ukrainian Premier League (Ukraine)", "Russian Premier League (Russia)", "MLS/Other"])

# DEFINE LEAGUE MULTIPLIERS
multipliers = {
    'Premier League (England)': 1.00,   # Premier League (England) - 103.6 pts
    'Serie A (Italy)': 0.89,   # Serie A (Italy) - 92.1 pts
    'La Liga (Spain)': 0.83,   # La Liga(Spain) - 85.9 pts
    'Bundesliga (Germany)': 0.80,   # Bundesliga (Germany) - 82.9 pts
    'Ligue 1 (France)': 0.73,   # Ligue 1 (France) - 75.5 pts
    'Eredivisie (Netherlands)': 0.63,   # Eredivisie (Netherlands) - 65.7 pts
    'Liga Nos (Portugal)': 0.61,   # Liga Nos (Portugal) - 63.2 pts
    'Jupiler Pro (Belgium)': 0.56,   # Jupiler Pro (Belgium) - 57.7 pts
    'Super Lig (Turkey)': 0.46,   # Super Lig (Turkey) - 48.1 pts
    'Super League (Greece)': 0.42,   # Super League (Greece) - 43.6 pts
    'Superliga (Denmark)': 0.38,   # Superliga (Denmark) - 38.9 pts
    'SPFL (Scotland)': 0.29,   # SPFL (Scotland) - 30.5 pts
    # Ukrainian Premier League (Ukraine) - 24.3 pts
    'Ukrainian Premier League (Ukraine)': 0.23,
    # Russian Premier League (Russia) - 18.3 pts
    'Russian Premier League (Russia)': 0.18,
    'MLS/Other': 0.15
}

league_mult = multipliers[league_name]

st.sidebar.write(f"**League Multiplier:** {league_mult}")
st.sidebar.markdown("---")

st.sidebar.header("Player Stats (Raw)")
# User inputs raw stats
age = st.sidebar.slider("Age", 16, 40, 24)
goals = st.sidebar.slider("Goals Scored", 0, 60, 10)
assists = st.sidebar.slider("Assists Made", 0, 40, 5)
minutes_played = st.sidebar.slider("Minutes Played", 0, 4000, 2000)

if st.sidebar.button("Predict Market Value"):
    if model_loaded:
        league_mult = multipliers[league_name]
        goals_weighted = goals * league_mult
        assists_weighted = assists * league_mult

        input_data = pd.DataFrame({
            'age': [age],
            'goals_weighted': [goals_weighted],
            'assists_weighted': [assists_weighted],
            'minutes_played': [minutes_played]
        })

        prediction = model.predict(input_data)[0]
        st.header(f"Valuation: €{prediction:,.0f}")

        if prediction > 50_000_000:
            st.success("🌟 This player is a superstar!")
        elif prediction > 10_000_000:
            st.info("👍 This player is a solid professional.")
        elif prediction < 1_000_000:
            st.warning(
                "⚠️ This player might be a youth or lower-league talent.")
    else:
        st.error("Cannot make prediction as model is not loaded.")

# CALCULATION AND PREDICTION
if model_loaded:
    # Calculate weighted stats
    goals_weighted = goals * league_mult
    assists_weighted = assists * league_mult

    # Prepare input for model
    input_data = pd.DataFrame({
        'age': [age],
        'goals_weighted': [goals_weighted],
        'assists_weighted': [assists_weighted],
        'minutes_played': [minutes_played]
    })

    # PREDICT
    try:
        # Make prediction
        prediction = model.predict(input_data)[0]

        # Debugging: show the user what the model actually saw
        st.write(
            f"Raw Goals: {goals} * Multiplier: {league_mult} = **{goals_weighted} Weighted Goals**")
        st.write(
            f"Raw Assists: {assists} * Multiplier: {league_mult} = **{assists_weighted} Weighted Assists**")
    except Exception as e:
        st.error(f"Error during prediction: {e}")
        st.write(
            "Check that your columns in 'train_model.py match 'input_data' exactly.")

# DATABASE SEARCH
st.markdown("---")
st.subheader("Compare with Real Players from Database")
conn = sqlite3.connect('final_data.db')
search = st.text_input("Search Player Name (partial names OK):", "")
if search:
    df = pd.read_sql(
        f"SELECT * FROM players where NAME LIKE '%{search}%' LIMIT 5", conn)
    st.dataframe(df)
conn.close()


# MONEYBALL SEARCH
st.markdown("---")
st.header("Scout Database (Real vs AI)")

conn = sqlite3.connect('final_data.db')
search = st.text_input("Search for a player:", "")

if search:
    # Get players
    sql = f"SELECT * FROM players WHERE NAME LIKE '%{search}%' LIMIT 100"
    df = pd.read_sql(sql, conn)

    if not df.empty and model_loaded:
        # Prepare data
        features = df[['age', 'goals_weighted',
                       'assists_weighted', 'minutes_played']].fillna(0)
        # Ask AI to predict value for ALL players at once
        df['AI_Predicted_Value'] = model.predict(features)

        # Calculate the difference (Real - AI)
        df['Value_Difference'] = df['market_value_in_eur'] - \
            df['AI_Predicted_Value']

        # Format
        display_df = df[['name', 'age', 'current_club_domestic_competition_id', 'market_value_in_eur',
                         'AI_Predicted_Value', 'Value_Difference']].copy()
        pd.options.display.float_format = '€{:,.0f}'.format
        st.dataframe(display_df)

        st.subheader("Value Analysis Chart")
        chart_data = df.copy()

        # Create Scatter Plot
        st.scatter_chart(chart_data, x='age', y='market_value_in_eur',
                         color='Value_Difference', size='AI_Predicted_Value')
        st.caption("Blue/Positive = Overpriced | Red/Negative = Underpriced")

        # Highlight the steal
        best_deal = df.loc[df['Value_Difference'].idxmin()]
        if best_deal['Value_Difference'] < -5000000:
            st.success(
                f"**MONEYBALL ALERT:** {best_deal['name']} is undervalued by €{abs(best_deal['Value_Difference']):,.0f}!")

    elif df.empty:
        st.warning("No players found with that name.")

conn.close()
