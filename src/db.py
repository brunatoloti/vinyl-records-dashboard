import streamlit as st
from streamlit_gsheets import GSheetsConnection


def get_all_users():
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM users;')
    return result

def get_collection_catalog():
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM collection_catalog;')
    result = result.astype(dtype={'duration': int, 'qt_lps': int,
                                  'release_year': int, 'compilation': bool})
    return result

def get_wishlist():
    conn = st.connection('gsheets', type=GSheetsConnection)
    result = conn.query('SELECT * FROM wishlist;')
    result = result.astype(dtype={'duration': int, 'qt_lps': int,
                                  'release_year': int, 'compilation': bool})
    return result

def insert_record_in_collection_and_remove_from_wishlist(new_collection, remove_wishlist):
    conn = st.connection('gsheets', type=GSheetsConnection)
    conn.update(worksheet='collection_catalog', data=new_collection)
    conn.update(worksheet='wishlist', data=remove_wishlist)
    st.cache_data.clear()
    st.rerun()

def insert_record_in_wishlist(updated_df):
    conn = st.connection('gsheets', type=GSheetsConnection)
    conn.update(worksheet='wishlist', data=updated_df)
    st.cache_data.clear()
    st.rerun()

def get_all_countries():
    conn = st.connection('gsheets', type=GSheetsConnection)
    country = conn.read(worksheet='country', usecols=list(range(2))).dropna()
    return country