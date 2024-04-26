'''
    Author: Miliano Fernandes de Oliveira Junior
    Date: 03/02/2024
    Description: Este é um projeto que vai estar no github e será vinculado ao servidor da railway, sendo assim, o
    projeto será um dashboard que vai mostrar os dados de um banco de dados que será alimentado por varias tabelas
    que já estão no servidor da railway.


    1 passo: Criar um projeto no github e vincular ao projeto local. ->OK
    2 passo: Vincular o repositório do github ao servidor da railway. ->OK
    3 passo: Configurar o servidor da railway para rodar o projeto. -> OK
'''
from streamlit_extras.metric_cards import style_metric_cards
from st_on_hover_tabs import on_hover_tabs
from libs.componentes import (titulo, tabs, check_password, timeline_component, ranking_component)
from libs.funcoes import (get_datas, get_tables)
import plotly.graph_objects as go
from dotenv import load_dotenv
from datetime import datetime
from libs.api import gemini
import streamlit as st
import pandas as pd
import numpy as np
import os
import re


cont = 0
load_dotenv()

def page_principal():
    ''' Página principal do dashboard que cotém as comparações entre as usinas'''

    # inserir o título
    # titulo('CGH Aparecida', 'Página principal')

    # ranking
    ranking_component()


def page_usinas():
    """Retrieves key metrics from each usina table."""

    # Consulta para obter as tabelas do banco de dados
    tables = get_tables('usinas')

    # criar uma lista com os nomes das usinas com a pagina principal
    pages =  list(tables['nome'].values)

    # remove ponte_serradastream
    pages.remove('PCH Ponte Serrada')

    # cria as abas com as usinas
    tabs(pages)

def page_config():
    ''' Página de configurações do dashboard '''

    # inserir o título
    titulo('Configurações', 'Página de configurações')

def pages():
    ''' Header do dashboard '''

    # carregamento do css
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

    # criação do header que contém as páginas
    with st.sidebar:

        # criação do menu
        menu = on_hover_tabs(tabName=['Dashboard','Unidades','Configurações'],
                             iconName=['dashboard','power','settings'], default_choice=0)

    # Página principal
    if menu == 'Dashboard':

        # instanciar a página principal
        page_principal()

    # Página de Unidades
    elif menu == 'Unidades':

        # instanciar a página de usinas
        page_usinas()

    # Página de Configurações
    elif menu == 'Configurações':

        # instanciar a página de configurações
        page_config()


def main():
    ''' Dashboard principal '''

    # configuração da página
    st.set_page_config(
                        layout="wide",
                        page_title="EngeSEP",
                        page_icon="📊",
                        initial_sidebar_state="expanded",
                     )

    # Header
    pages()

if __name__ == '__main__':

    main()

    # # instanciar a página principal
    # if not check_password():
    #
    #     # se a senha estiver errada, para o processamento do app
    #     st.stop()
    # else:
    #
    #     # se a senha estiver correta, executa o app
    #     main()

