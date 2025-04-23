import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta, date

def simulate_ddmrp_inventory(rop, max_qty, critical_level, moq, 
                           delivery_lead_time, qty_per_package, monthly_usage_avg, 
                           beginning_inventory, inventory_value, sim_days=90, start_date=datetime.now()):
    daily_avg_use = monthly_usage_avg / 30
    inventory = beginning_inventory
    dates = [start_date]
    inventory_levels = [inventory]
    pending_orders = []  # (delivery_date, quantity, order_day)
    order_annotations = []

    daily_consumption = np.random.uniform(daily_avg_use / 1.25, 
                                        daily_avg_use * 1.25, 
                                        sim_days)

    for day in range(sim_days):
        current_date = start_date + timedelta(days=day)
        dates.append(current_date)
        inventory = max(0, inventory - daily_consumption[day])
        
        # Check for delivered orders
        for delivery_date, qty, order_date in pending_orders[:]:
            if current_date >= delivery_date:
                inventory += qty
                order_amount = qty * inventory_value
                order_annotations.append({
                    'x': delivery_date,
                    'y': inventory,
                    'text': f'Order: {int(qty)}\n({order_amount:,.0f})',
                    'showarrow': True,
                    'arrowhead': 1,
                    'ax': 20,
                    'ay': -30
                })
                pending_orders.remove((delivery_date, qty, order_date))
        
        # Check if inventory falls below ROP and place order if needed
        if inventory <= rop and not any(current_date < d[0] < current_date + timedelta(days=delivery_lead_time) 
                                     for d in pending_orders):
            actual_order_qty = max(moq, 
                                 np.ceil((max_qty - inventory) / qty_per_package) * qty_per_package)
            actual_order_qty = min(actual_order_qty, max_qty - inventory)
            
            delivery_date = current_date + timedelta(days=delivery_lead_time)
            pending_orders.append((delivery_date, actual_order_qty, current_date))

        inventory_levels.append(min(inventory, max_qty))

    df = pd.DataFrame({
        'Date': dates,
        'Inventory': inventory_levels,
        'ROP': [rop] * len(dates),
        'Max_Qty': [max_qty] * len(dates),
        'Critical_Level': [critical_level] * len(dates)
    })
    
    order_dates = [d[2] for d in pending_orders]
    if len(order_dates) > 1:
        avg_cycle = np.mean([(order_dates[i+1] - order_dates[i]).days 
                           for i in range(len(order_dates)-1)])
    else:
        avg_cycle = None

    return df, avg_cycle, daily_avg_use, order_annotations

st.header("Inventory Simulation")

col_left, col_right = st.columns(2)

with col_left:    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_usage_avg = st.number_input("Monthly Usage Average", 
                                          min_value=10, 
                                          max_value=9000, 
                                          value=900, 
                                          step=1)
        
        daily_usage_avg = monthly_usage_avg / 30
        
        delivery_lead_time = st.number_input("Lead Time (days)", 
                                           min_value=1, 
                                           max_value=120, 
                                           value=7, 
                                           step=1)
        
        critical_default = int(daily_usage_avg * delivery_lead_time)
        if st.checkbox("Run to zero"):
          critical_default = 0
        critical_level = st.number_input("Critical Level", 
                                       min_value=0, 
                                       max_value=9000, 
                                       value=critical_default, 
                                       step=1)
        
        rop_default = int((daily_usage_avg * delivery_lead_time) + critical_level)
        rop = st.number_input("Re-Order Point (ROP)", 
                            min_value=0, 
                            max_value=9000, 
                            value=rop_default, 
                            step=1)
      
        
    with col2:
        beginning_inventory_default = int(monthly_usage_avg)
        beginning_inventory = st.number_input("Inventory Quantity", 
                                            min_value=0, 
                                            max_value=9000, 
                                            value=beginning_inventory_default, 
                                            step=1)

        max_qty_default = int(monthly_usage_avg + rop)
        if st.checkbox("Half Monthly Usage"):
          max_qty_default = int((0.5*monthly_usage_avg) + rop)
        max_qty = st.number_input("Maximum Quantity", 
                                min_value=rop, 
                                max_value=9000, 
                                value=max_qty_default, 
                                step=1)
        
        inventory_value = st.number_input("Material price per UoM", 
                                        min_value=0.01, 
                                        max_value=500000.00, 
                                        value=1.00, 
                                        step=0.01,
                                        format="%.2f")

        qty_per_package = st.number_input("Quantity per Package", 
                                        min_value=1, 
                                        max_value=100, 
                                        value=1, 
                                        step=1)
        moq = st.number_input("Minimum Order Quantity (MOQ)", 
                            min_value=0, 
                            max_value=500, 
                            value=qty_per_package, 
                            step=1)
        
    with col1:
      sim_days = st.number_input("Simulation Days", 
                                   min_value=30, 
                                   max_value=365, 
                                   value=90, 
                                   step=1)

# Right column: Chart and Results
with col_right:
    start_date_input = st.date_input("Simulation Start Date", 
                                   value=date.today(),
                                   min_value=date.today() - timedelta(days=365),
                                   max_value=date.today() + timedelta(days=365))
    
    # Convert date to datetime for consistency with simulation
    start_date = datetime.combine(start_date_input, datetime.min.time())

    # Run simulation with start_date parameter
    df, avg_cycle, daily_avg_use, order_annotations = simulate_ddmrp_inventory(
        rop, max_qty, critical_level, moq, 
        delivery_lead_time, qty_per_package, monthly_usage_avg, 
        beginning_inventory, inventory_value, sim_days, start_date
    )
    
    # Calculate end-of-month dates for markers and table
    end_date = start_date + timedelta(days=sim_days)
    current_date = start_date.replace(day=1)
    month_end_dates = []
    
    while current_date <= end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        if last_day >= start_date and last_day <= end_date:
            month_end_dates.append(last_day)
        current_date = (last_day + timedelta(days=1)).replace(day=1)

    # Filter DataFrame for month-end dates only for markers
    month_end_df = df[df['Date'].isin(month_end_dates)].copy()
    
    fig = px.line(df, x='Date', y=['Inventory', 'ROP', 'Max_Qty', 'Critical_Level'],
                 title=f'Inventory Simulation (Starting {start_date.strftime("%Y-%m-%d")})')
    
    # Add markers for month ends on the Inventory line
    fig.add_scatter(
        x=month_end_df['Date'],
        y=month_end_df['Inventory'],
        mode='markers',
        marker=dict(
            symbol='circle',
            size=10,
            color='grey',
            opacity=0.7
        ),
        name='Month End',
        hovertemplate='%{x|%Y-%m-%d}<br>Inventory: %{y:.0f}'
    )
    
    fig.update_layout(
        yaxis_title="Inventory Qty",
        legend_title="Metrics",
        xaxis_title="Date",
        yaxis=dict(range=[0, max(max_qty, df['Inventory'].max()) * 1.1]),
        annotations=order_annotations
    )
    st.plotly_chart(fig, use_container_width=True)
        
    st.write(f"Daily Average Use: {daily_avg_use:.1f} units")

with col_left:
    rop_formula = (r"\text{ROP} = (\text{Daily Usage} \times \text{Lead Time}) + \text{Critical Level} = "
                  f"({daily_usage_avg:.1f} \\times {delivery_lead_time}) + {critical_level} = {rop_default}")
    max_qty_formula = r"\text{Max Qty} = \text{Monthly Usage Avg} + \text{ROP} = " + f"{monthly_usage_avg} + {rop} = {max_qty_default}"
    critical_formula = (r"\text{Critical Level} = \text{Daily Usage} \times \text{Lead Time} = "
                      f"{daily_usage_avg:.1f} \\times {delivery_lead_time} = {critical_default}")
    order_qty_formula = r"\text{Order Qty} = \max(\text{MOQ}, \lceil\frac{\text{Max Qty} - \text{Inventory}}{\text{Qty per Package}}\rceil \times \text{Qty per Package})"

    st.latex(rop_formula)
    st.latex(max_qty_formula)
    st.latex(critical_formula)
    st.latex(order_qty_formula)

with col_right:
    # Calculate end-of-month dates within simulation period
    interval_data = []
    current_date = start_date.replace(day=1)  # Start from beginning of month
    
    while current_date <= end_date:
        # Get last day of current month
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        
        if last_day >= start_date and last_day <= end_date:
            # Find the inventory for this exact date
            qty = df.loc[df['Date'] == last_day, 'Inventory'].iloc[0] if not df[df['Date'] == last_day].empty else 0
            value = qty * inventory_value
            interval_data.append({
                'Date': last_day.strftime('%Y-%m-%d'),
                'Inventory Quantity': f"{qty:,.0f}",
                'Inventory Value': f"{value:,.0f}"
            })
        current_date = (last_day + timedelta(days=1)).replace(day=1)  # Move to next month

    interval_df = pd.DataFrame(interval_data)
    st.table(interval_df)
