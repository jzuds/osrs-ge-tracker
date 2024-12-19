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

def convert_ms_to_datetime(ms):
     """Converts milliseconds since 1 January 1970 to a datetime object."""
     seconds = ms / 1000.0
     return datetime.fromtimestamp(seconds)

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

investment_list = get_my_investment_data()

event = st.dataframe(
    investment_list,
    on_select='rerun',
    selection_mode='single-row'
)

def render_item_info(item_id):
    item_info = get_ge_basic_info(item_id)
    item_name = item_info["item"]["name"]
    item_icon = item_info["item"]["icon_large"]

    img_column, mid, title_column = st.columns([5,1,20])
    with img_column:
        st.image(item_icon)
    with title_column:
        st.title(item_name)

    st.line_chart(get_ge_historic_info(item_id), x="date", y="price")

if len(event.selection['rows']):
    selected_row = event.selection['rows'][0]
    item_id_selected = investment_list.iloc[selected_row]['item_id']
    render_item_info(item_id_selected)
