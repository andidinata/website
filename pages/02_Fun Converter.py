import streamlit as st

st.title('Fun Conversion App')

conversion_factors = {
  'calories': {'fries':319/319,
               'donut':319/190,
               'burger':319/290,
               'ice cream':319/207,
               'apple':319/52.1,
               'banana':319/88.7,
               'cabbage':319/24.6,
               'coke':319/139,
               'milk':319/42.3,
               'instant noodles':319/340},
  'weight':{'gr':1/0.001,
            'kg':1,
            'ton':1/1000,
            'adult person':1/70,
            'a teenager':1/40,
            'cat':None,
            'mouse':None,
            'dog':None,
            'cow':None,
            'elephant':None,
            'giraffe':None,
            'penguin':None,
            'dolphin':None,
            'blue whale':None,
            'brontosaurus':None,
            't-rex':None},
  'time':{'seconds':3600,
          'minutes':60,
          'hour':1,
          'day':1/24,
          'week':1/((24*7)),
          'month':1/(24*30),
          'year':1/(24*365),
          'cat year':1/(24*365*5),
          'dog year':None}}

picture_link = {'fries':'./images/fries.jpeg',
                'donut':'./images/donut.jpeg',
                'burger':'./images/burger.jpeg',
                'ice cream':'./images/ice_cream.jpeg',
                'apple':'./images/apple.jpeg',
                'banana':'./images/banana.jpeg',
                'cabbage':'./images/cabbage.jpeg',
                'coke':'./images/coke.jpeg',
                'milk':'./images/milk.jpeg',
                'instant noodles':'./images/instant_noodles.jpeg'}

col1,col2,col3,col4,col5 = st.columns(5)

with col1:
#category selection
    category_list = list(conversion_factors.keys())
    category = st.radio("Select category",options=category_list)

with col2:
    input_value = st.number_input("Input",min_value=1,value=1)
    
with col3:
    base_unit_list = list(conversion_factors[category].keys())
    base_unit = st.radio("From:",options=base_unit_list)
    base_cf = conversion_factors[category][base_unit]
    st.image(picture_link[base_unit])

with col4:
    target_unit_list = list(conversion_factors[category].keys())
    target_unit = st.radio("To:",options=target_unit_list)
    target_cf = conversion_factors[category][target_unit]
    st.image(picture_link[target_unit])

with col5:
    st.write("Output:")
    output_value = input_value / base_cf * target_cf
    st.write(f'The {category} of {input_value} {base_unit} equals to {output_value:.2f} {target_unit}')
