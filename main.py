'''
    Author: Miliano Fernandes de Oliveira Junior
    Date: 03/02/2024
    Description: Este é um projeto que vai estar no github e será vinculado ao servidor da railway, sendo assim, o
    projeto será um dashboard que vai mostrar os dados de um banco de dados que será alimentado por varias tabelas
    que já estão no servidor da railway.

    1 passo: Criar um projeto no github e vincular ao projeto local.
    2 passo: Vincular o repositório do github ao servidor da railway.
'''

import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.title('Engesep Dados')
    st.subheader('Dashboard para visualização de dados')

    # file = st.file_uploader('Escolha a base de dados que deseja analisar', type='csv')
    # if file is not None:
    #     st.subheader('Analisando os dados')
    #     df = pd.read_csv(file)
    #     st.write(df)
    #
    #     st.subheader('Resumo dos dados')
    #     select = st.selectbox('Escolha a coluna', df.columns)
    #     st.write(df[select].describe())
    #
    #     st.subheader('Gráfico de barras')
    #     st.bar_chart(df[select])
    #
    #     st.subheader('Gráfico de linha')
    #     st.line_chart(df[select])
    #
    #     st.subheader('Gráfico de área')
    #     st.area_chart(df[select])
    #
    #     st.subheader('Mapa de calor')
    #     st.heatmap(df.corr(), annot=True)
if __name__ == '__main__':
    main()


# git config user.email "jrmfilho37@gmail.com"
# git config user.name "MilianoJunior"