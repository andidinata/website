import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta, date
from io import BytesIO

def simulate_ddmrp_inventory(rop, max_qty, critical_level, moq, delivery_lead_time, qty_per_package, 
                            monthly_usage_avg, current_usage, w1, w2, w3, w4, w5, tol, 
                            beginning_inventory, inventory_value, sim_days, start_date=datetime.now()):
    daily_avg_use = monthly_usage_avg / 30 
    inventory_actual = beginning_inventory
    inventory_avg = beginning_inventory
    dates = [start_date]
    inventory_actual_levels = [inventory_actual]
    inventory_avg_levels = [inventory_avg]
    pending_orders_actual = []  # (delivery_date, quantity, order_day) for Inventory_Actual
    pending_orders_avg = []     # (delivery_date, quantity, order_day) for Inventory_Avg
    order_annotations = []
    critical_crossings = []  # Store (date, inventory_actual) when crossing critical_level going down

    for day in range(sim_days):
        current_date = start_date + timedelta(days=day)
        dates.append(current_date)
        previous_inventory_actual = inventory_actual
        previous_inventory_avg = inventory_avg
        
        # Determine which week (W1-W5) this day belongs to in the month
        days_into_month = (current_date - start_date.replace(day=1)).days % 30
        if days_into_month < 6:  # Week 1 (days 0-5)
            weekly_proportion = w1
        elif days_into_month < 12:  # Week 2 (days 6-11)
            weekly_proportion = w2
        elif days_into_month < 18:  # Week 3 (days 12-17)
            weekly_proportion = w3
        elif days_into_month < 24:  # Week 4 (days 18-23)
            weekly_proportion = w4
        else:  # Week 5 (days 24-29)
            weekly_proportion = w5
        
        # Calculate daily consumption for Inventory_Actual with tolerance
        base_daily_use = (current_usage * weekly_proportion) / 6
        tolerance_factor = np.random.uniform(1 - tol, 1 + tol)
        daily_consumption_actual = base_daily_use * tolerance_factor
        
        # Update inventories
        inventory_actual = max(0, inventory_actual - daily_consumption_actual)
        inventory_avg = max(0, inventory_avg - daily_avg_use)
        
        # Check for delivered orders for Inventory_Actual
        for delivery_date, qty, order_date in pending_orders_actual[:]:
            if current_date >= delivery_date:
                inventory_actual += qty
                order_amount = qty * inventory_value
                order_annotations.append({
                    'x': delivery_date,
                    'y': inventory_actual,
                    'text': f'Actual Order: {int(qty)}\n({order_amount:,.0f})',
                    'showarrow': True,
                    'arrowhead': 1,
                    'ax': 20,
                    'ay': -30,
                    'font': {'color': 'green', 'size': 10},
                    'bgcolor': 'rgba(255, 255, 255, 0.8)',
                    'bordercolor': 'green',
                    'borderwidth': 1
                })
                pending_orders_actual.remove((delivery_date, qty, order_date))
        
        # Check for delivered orders for Inventory_Avg
        for delivery_date, qty, order_date in pending_orders_avg[:]:
            if current_date >= delivery_date:
                inventory_avg += qty
                order_amount = qty * inventory_value
                order_annotations.append({
                    'x': delivery_date,
                    'y': inventory_avg,
                    'text': f'Avg Order: {int(qty)}\n({order_amount:,.0f})',
                    'showarrow': True,
                    'arrowhead': 1,
                    'ax': 20,
                    'ay': -30,
                    'font': {'color': 'purple', 'size': 10},
                    'bgcolor': 'rgba(255, 255, 255, 0.8)',
                    'bordercolor': 'purple',
                    'borderwidth': 1
                })
                pending_orders_avg.remove((delivery_date, qty, order_date))
        
        # Check if Inventory_Actual falls below ROP and place order
        if inventory_actual <= rop and not any(current_date < d[0] < current_date + timedelta(days=delivery_lead_time) 
                                            for d in pending_orders_actual):
            actual_order_qty = max(moq, 
                                 np.ceil((max_qty - inventory_actual) / qty_per_package) * qty_per_package)
            actual_order_qty = min(actual_order_qty, max_qty - inventory_actual)
            delivery_date = current_date + timedelta(days=delivery_lead_time)
            pending_orders_actual.append((delivery_date, actual_order_qty, current_date))

        # Check if Inventory_Avg falls below ROP and place order
        if inventory_avg <= rop and not any(current_date < d[0] < current_date + timedelta(days=delivery_lead_time) 
                                         for d in pending_orders_avg):
            avg_order_qty = max(moq, 
                               np.ceil((max_qty - inventory_avg) / qty_per_package) * qty_per_package)
            avg_order_qty = min(avg_order_qty, max_qty - inventory_avg)
            delivery_date = current_date + timedelta(days=delivery_lead_time)
            pending_orders_avg.append((delivery_date, avg_order_qty, current_date))

        # Detect crossing below critical_level when inventory_actual is going down
        if (inventory_actual <= critical_level and 
            (day == 0 or (previous_inventory_actual > critical_level and inventory_actual < previous_inventory_actual))):
            critical_crossings.append((current_date, inventory_actual))

        inventory_actual_levels.append(min(inventory_actual, max_qty))
        inventory_avg_levels.append(min(inventory_avg, max_qty))

    df = pd.DataFrame({
        'Date': dates,
        'Inventory_Actual': inventory_actual_levels,
        'Inventory_Avg': inventory_avg_levels,
        'ROP': [rop] * len(dates),
        'Max_Qty': [max_qty] * len(dates),
        'Critical_Level': [critical_level] * len(dates)
    })
    
    order_dates_actual = [d[2] for d in pending_orders_actual]
    if len(order_dates_actual) > 1:
        avg_cycle_actual = np.mean([(order_dates_actual[i+1] - order_dates_actual[i]).days 
                                   for i in range(len(order_dates_actual)-1)])
    else:
        avg_cycle_actual = None

    # Annotations for critical crossings (markers with date and value)
    critical_crossing_annotations = []
    for crossing_date, crossing_inventory in critical_crossings:
        critical_crossing_annotations.append({
            'x': crossing_date,
            'y': crossing_inventory,
            'text': f'{crossing_date.strftime("%Y-%m-%d")}\n{crossing_inventory:.0f}',
            'showarrow': True,
            'arrowhead': 1,
            'ax': 0,
            'ay': -40,
            'font': {'color': 'blue', 'size': 10},
            'bgcolor': 'rgba(255, 255, 255, 0.8)',
            'bordercolor': 'blue',
            'borderwidth': 1
        })

    # Calculate time gaps and horizontal lines between critical crossings
    critical_gap_annotations = []
    if len(critical_crossings) > 1:
        for i in range(1, len(critical_crossings)):
            prev_date, prev_inventory = critical_crossings[i-1]
            curr_date, curr_inventory = critical_crossings[i]
            gap_days = (curr_date - prev_date).days
            mid_date = prev_date + timedelta(days=gap_days // 2)
            critical_gap_annotations.append({
                'x': mid_date,
                'y': critical_level,
                'text': f'<- {gap_days} days ->',
                'showarrow': False,
                'font': {'color': 'red', 'size': 12},
                'bgcolor': 'rgba(255, 255, 255, 0.8)',
                'bordercolor': 'red',
                'borderwidth': 1
            })
            df['Critical_Crossing_Line'] = np.nan
            df.loc[df['Date'].isin([prev_date, curr_date]), 'Critical_Crossing_Line'] = critical_level

    return df, avg_cycle_actual, daily_avg_use, order_annotations, critical_crossing_annotations, critical_gap_annotations, critical_crossings

# Function to convert DataFrame to Excel bytes
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    return excel_data

st.subheader("Batch Inventory Simulation")

# Updated Excel column names
excel_template_columns = [
    'Material Name',
    'Monthly Usage Average',
    'Current Usage',
    'Beginning Inventory',
    'Lead Time (days)',
    'Critical Level',
    'Re-Order Point (ROP)',
    'Maximum Quantity',
    'Inventory Value per UoM',
    'Quantity per Package',
    'Minimum Order Quantity (MOQ)',
    'Simulation Days',
    'W1', 'W2', 'W3', 'W4', 'W5',
    'TOL'
]

# File uploader for Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    materials_df = pd.read_excel(uploaded_file)
    if 'Simulation Days' in materials_df.columns:
        materials_df['Simulation Days'] = materials_df['Simulation Days'].astype(int)
    
    required_columns = excel_template_columns
    missing_columns = [col for col in required_columns if col not in materials_df.columns]
    if missing_columns:
        st.error(f"Excel file is missing required columns: {', '.join(missing_columns)}.")
    else:
        with st.expander("Preview and Edit Materials Data"):
            edited_df = st.data_editor(materials_df, num_rows="dynamic")
            materials_data = edited_df
            original_filename = uploaded_file.name
            base_name = original_filename.rsplit('.', 1)[0]
            new_filename = f"{base_name}_edited.xlsx"
            excel_data = to_excel(edited_df)
            st.download_button(
                label="Download Edited Data as Excel",
                data=excel_data,
                file_name=new_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        start_date_input = st.date_input("Simulation Start Date", 
                                        value=date.today(),
                                        min_value=date.today() - timedelta(days=365),
                                        max_value=date.today() + timedelta(days=365))
        start_date = datetime.combine(start_date_input, datetime.min.time())

        num_materials = len(materials_data)
        num_rows = (num_materials + 1) // 2

        # Calculate number of materials (no need for num_rows since it's one row per material)
        num_materials = len(materials_data)

        # Simulation and visualization with one row per material
        for material_idx in range(num_materials):
            # Create a single row with 2 columns: chart on left, table on right
            col_chart, col_table = st.columns([1, 1])  # 3:1 ratio for chart:table width

            with col_chart:
                row = materials_data.iloc[material_idx]
                material_name = row['Material Name']
                monthly_usage_avg = row['Monthly Usage Average']
                current_usage = row['Current Usage']
                beginning_inventory = row['Beginning Inventory']
                delivery_lead_time = row['Lead Time (days)']
                critical_level = row['Critical Level']
                rop = row['Re-Order Point (ROP)']
                max_qty = row['Maximum Quantity']
                inventory_value = row['Inventory Value per UoM']
                qty_per_package = row['Quantity per Package']
                moq = row['Minimum Order Quantity (MOQ)']
                sim_days = int(row['Simulation Days'])
                w1, w2, w3, w4, w5 = row['W1'], row['W2'], row['W3'], row['W4'], row['W5']
                tol = row['TOL']

                df, avg_cycle, daily_avg_use, order_annotations, critical_crossing_annotations, critical_gap_annotations, critical_crossings = simulate_ddmrp_inventory(
                    rop, max_qty, critical_level, moq, delivery_lead_time, qty_per_package,
                    monthly_usage_avg, current_usage, w1, w2, w3, w4, w5, tol,
                    beginning_inventory, inventory_value, sim_days, start_date
                )

                fig = px.line(df, x='Date', y=['Inventory_Actual', 'Inventory_Avg', 'ROP', 'Max_Qty', 'Critical_Level'],
                              title=f'Inventory Simulation for {material_name} (Starting {start_date.strftime("%Y-%m-%d")})')
                
                end_date = start_date + timedelta(days=sim_days)
                current_date = start_date.replace(day=1)
                month_end_dates = []
                while current_date <= end_date:
                    next_month = current_date.replace(day=28) + timedelta(days=4)
                    last_day = next_month - timedelta(days=next_month.day)
                    if last_day >= start_date and last_day <= end_date:
                        month_end_dates.append(last_day)
                    current_date = (last_day + timedelta(days=1)).replace(day=1)
                
                month_end_df = df[df['Date'].isin(month_end_dates)].copy()
                fig.add_scatter(
                    x=month_end_df['Date'],
                    y=month_end_df['Inventory_Actual'],
                    mode='markers',
                    marker=dict(symbol='circle', size=10, color='grey', opacity=0.7),
                    name='Month End',
                    hovertemplate='%{x|%Y-%m-%d}<br>Inventory: %{y:.0f}'
                )

                if critical_crossings:
                    crossing_dates = [crossing[0] for crossing in critical_crossings]
                    crossing_values = [crossing[1] for crossing in critical_crossings]
                    fig.add_scatter(
                        x=crossing_dates,
                        y=crossing_values,
                        mode='markers',
                        marker=dict(symbol='x', size=10, color='blue'),
                        name='Critical Crossing',
                        hovertemplate='%{x|%Y-%m-%d}<br>Inventory: %{y:.0f}'
                    )

                if 'Critical_Crossing_Line' in df.columns:
                    fig.add_scatter(
                        x=df['Date'],
                        y=df['Critical_Crossing_Line'],
                        mode='lines',
                        line=dict(color='red', dash='dash'),
                        name='Gap Line',
                        hoverinfo='skip'
                    )

                all_annotations = order_annotations + critical_crossing_annotations + critical_gap_annotations
                fig.update_layout(
                    yaxis_title="Inventory Qty",
                    legend_title="Metrics",
                    xaxis_title="Date",
                    yaxis=dict(range=[0, max(max_qty, df['Inventory_Actual'].max(), df['Inventory_Avg'].max()) * 1.1]),
                    annotations=all_annotations,
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        traceorder="normal",
                        itemsizing="constant",
                        itemwidth=80,
                        font=dict(size=10)
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_table:
                interval_data = []
                current_date = start_date.replace(day=1)
                while current_date <= end_date:
                    next_month = current_date.replace(day=28) + timedelta(days=4)
                    last_day = next_month - timedelta(days=next_month.day)
                    if last_day >= start_date and last_day <= end_date:
                        qty = df.loc[df['Date'] == last_day, 'Inventory_Actual'].iloc[0] if not df[df['Date'] == last_day].empty else 0
                        value = qty * inventory_value
                        interval_data.append({
                            'Date': last_day.strftime('%Y-%m-%d'),
                            'Inventory Quantity': f"{qty:,.0f}",
                            'Inventory Value': f"{value:,.0f}"
                        })
                    current_date = (last_day + timedelta(days=1)).replace(day=1)
                
                interval_df = pd.DataFrame(interval_data)
                st.write(f"Month-End Inventory for {material_name})")
                st.dataframe(interval_df)
else:
    st.info("Please upload an Excel file to start the simulation.")