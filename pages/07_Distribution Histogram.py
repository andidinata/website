import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.stats import norm

# Streamlit layout with two columns
col1, col2 = st.columns([1, 2])  # Left column narrower, right column wider

# Input widgets in the left column
with col1:
    target_value = st.number_input("Target Value", 
                                   min_value=0.1, 
                                   value=1.7, 
                                   step=0.1)
    number_of_data = st.number_input("Number of Data Points", 
                                    min_value=1, 
                                    value=30, 
                                    step=1)
    
    # Widget for standard deviation
    standard_deviation = st.number_input("Standard Deviation", 
                                        min_value=0.1, 
                                        value=0.5, 
                                        step=0.1)
    
    # Deviation type selection
    deviation_type = st.selectbox("Deviation Type", 
                                 ["Percentage", "68-95-99.7 Rule"])
    
    if deviation_type == "Percentage":
        percent_deviation = st.number_input("Percent Deviation", 
                                          min_value=1.0, 
                                          value=50.0, 
                                          step=1.0)
        # Calculate min and max bounds based on percent deviation
        min_value = target_value * (1 - percent_deviation / 100)
        max_value = target_value * (1 + percent_deviation / 100)
        deviation_label = f"±{percent_deviation}% deviation"
    else:
        sd_choice = st.selectbox("Standard Deviations", 
                                ["1 SD (68%)", "2 SD (95%)", "3 SD (99.7%)"])
        sd_multipliers = {"1 SD (68%)": 1, "2 SD (95%)": 2, "3 SD (99.7%)": 3}
        sd = sd_multipliers[sd_choice]
        # Use the user-provided standard deviation for bounds
        min_value = target_value - sd * standard_deviation
        max_value = target_value + sd * standard_deviation
        deviation_label = f"{sd} SD ({['68', '95', '99.7'][sd-1]}%)"

    bins = st.number_input("Number of Bins", 
                          min_value=1, 
                          value=10, 
                          step=1)

# Generate random daily consumption data
daily_consumption = np.random.uniform(min_value, 
                                     max_value, 
                                     number_of_data)

# Determine the widest possible scale
max_percent_range = target_value * (1 + 50 / 100)  # Using max percent_deviation possible
min_percent_range = target_value * (1 - 50 / 100)
max_sd_range = target_value + 3 * standard_deviation  # 3 SD is the widest in 68-95-99.7
min_sd_range = target_value - 3 * standard_deviation
fixed_min = min(min_percent_range, min_sd_range)
fixed_max = max(max_percent_range, max_sd_range)

# Create the histogram in the right column
with col2:
    fig, ax = plt.subplots()
    # Plot histogram with density=True for normalized height
    n, bins_edges, patches = ax.hist(daily_consumption, 
                                    bins=bins, 
                                    edgecolor='black', 
                                    density=True)

    # Fit and plot normal distribution curve with fixed scale
    mu, sigma = norm.fit(daily_consumption)
    x = np.linspace(fixed_min, fixed_max, 100)  # Use widest scale
    y = norm.pdf(x, mu, sigma)
    ax.plot(x, y, 'r-', lw=2, label='Normal Fit')

    # Draw colored regions for 1 SD, 2 SD, and 3 SD based on fitted distribution
    x_1sd = np.linspace(mu - sigma, mu + sigma, 100)
    y_1sd = norm.pdf(x_1sd, mu, sigma)
    ax.fill_between(x_1sd, y_1sd, color='green', alpha=0.3, label='1 SD (68%)')

    x_2sd = np.linspace(mu - 2 * sigma, mu + 2 * sigma, 100)
    y_2sd = norm.pdf(x_2sd, mu, sigma)
    ax.fill_between(x_2sd, y_2sd, color='yellow', alpha=0.2, label='2 SD (95%)')

    x_3sd = np.linspace(mu - 3 * sigma, mu + 3 * sigma, 100)
    y_3sd = norm.pdf(x_3sd, mu, sigma)
    ax.fill_between(x_3sd, y_3sd, color='blue', alpha=0.1, label='3 SD (99.7%)')

    # Customize plot
    ax.set_title(f'Daily Consumption Distribution ({deviation_label})')
    ax.set_xlabel(f'Consumption (Target = {target_value})')  # Display target value
    ax.set_ylabel('Density')
    ax.set_xlim(fixed_min, fixed_max)  # Set fixed x-axis limits
    ax.legend()

    # Display in Streamlit
    st.pyplot(fig)