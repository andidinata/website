import streamlit as st
import pandas as pd

@st.cache_data
def get_data():
    data = pd.read_excel('./pages/dataset_marketplace.xlsx')
    return data

data = get_data()

stores = data['store'].unique()
category = sorted(list(data['category'].unique()),reverse=False)
product = sorted(list(data['product'].unique()),reverse=False)

with st.container(border=True):
    st.write("Filters")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        filter_store = st.selectbox("Filter Store",options=stores,index=None)
    with col2:
        filter_category = st.selectbox("Filter Category",options=category, index=None)
    with col3:
        filter_product = st.selectbox("Filter Product",options=product,index=None)

    if filter_category is None:
        min_price=data['price'].min()
        max_price=data['price'].max()
    else:
        min_price = data[data['category'] == filter_category]['price'].min()
        max_price = data[data['category'] == filter_category]['price'].max()
    with col4:   
        filter_price = st.slider("Price Filter",
                                min_value=min_price,
                                max_value=max_price,
                                value=max_price)

def filter_data(data):
    filtered_data = data.copy()

    if filter_store:
        filtered_data = filtered_data[filtered_data['store'] == filter_store]
    if filter_category:
        filtered_data = filtered_data[filtered_data['category'] == filter_category]
    if filter_product:
        filtered_data = filtered_data[filtered_data['product'] == filter_product]
    if filter_price:
        filtered_data = filtered_data[filtered_data['price'] <= filter_price]
        filtered_data = filtered_data.sort_values(by='price')

    return filtered_data

filtered_data = filter_data(data)

def grid_layout(filtered_data):
    st.header("🏪 Welcome to our Marketplace")
    st.write(f"There are {len(filtered_data)} products listed")

    data_length = len(filtered_data)
    total_column = st.number_input("Display Columns",value=4,step=1)

    columns = st.columns(total_column)

    for i in range(data_length):
        for r in range(total_column):
            if i%total_column == r:
                column = columns[r]
                with st.container():
                    with column:
                        with st.container(border=True):
                            product_picture = filtered_data.iloc[i]['picture']
                            product_name = filtered_data.iloc[i]['product']
                            product_description = filtered_data.iloc[i]['description']
                            product_store = filtered_data.iloc[i]['store']
                            product_price = filtered_data.iloc[i]['price']
    
                            st.image(product_picture)
                            st.write(product_name)
                            st.write(product_description)
                            st.write(product_store)
                            st.write(product_price)
    
                            if st.button("🛒Cart",key=f'cart{i}'):
                                st.write("Added to Cart")
                            if st.button("💲Buy",key=f'buy{i}'):
                                st.write("Thank you")

grid_layout(filtered_data)

