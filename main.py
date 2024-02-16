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
from dotenv import load_dotenv
import os
import pandas as pd
from streamlit_extras.row import row
from streamlit_extras.altex import sparkline_chart, sparkbar_chart
from streamlit_extras.colored_header import colored_header

load_dotenv()

def titulo(label, description, color_name="violet-70"):
    colored_header(
        label=label,
        description=description,
        color_name=color_name,
    )
def row(dados, vertical_align="top"):
    ''' Cria uma linha com os dados de uma usina '''
    print(dados)
    # recebe os dados da usina
    name_usina = dados[1]['nome']
    name_table = dados[1]['table_name']

    # Cria o título da usina
    titulo(name_usina, 'Status: Ligado', 'violet-70')

    # Cria uma linha com os dados da usina
    minisparklines(name_table)


    # random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    #
    # row1 = row(2, vertical_align="center")
    # row1.dataframe(random_df, use_container_width=True)
    # row1.line_chart(random_df, use_container_width=True)
    #
    # row2 = row([2, 4, 1], vertical_align="bottom")
    #
    # row2.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
    # row2.text_input("Your name")
    # row2.button("Send", use_container_width=True)

def minisparklines(name_table):
    ''' criar um dataframe com dados aleatórios '''
    # select table
    df = get_datas(name_table)
    col = st.columns(10)
    # List of columns to plot
    selected_column = st.selectbox('Escolha a coluna para análise', df.columns)
    cont = 0
    if df.empty:
        return None
    for selected_column in df.columns:
        if any([s in column for s in ['acumulador_energia', 'potencia_ativa', 'nivel_agua', 'frequencia','temp','Tf']]) and cont < 10:
            with col[cont]:
                st.metric(selected_column.replace('_', ' '), int(df[selected_column].values[-1]))
                # Convert the column to float
                df[selected_column] = df[selected_column].astype(float)

                # Create a sparkline chart
                if 'temp' in column:
                    sparkbar_chart(
                        data=df,
                        x="id",
                        y=f"{column}:Q",
                        height=80,
                        autoscale_y=True,
                    )
                else:
                    sparkline_chart(
                        data=df,
                        x="id",
                        y=f"{column}:Q",
                        height=80,
                        autoscale_y=True,
                    )
                cont += 1


        # print(df[column])
        # print('-------------------'*5)
    # with left:
    #     st.metric("Energia", int(data["price"].mean()))
    #     sparkline_chart(
    #         data=data,
    #         x="date",
    #         y="price:Q",
    #         height=80,
    #         autoscale_y=True,
    #     )
    # with middle:
    #     st.metric("Velocidade", int(data["price"].mean()))
    #     sparkline_chart(
    #         data=data,
    #         x="date",
    #         y="price:Q",
    #         height=80,
    #         autoscale_y=True,
    #     )
    # with right:
    #     st.metric("Temp. Mancal Comb.", int(data["price"].mean()))
    #     sparkline_chart(
    #         data=data,
    #         x="date",
    #         y="price:Q",
    #         height=80,
    #         autoscale_y=True,
    #     )
    # with col:
    #     st.metric("Vib. Mancal Guia", int(data["price"].mean()))
    #     sparkline_chart(
    #         data=data,
    #         x="date",
    #         y="price:Q",
    #         height=80,
    #         autoscale_y=True,
    #     )

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        print('Password entered', btn_password, 'User entered', btn_user)
        if btn_password  == os.getenv('PASSWORD') and btn_user == os.getenv('USERNAME'):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show a form to enter the password.
    st.subheader('Dashboard EngeSEP')
    # Show input for username.
    btn_user = st.text_input("Username", key="username")
    # Show input for password.
    btn_password = st.text_input("Password", type="password", key="password")

    print( 'Username: ', os.getenv('USERNAME'), btn_user, 'Password: ', os.getenv('PASSWORD'), btn_password)
    print('-------------------')

    # Show a button to submit the password.
    btn = st.button("Enter", on_click=password_entered)

    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

def get_tables(query):
    querys = {
        'name_table': 'SELECT table_name FROM information_schema.tables WHERE table_schema = "railway"',
        'usinas': 'SELECT * FROM Usinas',
    }
    try:
        # criar uma conexão com o banco de dados
        with Database() as db:
            data = db.fetch_all(querys[query])
            return data
    except Exception as e:
        print(e)
        return pd.DataFrame()
def get_columns(query):
    try:
        # criar uma conexão com o banco de dados
        query = 'ALTER TABLE Usinas ADD table_name VARCHAR(255) NOT NULL;'

        with Database() as db:
            # data = db.fetch_all(f'SHOW COLUMNS FROM {query};')
            data = db.fetch_all(query)
            return data
    except Exception as e:
        print(e)
        return pd.DataFrame()

def get_datas(query):
    try:

        # query que retorna os ultimos 10 registros da tabela
        query = f'SELECT * FROM {query} ORDER BY id DESC LIMIT 100'
        # criar uma conexão com o banco de dados
        with Database() as db:
            return db.fetch_all(query)
    except Exception as e:
        print(e)
        return pd.DataFrame()


def get_usinas():
    """Retrieves key metrics from each usina table."""
    tables = get_tables('usinas')
    tables_names = [str(name) for name in tables['table_name'].values]
    for table in tables.iterrows():
        # dados = {}
        # dados['name_usina'] = table['table_name']
        row(table)
    # return None
    # Itera sobre as tabelas em grupos de 3
    # for i in range(0, len(tables_names), 3):
    #     dados = {}
    #     # Cria 3 colunas
    #     cols = st.columns(3)
    #
    #     # Para cada coluna, adiciona a informação da tabela correspondente
    #     for j in range(3):
    #         # Verifica se ainda há tabelas para adicionar
    #         if i + j < len(tables):
    #             table_name = tables_names[i + j]
    #             cols[j].subheader(tables['nome'].values[i + j])
    #             # Aqui você pode adicionar mais informações sobre cada tabela
    #             # Por exemplo, para adicionar dados da tabela, você pode fazer:
    #             # data = get_datas(table_name)
    #             cols[j].metric(label="Status", value='Ligado', delta="1")

    # for table in tables.iterrows():
    #     usina_name = str(table[1][0])
    #     if 'cgh' in usina_name:
    #         usina_data = {}
    #
    #         # print(usina_name)
    #         st.subheader(usina_name)

            # Fetch key metrics from the database
            # data = get_datas(usina_name)

            # Extract relevant metrics into a dictionary
            # for col in data.columns:
            #     if col in ['status','acumulador_energia', 'potencia_ativa', 'nivel_agua', 'frequencia']:
            #         # usina_data[col] = data[col].iloc[0]
            #         print(col)
            #         print(data[col])
            #         print('-------------------'*5)

            # Create the card for this usina
            # create_usina_card(usina_name, usina_data)

def header():
    ''' Header do dashboard '''
    st.subheader('EngeSEP - Dashboard')
    if st.button('Voltar'):
        st.session_state["password_correct"] = False
        st.stop()
# streamlit run main.py

def main():
    ''' Dashboard principal '''
    st.set_page_config(layout="wide")
    # Header
    header()

    # Usinas
    get_usinas()



if __name__ == '__main__':
    main()
    # if not check_password():
    #     cont += 1
    #     # se a senha estiver errada, para o processamento do app
    #     st.stop()
    #     print('Senha incorreta', cont)
    # else:
    #     cont += 1
    #     print('Senha correta', cont)
    #     main()

