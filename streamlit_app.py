import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write title and intro text
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Add customer name text input box
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake in Streamlit Community Cloud (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# Pull fruit options from Snowflake table, including SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark Dataframe to Pandas Dataframe so we can use .loc
pd_df = my_dataframe.to_pandas()

# Add multiselect widget with maximum selection limit of 5
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# IF block: runs when ingredients_list is NOT empty
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Find the SEARCH_ON value corresponding to fruit_chosen
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Call API using the search_on variable dynamically
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Build SQL Insert Statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # Add Submit Order button
    time_to_insert = st.button('Submit Order')

    # Execute insert ONLY when the Submit Order button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
