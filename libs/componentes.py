import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_ranking)
import streamlit as st
import random
import os

def titulo(label, description, color_name="gray-70"):
    ''' Componente 01 -  Cria um título com descrição '''

    # retorna o título com descrição
    return colored_header(label=label, description=description, color_name=color_name)

def tabs(tables: list):
    ''' Componente 02 - Cria as abas do dashboard '''

    # acrescenta as abas de configurações
    return st.tabs(tables)

def check_password():
    ''' Componente 03 - Autenticação do usuário'''

    def password_entered():
        ''' Verifica se a senha está correta '''

        # verifica se a senha está correta com a senha do ambiente
        if btn_password == os.getenv('PASSWORD') and btn_user == os.getenv('USERNAME'):

            # se a senha estiver correta, retorna True e seta a variável de sessão
            st.session_state["password_correct"] = True

            # limpa a senha
            del st.session_state["password"]
        else:

            # se a senha estiver errada, retorna False e seta a variável de sessão
            st.session_state["password_correct"] = False

    # Verifica se a senha está correta
    if st.session_state.get("password_correct", False):
        return True

    # Cria o formulário de autenticação
    st.subheader('Dashboard EngeSEP')

    # Input para o usuário
    btn_user = st.text_input("Usuário", key="username")

    # Input para a senha
    btn_password = st.text_input("Password", type="password", key="password")

    # botão para verificar a senha
    btn = st.button("Enter", on_click=password_entered)

    # se a senha estiver correta, retorna True
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")

    # retorna False
    return False

def timeline_component(dados=None):
    ''' Componente 04 - Timeline '''

    # leitura dos dados se for None
    if dados is None:
        with open('libs\dados.json', "r") as f:
            dados = f.read()

    # cria um título
    st.subheader('Timeline')

    # retorna a timeline
    return timeline(data=dados)

def ranking_component(dados=None):
    ''' Componente 05 - Ranking '''

    # executa a função ranking
    dados = get_ranking()

    # leitura dos dados se for None
    if dados is None:
        # cria um DataFrame vazio
        dados = pd.DataFrame(columns=['data hora','nome', 'producao','nível água', 'eficiência'])

        # preenche o DataFrame com dados fictícios
        for i in range(10):
            dados.loc[i] = [f'2021-01-0{i}', f'Usina {i}', 1000, 100, random.randint(0, 100)]

    # ordena o DataFrame pela eficiência
    # dados = dados.sort_values(by='eficiência', ascending=False)

    # cria um título
    st.subheader('Ranking')

    # criar um ranking com todos os valores
    st.dataframe(dados)


