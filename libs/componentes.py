import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_ranking)
import streamlit as st
import random
import plotly.graph_objects as go
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

    # leitura dos dados se for None
    # if data is None:
    #     # cria um DataFrame vazio
    #     data = pd.DataFrame(columns=['data hora','nome', 'producao','nível água', 'eficiência'])
    #
    #     # preenche o DataFrame com dados fictícios
    #     for i in range(10):
    #         dados.loc[i] = [f'2021-01-0{i}', f'Usina {i}', 1000, 100, random.randint(0, 100)]
    period = st.selectbox(
        'Selecione o período de tempo dos dados',
        ('2min','h', 'd', 'w', 'm', 'y'),  # Opções para o seletor
        index=1
    )
    def generate_dataframes():
        for data in get_ranking(period):
            yield data

    placeholder = st.empty()
    max_columns = 3  # Substitua por seu número desejado de colunas
    rows_per_column = 1  # Número de rows (gráficos e DataFrames) por coluna

    # Cria uma lista para armazenar grupos de colunas
    column_groups = [st.columns(max_columns) for _ in range(rows_per_column)]
    col1, col2 = st.columns(2)

    for i, df in enumerate(generate_dataframes()):
        for key, value in df.items():
            col1, col2 = st.columns([3.5, 6.5])  # Ajusta o tamanho das colunas
            with col1:
                st.subheader(f'{key}')
                st.dataframe(value)
                potencia_max = round(value['potencia_atual_p'].max(),3)
                delta = round(value['potencia_atual_p'].diff().mean(),3)
                delta_color = "inverse" if delta < 0 else "auto"
                nivel_jusante_max = round(value['nivel_jusante'].max(),3)
                nivel_montante_max = round(value['nivel_montante'].max(),3)
                delta_jusante = round(value['nivel_jusante'].diff().mean(),3)
                delta_montante = round(value['nivel_montante'].diff().mean(),3)
                st.metric(label="Potência Máxima(MW)", value=potencia_max, delta=delta,
                          delta_color="normal")
                st.metric(label="Nível Jusante Máximo(m)", value=nivel_jusante_max, delta=delta_jusante,
                          delta_color="normal")
                st.metric(label="Nível Montante Máximo(m)", value=nivel_montante_max, delta=delta_montante,
                          delta_color="normal")


            with col2:
                st.subheader(
                    f'Energia gerada por hora - {value.index[-1].strftime("%Y-%m-%d %H:%M:%S")}')  # Formata a data e adiciona um título ao gráfico

                # fig = go.Figure(data=go.Bar(y=value['potencia_atual_p']))
                # fig.update_yaxes(range=[0, 3.5])  # Define os limites do eixo y
                # st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1
                st.bar_chart(value['potencia_atual_p'], use_container_width=True)

                st.subheader(f'Nível de jusante ')
                fig = go.Figure(data=go.Bar(y=value['nivel_jusante']))
                fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
                st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1

                st.subheader(f'Nível de montante ')
                fig = go.Figure(data=go.Bar(y=value['nivel_montante']))
                fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
                st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1
        # if isinstance(df, dict):
        #     # limpar o placeholder
        #     print('Executando o placeholder')
        #     placeholder.empty()
        #
        #     # Calcula o índice da coluna e da linha
        #     col_idx = i % max_columns
        #     row_idx = i // max_columns % rows_per_column
        #
        #     for key, value in df.items():
        #         with column_groups[row_idx][col_idx]:
        #             st.subheader(f'Ranking - {key}')
        #             st.dataframe(value)
        #             st.bar_chart(value, use_container_width=True)
        # else:
        #     # adiciona o valor do progresso
        #     placeholder.progress(i / 10)

                    # def generate_dataframes():
    #     for data in get_ranking():
    #         yield data
    #
    # placeholder = st.empty()
    # max_columns = 10  # Substitua por seu número máximo de colunas
    # columns = st.columns(max_columns)
    #
    # for i, df in enumerate(generate_dataframes()):
    #     if isinstance(df, dict):
    #         for key, value in df.items():
    #             columns[i].subheader('Ranking - {}'.format(key))
    #             columns[i].dataframe(value)
    #             columns[i + 1].bar_chart(value[0:100])
    # col1, col2 = st.columns(2)
    # for df in generate_dataframes():
    #     if isinstance(df, dict):
    #         for key, value in df.items():
    #             col1.subheader('Ranking - {}'.format(key))
    #             col1.dataframe(value)
    #             col1.bar_chart(value[0:100])
                # st.subheader('Ranking - {}'.format(key))
                # st.dataframe(value)


