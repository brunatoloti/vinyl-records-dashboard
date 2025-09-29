import streamlit as st

from src.db import get_wishlist

df = get_wishlist()

st.title('Lista de desejos')
st.divider()

cols_per_row = 4
for i in range(0, len(df), cols_per_row):
    cols = st.columns(cols_per_row)
    for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):
        with col:
            st.image(row["image_cover"], use_container_width=True)
            st.html(
                f"<a href={row['link']} target='_blank' style='text-decoration:none; color:#272942; font-weight:bold;'>{row['name']}</a>"
            )
            st.caption(f"{row['artist']} • {int(row['release_year'])} • {int(row['duration'])} min")