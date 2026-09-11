import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.db import get_wishlist, get_all_countries, insert_record_in_wishlist
from src.utils import VinylRecordsDashUtilities


def search_release_groups(artist_name):
    normalized_artist = artist_name.strip().casefold()
    cached_result = st.session_state.release_groups_cache.get(normalized_artist)

    if cached_result is not None:
        return cached_result

    result = VinylRecordsDashUtilities({"artist_name": normalized_artist}).get_release_group()
    st.session_state.release_groups_cache[normalized_artist] = result
    return result


@st.cache_data(ttl=3600, show_spinner=False)
def search_album_details(artist_name, release_group_id):
    data = {
        "artist_name": artist_name,
        "release_group_id": release_group_id
    }
    return VinylRecordsDashUtilities(data).get_album_details()

df = get_wishlist()

st.title('Lista de desejos')

tab1, tab2 = st.tabs(['💿 Desejados', '➕ Adicionar novo disco'])

with tab1:
    cols_per_row = 4
    for i in range(0, len(df), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):
            with col:
                st.image(row["image_cover"], width='stretch')
                st.html(
                    f"<a href={row['link']} target='_blank' style='text-decoration:none; color:#272942; font-weight:bold;'>{row['name']}</a>"
                )
                st.caption(f"{row['artist']} • {int(row['release_year'])} • {int(row['duration'])} min")

with tab2:
    if st.session_state.username == 'brunat':
        wishlist = get_wishlist()
        countries_options = list(get_all_countries()['value'].unique())
        boolean_options = ['Sim', 'Não']
        record_name_value = None
        image_cover_value = None
        duration_value = None
        qt_lps_value = None
        release_year_value = None
        compilation_value = None

        artist_name = st.text_input(label='Nome do artista ou banda')
        show_records = False
        show_form = False
        if artist_name:
            search_release_group = search_release_groups(artist_name)
            record_name_value = [t['title'] for t in search_release_group]
            if record_name_value != ['None'] and record_name_value != [None]:
                record_name = st.selectbox(label='Nome do álbum', options=record_name_value, index=None, accept_new_options=True)
                if record_name != 'None' and record_name != None:
                    record_infos1 = [ri for ri in search_release_group if ri['title'] == record_name][0]
                    record_infos2 = search_album_details(artist_name, record_infos1["id"])
                    record_details = record_infos1 | record_infos2
                    if record_details['duration']:
                        duration_value = record_details['duration'].split(':')[0]
                    qt_lps_value = record_details['discs_quantity']
                    release_year_value = record_details['release_date']
                    compilation_value = 'Sim' if 'Compilation' in record_details['secondary_types'] else 'Não'
                    image_cover_value = record_details['image_cover']
                    show_form = True
                    tt = False
            else:
                show_form = True
                tt = True
            if show_form:
                with st.form(key='new_vinyl_in_wishlist'):
                    if tt:
                        record_name = st.text_input(label='Nome do álbum')
                    duration = st.text_input(label='Duração', value=duration_value)
                    qt_lps = st.text_input(label='Quantidade de LPs', value=qt_lps_value)
                    release_year = st.text_input(label='Ano de lançamento', value=release_year_value)
                    compilation = st.text_input('O disco é uma coletânea?', value=compilation_value)
                    image_cover = st.text_input(label='Link da imagem da capa', value=image_cover_value)
                    country = st.selectbox('País', options=countries_options, index=None, placeholder='Escolha uma opção')
                    link = st.text_input('Link')

                    submit_button = st.form_submit_button(label='Salvar')

                    if submit_button:
                        new_record_wishlist = pd.DataFrame(
                            [
                                {
                                    'name': record_name,
                                    'artist': artist_name,
                                    'country': country,
                                    'image_cover': image_cover,
                                    'duration': duration,
                                    'qt_lps': qt_lps,
                                    'release_year': release_year,
                                    'compilation': compilation,
                                    'link': link
                                }
                            ]
                        )
                        st.dataframe(new_record_wishlist)
                        
                        update_collection_catalog = pd.concat([wishlist, new_record_wishlist], ignore_index=True)

                        insert_record_in_wishlist(update_collection_catalog)
                        st.success('Novo vinil na lista de desejos')
    else:
        st.info('Você não tem acesso a essa página')
        components.html(
            """
            <div style="display: flex; justify-content: center;">
                <iframe
                    src="https://giphy.com/embed/RJadE8FkETsptbI8O8"
                    style="width: 100%; max-width: 480px; aspect-ratio: 480/269;"
                    frameborder="0"
                    allowfullscreen>
                </iframe>
            </div>
            """,
            height=280,
            scrolling=False
        )