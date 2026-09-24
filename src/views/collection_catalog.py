from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from plotly_calplot import calplot
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from wordcloud import WordCloud

from src.db import get_collection_catalog, get_all_countries, get_wishlist, insert_record_in_collection_and_remove_from_wishlist
from src.utils import VinylRecordsDashUtilities


def search_release_groups_catalog(artist_name):
    normalized_artist = artist_name.strip().casefold()
    cached_result = st.session_state.release_groups_cache.get(normalized_artist)

    if cached_result is not None:
        return cached_result

    result = VinylRecordsDashUtilities({"artist_name": normalized_artist}).get_release_group()
    st.session_state.release_groups_cache[normalized_artist] = result
    return result


@st.cache_data(ttl=3600, show_spinner=False)
def search_album_details_catalog(artist_name, release_group_id):
    data = {
        "artist_name": artist_name,
        "release_group_id": release_group_id
    }
    return VinylRecordsDashUtilities(data).get_album_details()

df = get_collection_catalog()
df['year'] = df['entry_date'].apply(lambda x: x.split('/')[-1])

df_bruna = df[df['heritage'] == 0]
df_heritage = df[df['heritage'] == 1]

st.title('Coleção de discos')

tab1, tab2, tab3 = st.tabs(["💿 Catálogo", "📈 Métricas", "➕ Adicionar novo disco"])

def vinyl_display(df):
    cols_per_row = 4
    for i in range(0, len(df), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, (_, row) in zip(cols, df.iloc[i:i+cols_per_row].iterrows()):
            with col:
                st.image(row["image_cover"], width='stretch')
                st.markdown(f"**{row['name']}**")
                st.caption(f"{row['artist']} • {int(row['release_year'])} • {int(row['duration'])} min")

with tab1:
    vinyl_display(df_bruna)
    st.divider()
    st.subheader('Discos herdados do meu pai 🖤')
    vinyl_display(df_heritage)

with tab2:
    heritage_sel = st.session_state.get('heritage', [])
    musician_sel = st.session_state.get('musician', [])
    publication_year_sel = st.session_state.get('publication_year', [])
    purchase_year_sel = st.session_state.get('purchase_year', [])

    df['heritage_str'] = df['heritage'].apply(lambda x: 'Sim' if str(x) == '1.0' else 'Não')
    
    df_heritage_metric = df.copy()
    if musician_sel:
        df_heritage_metric = df_heritage_metric[df_heritage_metric['artist'].isin(musician_sel)]
    if publication_year_sel:
        df_heritage_metric = df_heritage_metric[df_heritage_metric['release_year'].isin(publication_year_sel)]
    if purchase_year_sel:
        df_heritage_metric = df_heritage_metric[df_heritage_metric['year'].isin(purchase_year_sel)]
    heritage_options = sorted(df_heritage_metric['heritage_str'].unique())

    df_musician_metric = df.copy()
    if heritage_sel:
        df_musician_metric = df_musician_metric[df_musician_metric['heritage_str'].isin(heritage_sel)]
    if publication_year_sel:
        df_musician_metric = df_musician_metric[df_musician_metric['release_year'].isin(publication_year_sel)]
    if purchase_year_sel:
        df_musician_metric = df_musician_metric[df_musician_metric['year'].isin(purchase_year_sel)]
    musician_options = sorted(df_musician_metric['artist'].unique())

    df_publication_year_metric = df.copy()
    if musician_sel:
        df_publication_year_metric = df_publication_year_metric[df_publication_year_metric['artist'].isin(musician_sel)]
    if heritage_sel:
        df_publication_year_metric = df_publication_year_metric[df_publication_year_metric['heritage_str'].isin(heritage_sel)]
    if purchase_year_sel:
        df_publication_year_metric = df_publication_year_metric[df_publication_year_metric['year'].isin(purchase_year_sel)]
    publication_year_options = sorted(df_publication_year_metric['release_year'].unique())

    df_purchase_year_metric = df.copy()
    if musician_sel:
        df_purchase_year_metric = df_purchase_year_metric[df_purchase_year_metric['artist'].isin(musician_sel)]
    if publication_year_sel:
        df_purchase_year_metric = df_purchase_year_metric[df_purchase_year_metric['release_year'].isin(publication_year_sel)]
    if heritage_sel:
        df_purchase_year_metric = df_purchase_year_metric[df_purchase_year_metric['heritage_str'].isin(heritage_sel)]
    purchase_year_options = sorted(df_purchase_year_metric['year'].unique())

    filters = st.columns(4)
    with filters[0]:
        heritage_sel = st.multiselect(
            'Herdados', 
            heritage_options,
            default=heritage_sel,
            key='heritage',
            placeholder='Todos'
        )
    with filters[1]:
        musician_sel = st.multiselect(
            'Músicos/banda',
            musician_options,
            default=musician_sel,
            key='musician',
            placeholder='Todos'
        )
    with filters[2]:
        publication_year_sel = st.multiselect(
            'Ano de lançamento',
            publication_year_options,
            default=publication_year_sel,
            key='publication_year',
            placeholder='Todos'
        )
    with filters[3]:
        purchase_year_sel = st.multiselect(
            'Ano que entrou na coleção',
            purchase_year_options,
            default=purchase_year_sel,
            key='purchase_year',
            placeholder='Todos'
        )

    result = df.copy()

    if heritage_sel:
        result = result[result['heritage_str'].isin(heritage_sel)]
    if musician_sel:
        result = result[result['artist'].isin(musician_sel)]
    if publication_year_sel:
        result = result[result['release_year'].isin(publication_year_sel)]
    if purchase_year_sel:
        result = result[result['year'].isin(purchase_year_sel)]

    col_indicator = st.columns(5)
    with col_indicator[0]:
        st.metric(label='📀 Quantidade de discos', value=result.shape[0])
    with col_indicator[1]:
        st.metric(label='🧑‍🎤 Quantidade de músicos/bandas', value=result.drop_duplicates(subset=['artist']).shape[0])
    with col_indicator[2]:
        st.metric(label='🖤 Quantidade de discos herdados', value=int(result.heritage.sum()))
    with col_indicator[3]:
        st.metric(label='⭐ Quantidade de discos usados', value=int(result.used.sum()))
    with col_indicator[4]:
        st.metric(label='🎁 Quantidade de presentes', value=int(result.gift.sum()))

    col1, col2 = st.columns([1, 1])

    with col1:
        # chart of number of records by country
        records_by_country = result.groupby('country')['name'].count().reset_index()
        records_by_country = records_by_country.merge(get_all_countries(), left_on='country', right_on='value').drop(columns=['value'])
        records_by_country = records_by_country.rename(columns={'id': 'IdISO3166'})
        chart1 = px.scatter_geo(records_by_country, locations='IdISO3166',
                            hover_name='country', size='name', color_discrete_sequence=['#FF4B4B'], custom_data=['name', 'country'])
        chart1.update_traces(
            hovertemplate =
                        "<b>%{customdata[1]}</b><br>" +
                        "Quantidade: %{customdata[0]}<br>" +
                        "<extra></extra>",
        )
        chart1.update_layout(
            title_text = f'Quantidade de discos por país',
            geo=dict(
                projection_type='equirectangular')
        )
        chart1.update_geos(
            showcoastlines=True, coastlinecolor="black",
            showland=True, landcolor="beige",
            showcountries=True, countrycolor="black",
            showocean=True, oceancolor="LightBlue"
        )
        st.plotly_chart(chart1)
    
    with col2:
        st.write('')
        st.markdown("""
            <h6 style='text-align: left; color: #272942; font-weight: bold;'>
            Músicos/Bandas
            </h6>
        """, unsafe_allow_html=True)
        st.write('')
        counting = result['artist'].value_counts().to_dict()

        wc = WordCloud(width=800, height=400, background_color="#cfd0daff", colormap="Reds")
        wc.generate_from_frequencies(counting)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        


    records_by_year = result.groupby('year')['name'].count().reset_index()
    records_by_year['year'] = records_by_year['year'].apply(lambda x: str(int(x)))
    chart2 = px.line(records_by_year, x='year', y='name', 
                    title=f'Quantidade de discos que entraram na coleção por ano', color_discrete_sequence=["#FF4B4B"], text='name')
    chart2.update_traces(
        hovertemplate =
                    "<b>%{x}</b><br>" +
                    "Quantidade: %{y}<br>" +
                    "<extra></extra>",
        textfont_color='#272942',
        textposition='top center'
    )
    chart2.update_layout(
        xaxis=dict(
            type='category',
            categoryorder='array',
            categoryarray=sorted(records_by_year['year'].unique())
        )
    )
    chart2.update_yaxes(title_text='')
    chart2.update_xaxes(title_text='')
    st.plotly_chart(chart2)

    counting = result.groupby('release_year').agg(
            records = ('name', lambda x: '<br>'.join(sorted(x))),
            count = ('name', 'count')
        ).reset_index()
    chart8 = px.scatter(
        counting,
        x="release_year",
        y="count",
        title="Quantidade de discos por ano de lançamento",
        labels={"release_year": "Ano de Lançamento", "count": "Quantidade"},
        hover_data={"records": True, "release_year": True, "count": True},
    )

    chart8.update_traces(
        textposition="top center", marker=dict(size=12, color="#FF4B4B"),
        hovertemplate="<b>Ano %{x}</b><br><b>Quantidade:</b> %{y}<br><b>Discos:</b> <br>%{customdata[0]}<extra></extra>"
        )
    chart8.update_layout(
        xaxis=dict(dtick=1),
        template="plotly_white",
        title_font_size=20,
    )
    chart8.update_yaxes(title_text='')
    chart8.update_xaxes(title_text='')
    st.plotly_chart(chart8)

    col1, col2 = st.columns([1, 1])

    with col1:
        count_gift_person = result.groupby('gift_person')['name'].count().reset_index()
        count_gift_person = count_gift_person.sort_values('name', ascending=False).head()
        chart4 = px.bar(count_gift_person, x='name', y="gift_person", orientation='h',
                    height=400,
                    title='Quantidade de discos dados de presente por pessoa', color_discrete_sequence=["#FF4B4B"],
                    text='name')
        chart4.update_traces(
            hovertemplate =
                        "<b>%{y}</b><br>" +
                        "Quantidade: %{x}<br>" +
                        "<extra></extra>",
            textfont_color='#d6d7dd'
        )
        chart4.update_layout(
            yaxis=dict(autorange="reversed")
        )
        chart4.update_yaxes(title_text='')
        chart4.update_xaxes(title_text='')
        st.plotly_chart(chart4)

        count_finished_books_by_new_reading = result['purchase_type'].value_counts().reset_index()
        count_finished_books_by_new_reading.columns = ['purchase_type', 'Qtd']
        chart7 = px.bar(count_finished_books_by_new_reading, x='purchase_type', y="Qtd", orientation='v',
                        height=400,
                        title='Quantidade de discos por tipo de compra', color_discrete_sequence=["#CF7C7C"],
                        text='Qtd')
        chart7.update_traces(
            hovertemplate =
                        "<b>%{x}</b><br>" +
                        "Quantidade: %{y}<br>" +
                        "<extra></extra>",
            textfont_color='#d6d7dd'
        )
        chart7.update_yaxes(title_text='')
        chart7.update_xaxes(title_text='')
        st.plotly_chart(chart7)

    with col2:
        chart5 = px.histogram(
            result,
            x='duration',
            title='Distribuição da duração dos álbuns',
            color_discrete_sequence=["#CF7C7C"]
        )
        chart5.update_xaxes(title_text='Duração')
        chart5.update_yaxes(title_text='')
        st.plotly_chart(chart5)


        count_shopping_store = result.groupby('shopping_store')['name'].count().reset_index()
        count_shopping_store = count_shopping_store.sort_values('name', ascending=False).head()
        chart6 = px.bar(count_shopping_store, x='name', y="shopping_store", orientation='h',
                    height=400,
                    title='Quantidade de discos por loja', color_discrete_sequence=["#FF4B4B"],
                    text='name')
        chart6.update_traces(
            hovertemplate =
                        "<b>%{y}</b><br>" +
                        "Quantidade: %{x}<br>" +
                        "<extra></extra>",
            textfont_color='#d6d7dd'
        )
        chart6.update_layout(
            yaxis=dict(autorange="reversed")
        )
        chart6.update_yaxes(title_text='')
        chart6.update_xaxes(title_text='')
        st.plotly_chart(chart6)

    entry_by_date = result[["name", "entry_date"]].copy()
    entry_by_date["entry_date"] = pd.to_datetime(entry_by_date["entry_date"], format="%d/%m/%Y", errors="coerce")
    entry_by_date = entry_by_date.dropna(subset=["entry_date"])
    entry_by_date = (
        entry_by_date
        .groupby("entry_date")
        .agg(
            records=(
                "name",
                lambda values: "<br>".join(
                    f"• {record}"
                    for record in sorted(
                        values.dropna().astype(str)
                    )
                ),
            ),
            QtDiscos=("name", "count"),
        )
        .reset_index()
    )

    start_date = pd.Timestamp(year=entry_by_date["entry_date"].min().year, month=1, day=1)
    end_date = pd.Timestamp.today().normalize()
    entry_by_date = (
        entry_by_date
        .set_index("entry_date")
        .reindex(
            pd.date_range(
                start=start_date,
                end=end_date,
                freq="D",
            )
        )
        .rename_axis("entry_date")
        .reset_index()
    )

    entry_by_date["QtDiscos"] = entry_by_date["QtDiscos"].fillna(0).astype(int)
    entry_by_date["records"] = entry_by_date["records"].fillna("Nenhum disco")
    entry_by_date["year"] = entry_by_date["entry_date"].dt.year
    entry_by_date["entry_date"] = entry_by_date["entry_date"].to_numpy(dtype="datetime64[ns]")
    chart9 = calplot(
        entry_by_date.copy(),
        x="entry_date",
        y="QtDiscos",
        text="records",
        cmap_min=0,
        cmap_max=5,
        name="Quantidade",
        colorscale="reds",
    )

    for trace in chart9.data:
        if trace.type == "heatmap":
            trace.hovertemplate = (
                "<b>Data:</b> %{customdata[0]}<br>"
                "<b>Quantidade:</b> %{z}<br>"
                "<b>Discos:</b><br>%{text}"
                "<extra></extra>"
            )

    dd = {"title": {"text": "Histórico de aquisição de discos"}}

    years_df = result.sort_values("year")["year"].astype(int).unique()
    all_years = range(min(years_df), max(years_df) + 1)

    for j, year in enumerate(all_years, start=1):
        dd.update({
            f"yaxis{j}": {
                "title": str(year),
                "ticktext": [
                    "Seg", "Ter", "Qua", "Qui",
                    "Sex", "Sab", "Dom",
                ],
            },
            f"xaxis{j}": {
                "ticktext": [
                    "Janeiro", "Fevereiro", "Março",
                    "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro",
                    "Outubro", "Novembro", "Dezembro",
                ],
            },
        })

    chart9.update_layout(dd)
    st.plotly_chart(chart9)

with tab3:
    if st.session_state.username == 'brunat':
        collection_catalog = get_collection_catalog()
        wishlist = get_wishlist()
        countries_options = list(get_all_countries()['value'].unique())
        boolean_options = ['Sim', 'Não']
        purchase_type_options = ['Site', 'Feira', 'Loja física']
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
            if new_record_is_in_wishlist == 'Não':
                artist_name = st.text_input(label='Nome do artista ou banda')
                show_records = False
                show_form = False
                if artist_name:
                    search_release_group = search_release_groups_catalog(artist_name)
                    record_name_value = [t['title'] for t in search_release_group]
                    if record_name_value != ['None'] and record_name_value != [None]:
                        record_name = st.selectbox(label='Nome do álbum', options=record_name_value, index=None, accept_new_options=True)
                        if record_name != 'None' and record_name != None:
                            record_infos1 = [ri for ri in search_release_group if ri['title'] == record_name][0]
                            record_infos2 = search_album_details_catalog(artist_name, record_infos1["id"])
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
                with st.form(key='new_vinyl_in_collection'):
                    if new_record_is_in_wishlist == 'Não' and tt:
                        record_name = st.text_input(label='Nome do álbum')
                    duration = st.text_input(label='Duração', value=duration_value)
                    qt_lps = st.text_input(label='Quantidade de LPs', value=qt_lps_value)
                    release_year = st.text_input(label='Ano de lançamento', value=release_year_value)
                    image_cover = st.text_input(label='Link da imagem da capa', value=image_cover_value)
                    if new_record_is_in_wishlist == 'Não':
                        country = st.selectbox('País', options=countries_options, index=None, placeholder='Escolha uma opção')
                        compilation = st.selectbox('O disco é uma coletânea?', options=boolean_options, index=None, placeholder='Escolha uma opção')
                    else:
                        country = st.text_input(label='País', value=country_value)
                        compilation = st.text_input('O disco é uma coletânea?', value=compilation_value)
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
                                    'compilation': compilation,
                                    'shopping_store': shopping_store,
                                    'purchase_type': purchase_type
                                }
                            ]
                        )

                        update_collection_catalog = pd.concat([collection_catalog, new_record_collection], ignore_index=True)

                        insert_record_in_collection_and_remove_from_wishlist(update_collection_catalog, wishlist.query(f"name != '{record_name}'"))
                        st.success('Novo vinil na coleção')
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