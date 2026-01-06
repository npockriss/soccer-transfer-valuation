# Soccer Transfer Value Predictor

### Objective
Predicting the market value of soccer playing using Machine Learning. The goal was to build a model that outperforms a single baseline and handles the high variance of the transfer market (from $100k rookies to $180M stars).

### Tech Stack
* **Python:** Pandas, Scikit-Learn, XGBoost, Matplotlib/Seaborn
* **Data Source:** Kaggle dataset (Transfermarkt scrape)

### Key Results
* **Baseline Error:** 6.3M Euros (Initial Random Forest)
* **Final Error:** 3.8M Euros (XGBoost + Log-Transformation)
* **Improvement:** Reduced error by around 40% through Feature Engineering

### Methodology
1.  **Feature Engineering:** Created a League Strength coefficient based on 2025 UEFA rankings to weigh goals/assists differently (e.g., a goal in the Premier League is weighted higher than in the Ukrainian Premier League).
2.  **Handling Outliers:** The raw price distribution was highly right-skewed by superstars. I applied a **Log-Transformation (`np.loglp`)** to the target variable, which allowed the model to accurately predict high-value players like Bellingham and Mbappe.
3.  **Model Selection:** Compared Random Forest vs. XGBoost. XGBoost provided best handling of edge cases.

### Visuals
![Model Prediction Chart](actual_vs_predicted_value_scatter.png)