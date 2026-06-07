import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.dashboard.queries import (
    get_countries,
    get_top_artists_by_playlist,
    get_top_artists_by_listeners,
    get_tracks_by_country,
    get_top_genres,
    get_listeners_vs_playlist,
    get_releases_over_time,
    get_genre_vs_success,
)

# Configuração
st.set_page_config(
    page_title="Tendências Musicais Globais",
    page_icon="",
    layout="wide"
)

st.title("Que fatores influenciam o sucesso musical?")
st.markdown(
    "Análise baseada em dados do **Spotify Million Playlist Dataset**, "
    "**Last.fm API**, **MusicBrainz** e **Wikipedia**. "
    "O *sucesso* é medido por duas métricas complementares: "
    "**aparições em playlists** (Spotify, cobre 24 000+ artistas) "
    "e **ouvintes únicos** (Last.fm, cobre os 1 000 artistas mais populares)."
)

st.divider()

# Sidebar
st.sidebar.header(" Filtros")

countries = ["Todos"] + get_countries()
selected_country = st.sidebar.selectbox("País de lançamento", countries)
country_param = None if selected_country == "Todos" else selected_country

top_n = st.sidebar.slider("Top N artistas", min_value=5, max_value=50, value=10, step=5)

st.sidebar.divider()
st.sidebar.caption(
    "**Nota sobre os dados:** Last.fm e MusicBrainz cobrem os 1000 artistas "
    "mais populares por playlists. A coluna *playlist_appearances* cobre "
    "todos os 24 000+ artistas."
)

# Top artistas
st.header("1. Artistas mais presentes nas playlists")
st.caption("Quantas playlists do Spotify incluem cada artista — o indicador de sucesso mais abrangente do dataset.")
st.markdown(
    "**Drake lidera de forma isolada**, com 4 565 aparições — mais do dobro do segundo lugar (Kanye West, 1 959). "
    "**7 dos 10 artistas pertencem ao hip-hop** ou subvariantes, o que sugere que este género domina a curadoria de playlists no Spotify. "
    "A diferença entre o 1.º e o 10.º lugar é de ~3 300 aparições, evidenciando uma concentração de sucesso no topo."
)

df_playlist = get_top_artists_by_playlist(top_n=top_n, country=country_param)

if df_playlist.empty:
    st.info("Sem dados para este filtro.")
else:
    fig = px.bar(
        df_playlist,
        x="playlist_appearances", y="artist_name",
        orientation="h",
        color="playlist_appearances",
        color_continuous_scale="Blues",
        labels={"playlist_appearances": "Aparições em playlists", "artist_name": "Artista"},
        title=f"Top {top_n} artistas por aparições em playlists"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Géneros e sucesso
st.header("2. Que géneros musicais dominam as playlists?")
st.caption("Média de aparições em playlists e de ouvintes por género musical (mínimo 3 artistas por género).")
st.markdown(
    "Os dois gráficos revelam **dois mundos distintos de sucesso**: à esquerda, o Spotify favorece "
    "**trap rap, cloud rap e dancehall** — subgéneros recentes do hip-hop. "
    "À direita, o Last.fm é liderado por **glam rock, britpop e nu metal** — géneros com décadas de história e bases de fãs fidelizadas. "
    "O canal de distribuição favorece géneros completamente diferentes: a curadoria algorítmica de playlists e o streaming global acumulado não medem o mesmo tipo de popularidade."
)

col1, col2 = st.columns(2)

with col1:
    df_genre_playlist = get_genre_vs_success(metric="playlist_appearances")
    if not df_genre_playlist.empty:
        fig2 = px.bar(
            df_genre_playlist,
            x="media_playlist_appearances", y="genero",
            orientation="h",
            color="media_playlist_appearances",
            color_continuous_scale="Greens",
            labels={"media_playlist_appearances": "Média de aparições", "genero": "Género"},
            title="Géneros com mais aparições médias em playlists"
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    df_genre_listeners = get_genre_vs_success(metric="listeners")
    if not df_genre_listeners.empty:
        fig3 = px.bar(
            df_genre_listeners,
            x="media_listeners", y="genero",
            orientation="h",
            color="media_listeners",
            color_continuous_scale="Oranges",
            labels={"media_listeners": "Média de ouvintes", "genero": "Género"},
            title="Géneros com mais ouvintes médios (Last.fm)"
        )
        fig3.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Listeners vs Playlists
st.header("3. Popularidade no streaming vs. presença em playlists")
st.markdown(
    "Cada ponto é um artista. **Artistas no canto superior direito** são populares em ambas as dimensões — "
    "o perfil de sucesso mais completo. "
    "**Artistas com muitos ouvintes mas poucas playlists** (lado direito, baixo) são populares globalmente "
    "mas menos presentes em playlists curadas — como Coldplay ou Radiohead. "
    "**Artistas com muitas playlists mas poucos ouvintes** (lado esquerdo, alto) são fenómenos "
    "específicos do Spotify — como Drake ou Future."
)
st.markdown(
    "A correlação entre as duas métricas é **positiva mas fraca** — confirma que existem dois perfis distintos de sucesso. "
    "O ponto isolado no topo (4 500+ playlists, ~6M ouvintes) é Drake, o único artista que combina ambas as métricas em simultâneo a um nível excecional. "
    "A maioria dos artistas concentra-se na zona inferior esquerda, com valores moderados em ambas as dimensões."
)

df_scatter = get_listeners_vs_playlist(country=country_param)

if df_scatter.empty:
    st.info("Sem dados suficientes para este filtro.")
else:
    # Extrair o primeiro género de cada artista para simplificar a legenda
    df_scatter["genero_principal"] = df_scatter["tags_genres_era"].apply(
        lambda x: x.split(",")[0].strip() if pd.notna(x) else "Desconhecido"
    )
    fig4 = px.scatter(
        df_scatter,
        x="listeners", y="playlist_appearances",
        hover_name="artist_name",
        hover_data={"tags_genres_era": True, "genero_principal": False},
        color="genero_principal",
        labels={
            "listeners": "Ouvintes únicos (Last.fm)",
            "playlist_appearances": "Aparições em playlists (Spotify)",
            "genero_principal": "Género principal"
        },
        title="Ouvintes Last.fm vs. Aparições em Playlists Spotify"
    )
    fig4.update_traces(marker=dict(size=8, opacity=0.7))
    fig4.update_layout(legend=dict(
        title="Género principal",
        orientation="v",
        yanchor="top", y=1,
        xanchor="left", x=1.02,
        font=dict(size=10)
    ))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Distribuição por país
st.header("4. De onde vêm as faixas com mais dados?")
st.caption(
    "Mapa de faixas com país de lançamento identificado no MusicBrainz. "
    "Nota: 'XW' (lançamento mundial) e 'XE' (Europa) são excluídos por não corresponderem a países específicos."
)
st.markdown(
    "Os **EUA dominam com 108 faixas** identificadas — quase 5× mais do que o segundo lugar (Reino Unido, 22). "
    "Seguem-se Alemanha, Austrália e Canadá, todos países de tradição anglo-saxónica na indústria musical. "
    "Esta distribuição é **consistente com a origem do dataset** (utilizadores do Spotify USA) e reflete a dominância "
    "anglo-americana na produção musical global. A cobertura geográfica total é de apenas 0,3% das faixas — "
    "insuficiente para conclusões robustas por país."
)

df_countries = get_tracks_by_country(top_n=50)

if df_countries.empty:
    st.info("Sem dados de país disponíveis.")
else:
    # XW = "worldwide" e XE = "Europe" são códigos MusicBrainz, não países ISO
    df_map = df_countries[~df_countries["release_country"].isin(["XW", "XE"])].copy()

    # Converter ISO-2 para ISO-3 (Plotly choropleth requer ISO-3)
    ISO2_TO_ISO3 = {
        "AF": "AFG", "AL": "ALB", "AO": "AGO", "AR": "ARG", "AT": "AUT",
        "AU": "AUS", "BR": "BRA", "BS": "BHS", "CA": "CAN", "CH": "CHE",
        "DE": "DEU", "DK": "DNK", "ES": "ESP", "FR": "FRA", "GB": "GBR",
        "IT": "ITA", "JP": "JPN", "KR": "KOR", "MY": "MYS", "NL": "NLD",
        "PT": "PRT", "RU": "RUS", "SE": "SWE", "US": "USA", "ZA": "ZAF",
        "LU": "LUX",
    }
    df_map["iso3"] = df_map["release_country"].map(ISO2_TO_ISO3)
    df_map = df_map.dropna(subset=["iso3"])

    fig5 = px.choropleth(
        df_map,
        locations="iso3",
        locationmode="ISO-3",
        color="total_faixas",
        color_continuous_scale=[
            [0.0,  "#F0A0FF"],
            [0.2,  "#C84FE8"],
            [0.4,  "#9B30D0"],
            [0.6,  "#5B2D8E"],
            [0.8,  "#2D1B69"],
            [1.0,  "#0A0A2E"],
        ],
        range_color=[1, df_map["total_faixas"].max()],
        hover_name="release_country",
        hover_data={"total_faixas": True, "iso3": False},
        labels={"total_faixas": "Nº de faixas"},
        title="Faixas por país de lançamento (MusicBrainz)",
    )
    fig5.update_layout(
        paper_bgcolor="#0D0D0D",
        plot_bgcolor="#0D0D0D",
        font_color="#FFFFFF",
        coloraxis_colorbar=dict(
            title=dict(text="Nº faixas", font=dict(color="white")),
            tickfont=dict(color="white"),
        ),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor="#FFFFFF",
            showocean=True,
            oceancolor="#0D0D0D",
            showcountries=True,
            countrycolor="#000000",
            countrywidth=0.8,
            projection_type="natural earth",
            bgcolor="#0D0D0D",
        ),
        margin=dict(t=50, l=0, r=0, b=0),
        height=450,
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Ranking top 10
    st.caption("Top 10 países por número de faixas identificadas")
    fig5b = px.bar(
        df_map.sort_values("total_faixas", ascending=False).head(10),
        x="release_country", y="total_faixas",
        color="total_faixas",
        color_continuous_scale="Purples",
        labels={"release_country": "País", "total_faixas": "Nº de faixas"},
        text="total_faixas",
    )
    fig5b.update_traces(textposition="outside")
    fig5b.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#333333"),
        margin=dict(t=10, l=0, r=0, b=0),
        height=300,
    )
    st.plotly_chart(fig5b, use_container_width=True)

st.divider()

# Evolução temporal
st.header("5. Evolução dos lançamentos ao longo do tempo")
st.caption("Anos com mais lançamentos identificados no MusicBrainz.")
st.markdown(
    "Observa-se uma **tendência crescente desde 1997 até 2015**, com um pico máximo de ~35 faixas identificadas. "
    "Após 2015, nota-se uma **queda abrupta seguida de recuperação parcial**, o que pode refletir tanto o crescimento "
    "de lançamentos digitais sem registo físico no MusicBrainz, como o viés do dataset — as playlists do Spotify MPD "
    "foram criadas até 2017, limitando a representação de lançamentos posteriores. "
    "A queda após 2015 **não significa menos lançamentos musicais**, mas sim menos cobertura da amostra."
)

df_time = get_releases_over_time(country=country_param)

if df_time.empty:
    st.info("Sem dados temporais para este filtro.")
else:
    fig6 = px.line(
        df_time,
        x="ano", y="total_lancamentos",
        markers=True,
        labels={"ano": "Ano", "total_lancamentos": "Nº de lançamentos"},
        title="Lançamentos por ano"
    )
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# Top artistas por ouvintes
st.header("6. Top artistas por ouvintes únicos (Last.fm)")
st.caption("Os 1000 artistas mais populares em playlists foram enriquecidos com dados do Last.fm.")
st.markdown(
    "**Coldplay lidera com ~9M de ouvintes únicos**, seguido de Rihanna e Radiohead — nenhum deles aparece no top de playlists. "
    "**Kanye West e Eminem são os únicos presentes em ambos os tops**, confirmando um sucesso verdadeiramente transversal. "
    "O top é dominado por artistas de **rock, pop e rap com décadas de carreira** (Nirvana, Queen, Red Hot Chili Peppers), "
    "em contraste com o top de playlists dominado por hip-hop contemporâneo. "
    "O sucesso de longo prazo em streaming global pertence a géneros com história — o hip-hop domina o presente das playlists, "
    "mas o rock e o pop acumularam audiências globais ao longo de décadas."
)

df_listeners = get_top_artists_by_listeners(top_n=top_n, country=country_param)

if df_listeners.empty:
    st.info("Sem dados para este filtro.")
else:
    fig7 = px.bar(
        df_listeners,
        x="listeners", y="artist_name",
        orientation="h",
        color="listeners",
        color_continuous_scale="Reds",
        labels={"listeners": "Ouvintes únicos", "artist_name": "Artista"},
        title=f"Top {top_n} artistas por ouvintes únicos (Last.fm)"
    )
    fig7.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig7, use_container_width=True)

st.divider()

# Conclusões
st.header("Conclusões ")
st.markdown("""
> *"Que fatores influenciam o sucesso musical?"*

A análise dos dados do **Spotify Million Playlist Dataset**, **Last.fm**, **MusicBrainz** e **Wikipedia**
permite identificar três fatores principais e uma limitação estrutural:

---

**1. O género musical é o fator mais determinante — mas o seu efeito depende da plataforma.**

Hip-hop e subvariantes (trap rap, cloud rap, dancehall, rnb) dominam as playlists curadas do Spotify,
com médias de 300 a 370 aparições por artista. Em contrapartida, glam rock, britpop e nu metal lideram
em ouvintes globais no Last.fm, com médias superiores a 5 milhões de ouvintes únicos.
O mesmo artista pode ter sucesso muito diferente consoante a métrica e a plataforma utilizadas —
o **canal de distribuição favorece géneros distintos**.

---

**2. Presença em playlists e popularidade no streaming são métricas complementares, não equivalentes.**

Drake lidera as playlists com 4 565 aparições mas não figura no top de ouvintes.
Coldplay lidera em ouvintes com ~9M mas está ausente do top de playlists.
Apenas Kanye West e Eminem aparecem em ambos os tops simultaneamente.
O scatter plot confirma que a correlação entre as duas métricas é positiva mas fraca —
**existem dois perfis distintos de sucesso**: o artista de curadoria algorítmica (hip-hop contemporâneo)
e o artista de audiência global acumulada (rock e pop com décadas de carreira).
Um pipeline que use apenas uma destas métricas terá uma visão incompleta do sucesso musical.

---

**3. A dominância anglo-americana é estrutural nos dados disponíveis.**

Os EUA representam ~44% das faixas com país identificado (108 em 245), seguidos do Reino Unido (22).
Esta distribuição é consistente com a origem do dataset — utilizadores do Spotify USA — e com a
dominância histórica da indústria musical anglo-americana. No entanto, com apenas 0,3% das faixas
com país identificado, **não é possível tirar conclusões robustas sobre diferenças por país**.
Esta é a principal limitação do projeto e o trabalho mais prioritário numa iteração futura.

---

**Resposta direta à pergunta:**
O sucesso musical é influenciado pelo **género** (hip-hop para playlists; rock/pop para streaming global),
pela **plataforma de medição** (Spotify vs. Last.fm capturam dimensões diferentes),
e pela **longevidade da carreira** (audiências globais acumulam-se ao longo de décadas).
A origem geográfica não foi possível analisar de forma robusta com os dados disponíveis.
""")

st.caption("Projeto ETL — Análise de Tendências Musicais Globais | Fontes: Spotify MPD, Last.fm API, MusicBrainz, Wikipedia REST API")
