import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from functions import *

st.set_page_config(
    page_title="Monetary & Financial Statistics",
    layout="wide",  # Define o layout como wide
    initial_sidebar_state="expanded"  # Expande a barra lateral por padrão
)

st.title("Monetary & Financial Statistics")


url = 'https://raw.githubusercontent.com/TRAVEL-GVM/Data/main/Data/EMFs/emfs.csv'
df = pd.read_csv(url).drop(columns="Unnamed: 0")
df['Date'] = pd.to_datetime(df['Date'])  

with st.expander("Raw data inspection", expanded=False):
    st.subheader("Inspect and download the raw data")
    st.dataframe(df, hide_index=True)

    # Botão para download do Excel
    st.download_button(label="Download in xlsx format",
                    data=convert_df_to_excel(df),
                    file_name='EMFs.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Seleciona as colunas para o gráfico
time_column = 'Date'
not_date_columns = df.columns[1:]

# Adiciona um time slider para selecionar o intervalo de tempo
min_date = df[time_column].min().date()  # Converte para datetime.date
max_date = df[time_column].max().date()  # Converte para datetime.date
start_date, end_date = st.slider(
    "Select time range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Adiciona uma opção para selecionar as colunas a serem exibidas
# Adiciona uma opção para selecionar as colunas a serem exibidas (exceto 'Date')
selected_columns = st.multiselect(
    "Select columns to display in the plots:",
    options=not_date_columns,  # Exclui 'Date' das opções
    default=not_date_columns[1:5]  # Por padrão, seleciona algumas colunas numéricas
)

# Garante que a coluna 'Date' esteja sempre incluída
selected_columns_with_date = [time_column] + selected_columns

if not selected_columns:
    st.error("Please select at least one column to display.")
else:
    # Filtra os dados com base no intervalo de tempo selecionado
    filtered_df = df[(df[time_column] >= pd.Timestamp(start_date)) & (df[time_column] <= pd.Timestamp(end_date))]

    # Filtra apenas as colunas selecionadas, incluindo 'Date'
    filtered_df = filtered_df[selected_columns_with_date]

    value_columns = filtered_df.columns[1:]  # Atualiza value_columns para incluir apenas as colunas selecionadas

    # Adiciona uma opção para normalizar as variáveis
    normalize = st.checkbox("Normalize variables for the plot")

    # Normaliza as variáveis, se a opção estiver marcada
    if normalize:
        filtered_df[value_columns] = filtered_df[value_columns].apply(lambda x: x / x.max(), axis=0)

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        # Adiciona uma opção para calcular o percentil
        percentile = st.number_input(
            "Enter the percentile to calculate (0-100):",
            min_value=0.0,  # Permite valores de ponto flutuante
            max_value=100.0,
            value=99.0,
            step=0.1  # Incremento de 0.1 para permitir floats
        )
        percentile_values = filtered_df[value_columns].apply(lambda x: np.percentile(x, percentile))
        percentile_df = pd.DataFrame(percentile_values, columns=[ str(percentile) + " percentile"])
        percentile_df.index.name = "Variables" 

        styled_table = percentile_df.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', default_color1), ('color', 'white'), ('text-align', 'center')]},
            {'selector': 'tbody td', 'props': [('background-color', 'white'), ('color', 'black'), ('text-align', 'center')]},
            {'selector': 'thead tr', 'props': [('background-color', default_color1)]}
        ]).set_properties(**{'text-align': 'center'})

        st.write(styled_table.to_html(), unsafe_allow_html=True)
    with col2:
        fig = generate_interactive_line_plot(filtered_df, time_column, value_columns)
        st.plotly_chart(fig, use_container_width=True)



with st.expander("Correlation analysis", expanded=False):
    st.warning("Correlation analysis is only available for the selected time range above.")
    
    # Filtra apenas as colunas numéricas para a matriz de correlação
    numeric_columns = filtered_df[value_columns].select_dtypes(include=[np.number])

    if numeric_columns.empty:
        st.error("No numeric columns available for correlation analysis.")
    else:
        # Gera o gráfico de correlação com Plotly
        fig = plot_correlation_matrix(numeric_columns)

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)