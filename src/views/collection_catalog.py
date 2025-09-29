import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.db import get_collection_catalog

df = get_collection_catalog()

st.title('Coleção de discos')

tab1, tab2 = st.tabs(["💿 Catálogo", "📈 Métricas"])

with tab1:
    cols_per_row = 4
    for i in range(0, len(df), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):
            with col:
                st.image(row["image_cover"], use_container_width=True)
                st.markdown(f"**{row['name']}**")
                st.caption(f"{row['artist']} • {int(row['release_year'])} • {int(row['duration'])} min")
with tab2:
    col_indicator = st.columns(5)
    with col_indicator[0]:
        st.metric(label='📀 Quantidade de discos', value=df.shape[0])
    with col_indicator[1]:
        st.metric(label='🧑‍🎤 Quantidade de músicos/bandas', value=df.drop_duplicates(subset=['artist']).shape[0])
    with col_indicator[2]:
        st.metric(label='🗓️ Mediana do ano de lançamento', value=int(df.release_year.median()))
    with col_indicator[3]:
        st.metric(label='⭐ Quantidade de discos usados', value=int(df.used.sum()))
    with col_indicator[4]:
        st.metric(label='🎁 Quantidade de presentes', value=int(df.gift.sum()))
        

