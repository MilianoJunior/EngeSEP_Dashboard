'''
    Author: Miliano Fernandes de Oliveira Junior
    Date: 03/02/2024
    Description: Este é um projeto que vai estar no github e será vinculado ao servidor da railway, sendo assim, o
    projeto será um dashboard que vai mostrar os dados de um banco de dados que será alimentado por varias tabelas
    que já estão no servidor da railway.

    1 passo: Criar um projeto no github e vincular ao projeto local. ->OK
    2 passo: Vincular o repositório do github ao servidor da railway. ->OK
    3 passo: Configurar o servidor da railway para rodar o projeto. -> Faltante
'''

import streamlit as st
import pandas as pd
import numpy as np
from database import Database


def get_data():
    querys = {
        'name_table': 'SELECT table_name FROM information_schema.tables WHERE table_schema = "public"',
    }
    # criar uma conexão com o banco de dados
    with Database() as db:
        data = db.fetch_all(query['name_table'])

    print(data.head())
    return data

def main():
    st.title('Engesep Dados')
    st.subheader('Dashboard de Dados')
    name = get_data()
    df = pd.DataFrame(
        [
            {"command": "st.selectbox", "rating": 4, "is_widget": True},
            {"command": "st.balloons", "rating": 5, "is_widget": False},
            {"command": "st.time_input", "rating": 3, "is_widget": True},
        ]
    )

    st.dataframe(df, use_container_width=True)
    # st.dataframe(name, use_container_width=True)

if __name__ == '__main__':
    main()

