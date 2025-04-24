import streamlit as st
import pandas as pd
from functions import *

st.title("EMFs")

url = 'https://raw.githubusercontent.com/TRAVEL-GVM/EMFs/main/Data/emfs.csv'
df = pd.read_csv(url).drop(columns="Unnamed: 0")
st.dataframe(df, hide_index=True)

st.download_button(label="Download in xlsx format",
                       data=convert_df_to_excel(df),
                       file_name='EMFs.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')