import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle

# Material density dictionary
density = {'ALU': 2.71, 'PET': 1.4, 'NYLON': 1.16, 'OPP': 0.91}

def roll_weight_calculator():
    st.subheader("Roll Weight")
    
    # First container: Input parameters (4 columns)
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            width = st.number_input("Width", value=0.0, key="width")
        
        with col2:
            thick = st.number_input("Thick", value=0.0, key="thick")
        
        with col3:
            material = st.selectbox("Material", ['ALU', 'PET', 'NYLON', 'OPP'], key="material")
        
        with col4:
            length = st.selectbox("Length (m)", [6000, 8000, 12000, 24000, 36000], key="length")

    # Calculate base roll weight
    roll_kg = 0.0
    if width and thick and material and length:
        d = density[material]
        roll_kg = round(width * thick * d * length / 10e5, 2)

    # Second container: Roll-based calculations (5 columns)
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            roll_num = st.number_input(
                "Total Roll",
                value=0.0,
                step=0.01,
                key="roll_num_input",
                help="Enter number of rolls to calculate total weight"
            )
        
        with col2:
            st.metric("Weight per Roll (kg)", f'{roll_kg:#,.1f}' if roll_kg > 0 else 0.0)
        
        with col3:
            total_kg_from_rolls = round(roll_kg * roll_num, 2) if roll_num > 0 and roll_kg > 0 else 0.0
            st.metric("Total Weight (kg)", f'{total_kg_from_rolls:#,.1f}')
        
        with col4:
            total_length_from_rolls = roll_num * length if roll_num > 0 else 0.0
            st.metric("Total Length (m)", f'{total_length_from_rolls:#,.1f}')

    # Third container: Length-based calculations (5 columns)
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sum_length = st.number_input(
                "Total Length (km)",
                value=0.0,
                key="sum_length_input",
                help="Enter total length to calculate number of rolls and total weight"
            )
        
        with col2:
            calculated_rolls = round(sum_length*1000 / length, 2) if sum_length > 0 and length > 0 else 0.0
            st.metric("Calculated Rolls", f'{calculated_rolls:#,.1f}')
        
        with col3:
            total_kg_from_length = round(roll_kg * calculated_rolls, 2) if roll_kg > 0 and calculated_rolls > 0 else 0.0
            st.metric("Total Weight (kg)", f'{total_kg_from_length:#,.1f}')
        
        with col4:
            st.empty()

    # Fourth container: Weight-based calculations (4 columns)
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_weight = st.number_input(
                "Total Weight (T)",
                value=0.0,
                key="total_weight_input",
                help="Enter total weight to calculate number of rolls and total length"
            )
        
        with col2:
            calculated_rolls_from_weight = round(total_weight*1000 / roll_kg, 2) if total_weight > 0 and roll_kg > 0 else 0.0
            st.metric("Calculated Rolls", f'{calculated_rolls_from_weight:#,.1f}')
        
        with col3:
            total_length_from_weight = calculated_rolls_from_weight * length if calculated_rolls_from_weight > 0 else 0.0
            st.metric("Total Length (m)", f'{total_length_from_weight:#,.1f}')
        
        with col4:
            st.empty()

    # Fifth container: Diameter calculation (4 columns)
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            core_diameter = st.number_input(
                "Core Diameter (inch)",
                value=0.0,
                step=0.1,
                key="core_diameter",
                help="Enter core diameter in inches"
            )
        
        with col2:
            # Calculate outer diameter (simplified approximation)
            # Convert thickness to meters (assuming thick is in microns)
            thickness_m = thick * 1e-6 if thick > 0 else 0
            core_diameter_m = core_diameter * 0.0254  # Convert inches to meters
            core_diameter_mm = core_diameter * 25.4  # Convert inches to mm for display
            
            # Approximate outer diameter using roll length and thickness
            if thickness_m > 0 and length > 0 and core_diameter_m > 0:
                # Simplified formula: area = π(R² - r²) where area = length * thickness
                area = length * thickness_m
                outer_radius_m = np.sqrt(area/np.pi + (core_diameter_m/2)**2)
                outer_diameter_m = 2 * outer_radius_m
                outer_diameter_mm = round(outer_diameter_m * 1000, 2)  # Convert to mm
            else:
                outer_diameter_mm = 0.0
            
            st.metric("Outer Diameter (mm)", f'{outer_diameter_mm:#,.2f}')

        with col3:
            st.empty()
        with col4:
            st.empty()
        
    with st.container():
        # Create sketch of a horizontal cylinder
        if outer_diameter_mm > 0 and core_diameter_mm > 0 and width > 0:
            fig, ax = plt.subplots(figsize=(5, 3))
            
            # Convert all dimensions to mm for consistency
            width_mm = width  # Assuming width is already in mm from first container
            outer_radius_mm = outer_diameter_mm / 2
            core_radius_mm = core_diameter_mm / 2
            
            # Draw the outer cylinder body (rectangle for side view)
            outer_body = Rectangle((-width_mm/2, -outer_radius_mm), width_mm, outer_diameter_mm, 
                                 fill=True, color='lightblue', alpha=0.5)
            ax.add_patch(outer_body)
            
            # Draw the core cylinder body (inner rectangle)
            core_body = Rectangle((-width_mm/2, -core_radius_mm), width_mm, core_diameter_mm, 
                                fill=True, color='gray', alpha=0.5)
            ax.add_patch(core_body)
            
            # Draw the left end of the outer cylinder (ellipse)
            outer_left = Ellipse((-width_mm/2, 0), outer_diameter_mm/2, outer_diameter_mm, 
                               fill=True, color='lightblue')
            ax.add_patch(outer_left)
            
            # Draw the right end of the outer cylinder (ellipse)
            outer_right = Ellipse((width_mm/2, 0), outer_diameter_mm/2, outer_diameter_mm, 
                                fill=False, color='blue')
            ax.add_patch(outer_right)
            
            # Draw the left end of the core (ellipse)
            core_left = Ellipse((-width_mm/2, 0), core_diameter_mm/2, core_diameter_mm, 
                              fill=False, color='red')
            ax.add_patch(core_left)
            
            # Draw the right end of the core (ellipse)
            core_right = Ellipse((width_mm/2, 0), core_diameter_mm/2, core_diameter_mm, 
                               fill=False, color='red')
            ax.add_patch(core_right)
            
            # Annotations
            # Outer diameter
            ax.annotate(f'Outer: {outer_diameter_mm:.2f} mm',
                       xy=(0, outer_radius_mm),
                       xytext=(0, outer_radius_mm + 20),
                       ha='center')
#                           arrowprops=dict(facecolor='black', shrink=0.05))
            
            # Core diameter
            ax.annotate(f'Core: {core_diameter_mm:.2f} mm',
                       xy=(0, core_radius_mm),
                       xytext=(0, core_radius_mm + 10),
                       ha='center')
#                           arrowprops=dict(facecolor='black', shrink=0.05))
            
            # Width
            ax.annotate(f'Width: {width_mm:.2f} mm',
                       xy=(0, -outer_radius_mm),
                       xytext=(0, -outer_radius_mm - 20),
                       ha='center')
#                           arrowprops=dict(facecolor='black', shrink=0.05))
            
            # Set limits and aspect
            ax.set_xlim(-width_mm/2 - 120, width_mm/2 + 120)
            ax.set_ylim(-outer_diameter_mm/2 - 50, outer_diameter_mm/2 + 50)
            ax.set_aspect('equal')
            ax.axis('off')
            
            st.pyplot(fig)
        else:
            st.write("Enter values to see roll sketch")
        

def main():
    roll_weight_calculator()

if __name__ == "__main__":
    main()
