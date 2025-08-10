import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pandas.io.formats.info import frame_examples_sub

st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados',
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados-imersao-final.csv')
    return df

df = carregar_dados()

st.sidebar.header('🔍 Filtros')

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionadas = st.sidebar.multiselect('Senioridade', senioridade_disponiveis, default=senioridade_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('Tipo de Contrato', contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('Tamanho da Empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)

df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

st.title('📊 Dashboard de Análise de Salários na Área de Dados')
st.markdown('Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar a sua análise.')

st.subheader('Métricas gerais (Salário anual em USD)')

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ''

col1, col2, col3, col4 = st.columns(4)
col1.metric('Salário médio', f"${salario_medio:,.0f}")
col2.metric('Salário máximo', f"${salario_maximo:,.0f}")
col3.metric('Total de registros', f"{total_registros:,.0f}")
col4.metric('Cargo mais frequente', cargo_mais_frequente)

st.markdown('---')

st.subheader('Gráficos')

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby('cargo')['usd']
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        colorscale = 'YlOrRd'
        height = max(400, 30 * len(top_cargos))
        max_x = top_cargos['usd'].max()
        padding_factor = 0.12
        x_limit = max_x * (1 + padding_factor)

        fig = go.Figure(
            go.Bar(
                x=top_cargos['usd'],
                y=top_cargos['cargo'],
                orientation='h',
                marker=dict(
                    color=top_cargos['usd'],
                    colorscale=colorscale,
                    reversescale=False,
                    line=dict(width=0.5, color='black')),
                text=top_cargos['usd'],
                texttemplate='$%{text:,.2f}',
                textposition='outside',
                hovertemplate='%{y}: $%{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )

        fig.update_layout(
            title='Top 10 cargos por salário médio',
            title_x=0.1,
            height=height,
            margin=dict(l=160, r=180, t=60, b=40),
            yaxis=dict(categoryorder='total ascending'),
            showlegend=False,
        )

        fig.update_xaxes(range=[0, x_limit], tickformat=',.0f')

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de cargos.')

with col_graf2:
    if not df_filtrado.empty:
        vals = df_filtrado['usd'].dropna().to_numpy()
        nbins = 30
        counts, bin_edges = np.histogram(vals, bins=nbins)

        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        widths = bin_edges[1:] - bin_edges[:-1]

        colorscale = 'YlOrRd'

        fig_hist = go.Figure(
            go.Bar(
                x=bin_centers,
                y=counts,
                width=widths,
                marker=dict(
                    color=bin_centers,
                    colorscale=colorscale,
                    colorbar=dict(title='USD'),
                    line=dict(width=0.3, color='black')
                ),
                text=counts,
                texttemplate='%{text}',
                textposition='outside',
                hovertemplate='Faixa: $%{x:,.0f}<br>Contagem: %{y}<extra></extra>'
            )
        )

        fig_hist.update_layout(
            title='Distribuição de salários anuais',
            title_x=0.1,
            margin=dict(l=40, r=80, t=60, b=40),
            xaxis=dict(title='Faixa salarial (USD)', tickprefix='$', tickformat=',.0f'),
            yaxis=dict(title='Contagem'),
            bargap=0.02,
            height=420
        )

        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibis no gráfico de distribuição')

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico dos tipos de trabalho')

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
           locations='residencia_iso3',
           color='usd',
           color_continuous_scale='rdylgn',
           title='Salário médio de Cientista de Dados por país',
           labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de países')

st.subheader('Dados Detalhados')
df_filtrado = df_filtrado.drop(columns=['residencia', 'empresa'])
colunas = [
    'Ano', 'Senioridade', 'Tipo de Contrato', 'Cargo',
    'Salário', 'Moeda', 'USD', 'Tipo', 'Tamanho da Empresa', 'País'
]
df_filtrado.columns = colunas
st.dataframe(df_filtrado)
