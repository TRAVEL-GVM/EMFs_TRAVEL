from io import BytesIO
import requests
from io import StringIO
import pandas as pd
from xlsxwriter import Workbook
from config import *
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

def plot_correlation_matrix(df):
    """
    Gera uma matriz triangular de correlação interativa em tons de verde usando Plotly.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados para calcular a correlação.

    Returns:
        plotly.graph_objects.Figure: Figura interativa da matriz de correlação.
    """
    # Calcula a matriz de correlação
    corr = df.corr()

    # Cria uma máscara para a matriz triangular superior
    mask = np.triu(np.ones(corr.shape), k=1)  # k=1 para manter a diagonal
    corr = corr.where(mask == 0)  # Aplica a máscara, mantendo apenas a parte triangular inferior

    # Cria a figura do heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='Greens',  # Escala de cores em tons de verde
            zmin=-1,  # Define o limite mínimo da correlação
            zmax=1,   # Define o limite máximo da correlação
            colorbar=dict(title="Correlation", tickvals=[-1, 0, 1], ticks="outside"),
            texttemplate="%{z:.2f}",  # Exibe os valores da correlação com 2 casas decimais
            textfont={"size": 15},    # Ajusta o tamanho da fonte dos valores
            hoverongaps=False         # Remove o hover nas lacunas
        )
    )

    # Atualiza o layout da figura
    fig.update_layout(
        title="Triangular Correlation Matrix",
        xaxis=dict(title="Variables", tickangle=45),
        yaxis=dict(title="Variables", autorange="reversed"),  # Inverte a ordem do eixo Y
        template="plotly_white",
        autosize=False, 
        height=600       # Define a altura do gráfico para torná-lo mais quadrado
    )

    return fig

def convert_df_to_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max() + 2, len(col) + 2) # Calcula o tamanho máximo da coluna + padding
            worksheet.set_column(idx, idx, max_len)  # Define a largura de cada coluna

        # Formatar o cabeçalho (linha das colunas)
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'font_color': '#FFFFFF',
            'valign': 'center',
            'align': 'center',
            'fg_color': default_color1,
            'border': 1
        })

        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        for row_num in range(1, len(df) + 1):
            worksheet.set_row(row_num, None, cell_format)

    output.seek(0)
    return output


def generate_interactive_line_plot(df, time_column, value_columns):
    """
    Gera um gráfico de linha interativo em função do tempo para as variáveis do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados.
        time_column (str): Nome da coluna que representa o tempo.
        value_columns (list): Lista de colunas cujos valores serão plotados.

    Returns:
        plotly.graph_objects.Figure: Figura interativa do gráfico.
    """
    # Converte o DataFrame para o formato longo
    df_long = df.melt(id_vars=[time_column], value_vars=value_columns, 
                      var_name='Variável', value_name='Valor')

    # Gera o gráfico interativo
    fig = px.line(df_long, x=time_column, y='Valor', color='Variável',
                  title='Line Plot Interativo',
                  labels={time_column: 'Tempo', 'Valor': 'Valor', 'Variável': 'Variável'})

    # Atualiza o layout para mover a legenda para baixo do eixo X
    fig.update_layout(
        autosize=True,
        template='plotly_white',
        legend=dict(
            orientation='h',  # Define a orientação horizontal
            y=-0.2,           # Move a legenda para baixo do eixo X
            x=0.5,            # Centraliza a legenda horizontalmente
            xanchor='center', # Define o ponto de ancoragem horizontal
            yanchor='top'     # Define o ponto de ancoragem vertical
        )
    )
    return fig