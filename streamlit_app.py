import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import datetime

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    layout='centered',
    page_title='OSRS Grand Exchange Tracker',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# Set the title that appears at the top of the page.
'''
# :earth_americas: OSRS Grand Exchange Tracker

# Browse GE data from the [OSRS Grand Exchange Data](https://secure.runescape.com/m=itemdb_oldschool/) website.
# '''

@st.cache_data
def get_my_investment_data():
    DATA_FILENAME = Path(__file__).parent/'data/osrs_investments.json'
    df = pd.read_json(DATA_FILENAME)
    return df

def get_ge_basic_info(id:int):
    resp = requests.get(f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={id}")
    return resp.json()

def get_ge_historic_info(id:int):
    resp = requests.get(f"https://secure.runescape.com/m=itemdb_oldschool/api/graph/{id}.json")
    df = pd.DataFrame(resp.json()["daily"].items(), columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')

    return df

def render_item_info(item_id: int, calc_profit_item_amount, calc_profit_item_price):
    item_info = get_ge_basic_info(item_id)
    item_name = item_info["item"]["name"]
    item_icon = item_info["item"]["icon_large"]
    item_30d_percent_change_price = item_info["item"]["day30"]["change"]
    df_item_historic_pricing = get_ge_historic_info(item_id)
    current_price = df_item_historic_pricing.iloc[-1]["price"]

    img_column, mid, title_column = st.columns([5,1,20])
    with img_column:
        st.image(item_icon)
    with title_column:
        st.title(item_name)

    kpi_1, mid, kpi_2 = st.columns([5,1,20])
    with kpi_1:
        st.metric(label='current price', value=current_price, delta=item_30d_percent_change_price)
    
    if calc_profit_item_amount > 0:
        with kpi_2:
            st.metric(label='calculated profit', value=int(current_price - calc_profit_item_price) * calc_profit_item_amount, delta=int(current_price - calc_profit_item_price))

    st.line_chart(df_item_historic_pricing, x="date", y="price")

# Main
investment_list = get_my_investment_data()

event = st.dataframe(
    investment_list,
    on_select='rerun',
    selection_mode='single-row'
)

if len(event.selection['rows']):
    selected_row = event.selection['rows'][0]
    item_id_selected = investment_list.iloc[selected_row]['item_id']
    calc_profit_item_amount = 0
    calc_profit_item_price = 0

    if investment_list.iloc[selected_row]['ge_type'] == 'purchase':
        calc_profit_item_amount = investment_list.iloc[selected_row]['amount']
        calc_profit_item_price = investment_list.iloc[selected_row]['price']
    
    render_item_info(item_id_selected, calc_profit_item_amount, calc_profit_item_price)
