from datetime import datetime
import pandas as pd
import streamlit as st

from src.db import get_collection_catalog, get_wishlist, insert_record_in_collection_and_remove_from_wishlist, insert_record_in_wishlist, get_all_countries


collection_catalog = get_collection_catalog()
wishlist = get_wishlist()
countries_options = list(get_all_countries()['value'].unique())
col1, col2 = st.columns([1, 1])

with col1:
    with st.expander('Adicionar vinil na coleção'):
        boolean_options = ['Sim', 'Não']
        purchase_type_options = ['Site', 'Feira']
        new_record_is_in_wishlist = st.radio('É um disco presente na lista de desejos?', ['Não', 'Sim'], horizontal=True)
        record_name_value, artist_name_value, country_value, image_cover_value, duration_value, qt_lps_value, release_year_value, compilation_value = None, None, None, None, None, None, None, None 
        show_form = False
        if new_record_is_in_wishlist == 'Sim':
            record_name_value = st.selectbox('Qual o disco?', options=list(wishlist['name']), index=None, placeholder='Escolha uma opção')
            if record_name_value:
                artist_name_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['artist']
                country_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['country']
                image_cover_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['image_cover']
                duration_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['duration']
                qt_lps_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['qt_lps']
                release_year_value = wishlist[wishlist['name'] == record_name_value].iloc[0]['release_year']
                compilation_value = 'Sim' if wishlist[wishlist['name'] == record_name_value].iloc[0]['compilation'] else 'Não'
                show_form = True
        else:
            show_form = True
        if show_form:
            with st.form(key='new_vinyl_in_collection'):
                record_name = st.text_input(label='Nome do álbum', value=record_name_value)
                artist_name = st.text_input(label='Nome do artista ou banda', value=artist_name_value)
                if new_record_is_in_wishlist == 'Não':
                    country = st.selectbox('País', options=countries_options, index=None, placeholder='Escolha uma opção')
                    compilation = st.selectbox('O disco é uma coletânea?', options=boolean_options, index=None, placeholder='Escolha uma opção')
                else:
                    country = st.text_input(label='País', value=country_value)
                    compilation = st.text_input('O disco é uma coletânea?', value=compilation_value)
                image_cover = st.text_input(label='Link da imagem da capa', value=image_cover_value)
                duration = st.text_input(label='Duração', value=duration_value)
                qt_lps = st.text_input(label='Quantidade de LPs', value=qt_lps_value)
                release_year = st.text_input(label='Ano de lançamento', value=release_year_value)
                used = st.selectbox('O disco é usado?', options=boolean_options, index=None, placeholder='Escolha uma opção')
                heritage = st.selectbox('O disco é herança?', options=boolean_options, index=None, placeholder='Escolha uma opção')
                gift = st.selectbox('O disco foi presente?', options=boolean_options, index=None, placeholder='Escolha uma opção')
                if gift == 'Sim':
                    gift_person = st.text_input(label='Foi dado por quem?')
                else:
                    gift_person = ''
                shopping_store = st.text_input(label='Loja da compra')
                purchase_type = st.selectbox('Tipo de compra', options=purchase_type_options, index=None, placeholder='Escolha uma opção')

                submit_button = st.form_submit_button(label='Salvar')

                if submit_button:
                    new_record_collection = pd.DataFrame(
                        [
                            {
                                'name': record_name,
                                'artist': artist_name,
                                'country': country,
                                'image_cover': image_cover,
                                'duration': duration,
                                'qt_lps': qt_lps,
                                'release_year': release_year,
                                'entry_date': datetime.today().strftime('%d/%m/%Y'),
                                'used': True if used == 'Sim' else False,
                                'heritage': True if heritage == 'Sim' else False,
                                'gift': True if gift == 'Sim' else False,
                                'gift_person': gift_person,
                                'compilation': True if compilation == 'Sim' else False,
                                'shopping_store': shopping_store,
                                'purchase_type': purchase_type
                            }
                        ]
                    )

                    update_collection_catalog = pd.concat([collection_catalog, new_record_collection], ignore_index=True)

                    insert_record_in_collection_and_remove_from_wishlist(update_collection_catalog, wishlist.query(f"name != '{record_name}'"))
                    st.success('Novo vinil na coleção')

with col2:
    with st.expander('Adicionar vinil na lista de desejos'):
        boolean_options = ['Sim', 'Não']
        purchase_type_options = ['Site', 'Feira']

        with st.form(key='new_vinyl_in_wishlist'):
            record_name = st.text_input(label='Nome do álbum')
            artist_name = st.text_input(label='Nome do artista ou banda')
            country = st.selectbox('País', options=countries_options, index=None, placeholder='Escolha uma opção')
            image_cover = st.text_input(label='Link da imagem da capa')
            duration = st.text_input(label='Duração')
            qt_lps = st.text_input(label='Quantidade de LPs')
            release_year = st.text_input(label='Ano de lançamento')
            compilation = st.selectbox('O disco é uma coletânea?', options=boolean_options, index=None, placeholder='Escolha uma opção')
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
                            'compilation': True if compilation == 'Sim' else False,
                            'link': link
                        }
                    ]
                )
                
                update_collection_catalog = pd.concat([wishlist, new_record_wishlist], ignore_index=True)

                insert_record_in_wishlist(update_collection_catalog)
                st.success('Novo vinil na coleção')
