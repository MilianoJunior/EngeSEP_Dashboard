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
# import hmac

load_dotenv()
cont = 0

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

def get_data(query):
    querys = {
        'name_table': 'SELECT table_name FROM information_schema.tables WHERE table_schema = "railway"',
    }
    try:
        # criar uma conexão com o banco de dados
        with Database() as db:
            data = db.fetch_all(querys['name_table'])
            return data
    except Exception as e:
        print(e)
        return pd.DataFrame()

# streamlit run main.py

def main():
    ''' Dashboard principal '''
    st.title('Engesep Dados')
    st.subheader('Dashboard de Dados')
    # btn que retorna ao login
    if st.button('Voltar'):
        st.session_state["password_correct"] = False
        st.stop()
    name = get_data('table_name')
    st.dataframe(name, use_container_width=True)

if __name__ == '__main__':

    if not check_password():
        cont += 1
        # se a senha estiver errada, para o processamento do app
        st.stop()
        print('Senha incorreta', cont)
    else:
        cont += 1
        print('Senha correta', cont)
        main()
