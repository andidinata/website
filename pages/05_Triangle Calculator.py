import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math

st.header("Triangle")

def guess_triangle(a,b,c):
    if not (a + b > c and a + c > b and b + c > a):
        st.write("Not a triangle")
    else:    
        if a > 0 and b > 0 and c > 0:    
            if a == b and b == c and c == a:
                st.write("equilateral")
                return "equilateral"
            elif a == b or b == c or c == a:
                st.write("isoceles")
                return "isoceles"
            elif (a**2) + (b**2) == (c**2) or (a**2) + (c**2) == (b**2) or (b**2) + (c**2) == (a**2):
                st.write("right-angle")
                return "right-angle"
            else:
                st.write("scalene")
                return "scalene"
        else:
            st.write("value should not be less or equal to zero")
            return "none"

def calculate_angles(a, b, c):
    try:
        angle_A = math.degrees(math.acos((b**2 + c**2 - a**2) / (2 * b * c)))
        angle_B = math.degrees(math.acos((a**2 + c**2 - b**2) / (2 * a * c)))
        angle_C = math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))
        return angle_A, angle_B, angle_C
    except (ValueError,TypeError) as e:
        st.write(f"ValueError: Unable to calculate angles. {e}")
        return None, None, None

def draw_triangle(a, b, c, triangle_type):
    plt.figure(figsize=(5, 5))
    if triangle_type == "none":
        st.write("Unable to draw the triangle.")
        return
        
    if triangle_type == "equilateral":
        points = np.array([[0, 0], 
                           [a, 0], 
                           [a/2, (np.sqrt(3)/2) * a]])
    elif triangle_type == "isosceles":
        if a == b:
            points = np.array([[0, 0], 
                               [c, 0], 
                               [c / 2, np.sqrt(a**2 - (c / 2)**2)]])
        elif b == c:
            points = np.array([[0, 0], 
                               [a, 0], 
                               [a / 2, np.sqrt(b**2 - (a / 2)**2)]])
        else:
            points = np.array([[0, 0], 
                               [b, 0], 
                               [b / 2, np.sqrt(c**2 - (b / 2)**2)]])
    elif triangle_type == "right-angle":
        points = np.array([[0, 0], 
                           [a, 0], 
                           [0, b]])
    else:  # scalene
        points = np.array([[0, 0], 
                           [a, 0], 
                           [b * np.cos(np.arccos((a**2 + b**2 - c**2) / (2 * a * b))), 
                            b * np.sin(np.arccos((a**2 + b**2 - c**2) / (2 * a * b)))]])
    
    plt.plot([points[0][0], points[1][0]], [points[0][1], points[1][1]], 'k-')
    plt.plot([points[1][0], points[2][0]], [points[1][1], points[2][1]], 'k-')
    plt.plot([points[2][0], points[0][0]], [points[2][1], points[0][1]], 'k-')
    plt.fill(points[:, 0], points[:, 1], color="skyblue", alpha=0.5)
  
    plt.text((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2, f'{a}', ha='center')
    plt.text((points[1][0] + points[2][0]) / 2, (points[1][1] + points[2][1]) / 2, f'{b}', ha='center')
    plt.text((points[2][0] + points[0][0]) / 2, (points[2][1] + points[0][1]) / 2, f'{c}', ha='center')

    angle_A, angle_B, angle_C = calculate_angles(a, b, c)
    plt.text(points[0][0], points[0][1], f'{angle_A:.1f}°', ha='right')
    plt.text(points[1][0], points[1][1], f'{angle_B:.1f}°', ha='right')
    plt.text(points[2][0], points[2][1], f'{angle_C:.1f}°', ha='right')

    
    plt.axis("equal")
    plt.axis("off")
    plt.show()
    st.pyplot(plt)
  
    peri = a + b + c
    st.write(f'Perimeter: {peri}')
    
    s = peri / 2

    A = math.sqrt(s*((s-a)*(s-b)*(s-c)))
    st.write(f'Area: {A:.2f} square')
   
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.write("Triangle Input")
        # a = st.number_input("A side")
        a = st.slider("A side", min_value = 0 , max_value = 100, value = 50)
        # b = st.number_input("B side")
        b = st.slider("B side", min_value = 0 , max_value = 100, value = 50)
        # c = st.number_input("C side")
        c = st.slider("C side", min_value = 0 , max_value = 100, value = 50)

        triangle_type = guess_triangle(a,b,c)
        
with c2:
    with st.container(border=True):
        st.write("Triangle Picture")
        draw_triangle(a, b, c, triangle_type)

        
        



# guess_triangle(5,30,40)
