import streamlit as st
import pandas as pd

st.title("Cashier")
data = pd.read_excel('./pages/dataset_cashier.xlsx')

if 'transaction' not in st.session_state:
    st.session_state['transaction'] = pd.DataFrame(columns=['description', 'price', 'quantity', 'amount'])

cashier_col1, cashier_col2, cashier_col3 = st.columns(3)

with cashier_col1:
    with st.container(border=True,height=450):
        input_product = st.number_input("Product Code", step=1, value=0)
        preview_data = data[data['product_id'] == input_product][['description', 'price']]

        st.write('Product Information')
        st.dataframe(preview_data,use_container_width=True,hide_index=True)

        input_quantity = st.number_input("Quantity", step=1, value=0)

        if st.button("Add"):
            if not preview_data.empty and input_quantity > 0:
                description = preview_data['description'].values[0]
                price = preview_data['price'].values[0]
                
                existing_item = st.session_state['transaction']['description'] == description

                if existing_item.any():
                    index = st.session_state['transaction'][existing_item].index[0]
                    st.session_state['transaction'].at[index, 'quantity'] += input_quantity
                    st.session_state['transaction'].at[index, 'amount'] = (st.session_state['transaction'].at[index, 'quantity'] * price)
                else:
                    cart = pd.DataFrame({
                        'description': [description],
                        'price': [price],
                        'quantity': [input_quantity],
                        'amount': [price * input_quantity]
                    })
                    st.session_state['transaction'] = pd.concat([st.session_state['transaction'], cart], ignore_index=True)
            else:
                st.warning("Invalid input")
with cashier_col2:
    with st.container(height=450, border=True):
        st.write('Cart')
        st.dataframe(st.session_state['transaction'],hide_index=True,use_container_width=True)
with cashier_col3:
    with st.container(border=True):
        total_amount = st.session_state['transaction']['amount'].sum()
        st.write("Total Amount")
        st.subheader(f"**${total_amount:.2f}**")
    with st.container(height=320,border=True):
        payment_input = st.number_input("Payment:",step=1)
        if st.button("Pay"):
            if payment_input >= total_amount:
                return_amount = payment_input - total_amount
                receipt = "----- Receipt -----\n"
                receipt += "Items Purchased:\n"
                for idx, row in st.session_state['transaction'].iterrows():
                    receipt += f"- {row['quantity']}x {row['description']} (${row['amount']:.2f})\n"
                    
                receipt += f"\nTotal: ${total_amount:.2f}\n"
                receipt += f"Payment: ${payment_input:.2f}\n"
                receipt += f"Return: ${return_amount:.2f}\n"
                receipt += "-------------------"

                st.text(receipt)
            else:
                st.error("Insufficient payment")
        if st.button("Clear"):
            st.session_state['transaction'] = pd.DataFrame(columns=['description', 'price', 'quantity', 'amount'])
            st.success("Transaction cleared")
