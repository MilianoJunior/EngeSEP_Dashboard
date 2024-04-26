import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_ranking, get_niveis, resample_data, get_energia, calculate_production)
import streamlit as st
import random
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import os
import numpy as np
import base64
def titulo(label, description, color_name="gray-70"):
    ''' Componente 01 -  Cria um título com descrição '''

    # retorna o título com descrição
    # return colored_header(label=label, description=description, color_name=color_name)
    return colored_header(label=label,description='', color_name=color_name)

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

    # cria um título
    st.subheader('Timeline')

    # retorna a timeline
    return timeline(data=dados)

def radio_period():
    ''' Componente 05 - Botões de escolha '''

    # cria um título
    st.subheader('Escolha uma opção')

    # cria um botão de escolha
    choice = st.radio('Escolha uma opção', ['2 min', '30 min', 'Diário', 'Semanal', 'Mensal', 'Anual'])

    # retorna a escolha
    return choice

def select_date():
    ''' Componente 06 - Seleção de datas '''

    # inicializa as colunas
    col1, col2, col3 = st.columns([2.0, 2.0, 2.0])

    # seleciona o período de tempo
    with col1:
        # dict para converter o período de tempo
        periodo = {'2 min': '2min', '30 min': '30min','Hora': 'h', 'Diário': 'd', 'Semanal': 'w', 'Mensal': 'm', 'Anual': 'YE'}
        # seleciona o período de tempo resamplado
        period = st.selectbox(
            'Selecione o período',
            ('2 min', '30 min', 'Hora', 'Diário', 'Semanal', 'Mensal', 'Anual'),  # Opções para o seletor
            index=3  # Índice da opção padrão
        )
        period = periodo.get(period, 'h')

    # seleciona a data inicial
    with col2:
        # seleciona a data inicial, que é a data de hoje menos 30 dias
        data_inicial = (pd.to_datetime('today') - pd.Timedelta(days=7)).strftime('%d-%m-%Y %H:%M:%S')
        start_date = st.date_input('Data Inicial', value=pd.to_datetime(data_inicial, dayfirst=True),
                                   format="DD-MM-YYYY")
    # seleciona a data final
    with col3:
        # seleciona a data final, que é a data de hoje
        data_end = (pd.to_datetime('today') + pd.Timedelta(days=1)).strftime('%d-%m-%Y %H:%M:%S')
        end_date = st.date_input('Data Final', value=pd.to_datetime(data_end, dayfirst=True), format="DD-MM-YYYY")

    # retorna o período de tempo, a data inicial e a data final
    return period, start_date, end_date

def niveis_component(dados, start_date, end_date):
    ''' Componente 07 - Níveis jusante e montante '''
    # cria um objeto do tipo figura
    fig = go.Figure()
    # adiciona linha reta no gráfico para o nível máximo
    fig.add_shape(type="line",
                  x0=dados.index[0], y0=405.3, x1=dados.index[-1], y1=405.3,
                  line=dict(color="red", width=2, dash="dashdot"),name='Nível vertimento')
    fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_montante'], mode='lines', name='Montante'))
    fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_jusante'], mode='lines', name='Jusante'))

    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')

    # Configurando layout do gráfico
    fig.update_layout(title=f'Níveis Montante e Jusante : {start_date} até {end_date}',
                      xaxis_title='Data',
                      yaxis_title='Nível (m)')

    # Mostrando o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

def temperatura_component(dados, start_date, end_date):
    ''' Componente 08 - Temperatura do gerador '''


    # Cria um DataFrame com dados aleatórios
    dados = pd.DataFrame(index=range(0, 10), columns=[f'temperatura_gerador_{str(s)}' for s in range(0, 10)])
    for s in range(0, 10):
        for p in range(0, 10):
            dados.loc[s, f'temperatura_gerador_{str(p)}'] = random.randint(0, 100)


    fig = go.Figure()
    for i in range(0, 10):
        fig.add_trace(go.Scatter(x=dados.index, y=dados[f'temperatura_gerador_{str(i)}'], mode='lines', name=f'Gerador {str(i)}'))

    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')

    # Configurando layout do gráfico
    fig.update_layout(title=f'Temperatura do Gerador : {start_date} até {end_date}',
                        xaxis_title='Data',
                        yaxis_title='Temperatura (°C)')

    # Mostrando o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

def energia_component(dados, period, start_date, end_date):
    ''' Componente 08 - Energia acumulada Pie'''


    ''' Preciso criar um gráfico de pizza com a energia acumulada, onde o valor de referência é a potência nominal da usina'''
    # calcula o intervalo de tempo em horas
    intervalo = (end_date - start_date).total_seconds() / 3600
    periodo = {'2min': 2/60, '30min': 1/2, 'h': intervalo, 'd': intervalo, 'w': intervalo, 'm': intervalo, 'YE': intervalo}
    potencia_nominal = 3.15  # MW/h
    referencia = potencia_nominal * periodo.get(period, 1)

    producao = dados['acumulador_energia_p'].sum()

    print(producao, referencia, period, intervalo)

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=['Energia Acumulada', 'Potência Nominal'], values=[producao, referencia], hole=0.7))

    # Configurando layout do gráfico
    fig.update_layout(title=f'Eficência : {start_date} até {end_date}')

    # Mostrando o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)



def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def chatbot_component():
    ''' Componente 09 - Chatbot personalizado '''
    st.write("IA - Hawking")
    messages = st.empty()

    # Obtém o caminho absoluto para o diretório do script Python
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Cria o caminho absoluto para a imagem
    image_path = os.path.join(dir_path, "img.webp")

    # Obtém a imagem em base64
    image_base64 = get_image_base64(image_path)

    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []

    # Adicionar mensagem inicial do hawkings
    if len(st.session_state.chatbot_messages) == 0:
        message = "Olá, eu sou o Hawking, como posso te ajudar?"
        st.session_state.chatbot_messages.append(message)
        messages.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="data:image/webp;base64,{image_base64}" width="50" style="border-radius: 50%; margin-right: 10px;">
                            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                                <b>Usuário</b>: {message}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    if prompt := st.text_input("Digite uma mensagem..."):
        st.session_state.chatbot_messages.append(prompt)
        for i, message in enumerate(st.session_state.chatbot_messages):
            messages.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <img src="data:image/webp;base64,{image_base64}" width="50" style="border-radius: 50%; margin-right: 10px;">
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                        <b>Usuário</b>: {message}
                    </div>
                </div>
            """, unsafe_allow_html=True)

def statistics_component(data_df):
    ''' Componente 10 - Estatísticas '''

    # Gera estatísticas descritivas
    stats_df = data_df.describe()

    # Mostra as estatísticas no Streamlit
    st.dataframe(stats_df)

def energia_bar_component(dados, period, start_date, end_date):
    ''' Componente 08 - Energia acumulada Pie'''

    ''' Preciso criar um gráfico de barras com a energia acumulada'''
    # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    # st.bar_chart(chart_data)
    fig = go.Figure(data=go.Bar(y=dados['acumulador_energia_p'], x=dados.index))
    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')

    # Configurando layout do gráfico
    fig.update_layout(title=f'Energia Acumulada : {start_date} até {end_date}',
                        xaxis_title='Data',
                        yaxis_title='Energia (MW)')

    # fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
    st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1

def ranking_component(dados=None):
    ''' Componente 05 - Ranking '''

    def generate_dataframes():
        for data in get_ranking(period, start_date, end_date):
            yield data

    # cria as colunas
    col1, col2, col3 = st.columns([3.3, 4.0, 2.7], gap='small')  # Ajusta o tamanho das colunas

    col11, col12 = st.columns([0.5, 0.5], gap='small')  # Ajusta o tamanho das colunas

    usina = 'cgh_aparecida'

    with col1:
        period, start_date, end_date = select_date()
    # leitura dos dados se for None
    df_nivel = get_niveis(usina, start_date, end_date)

    # resample dos dados
    df_nivel = resample_data(df_nivel, period)

    df_energia = get_energia(usina, start_date, end_date)

    df_energia = calculate_production(df_energia,'acumulador_energia', period)


    with col1:

        # merge dataframes
        df = pd.merge(df_nivel, df_energia, on='data_hora', how='inner')

        # mudar o nome da coluna energia
        df.rename(columns={'acumulador_energia_p': 'Energia Prod. (MW)', 'nivel_montante': 'Nível Montante (m)',
                            'nivel_jusante': 'Nível Jusante (m)'}, inplace=True)

        # cria um objeto do tipo figura
        st.dataframe(df)

        # cria um objeto chatbot
        chatbot_component()

    with col2:
        # nivel de jusante e montante
        niveis_component(df_nivel, start_date, end_date)

        # get_ranking(period, start_date, end_date)
        energia_bar_component(df_energia, period, start_date, end_date)

    with col3:
        # with col11:
            # energia do gerador
        energia_component(df_energia, period, start_date, end_date)
    # with col12:
        statistics_component(df)

        # temperatura do gerador
        # temperatura_component(df_nivel, start_date, end_date)


    # for i, df in enumerate(generate_dataframes()):
    #     for key, value in df.items():
    #
    #         with col1:
    #             print(value)

                # energia = value['energia']
                # st.dataframe(value)
                # potencia_max = round(energia['potencia_atual_p'].max(),3)
                # delta = round(energia['potencia_atual_p'].diff().mean(),3)
                # delta_color = "inverse" if delta < 0 else "auto"
                # nivel_jusante_max = round(energia['nivel_jusante'].max(),3)
                # nivel_montante_max = round(energia['nivel_montante'].max(),3)
                # delta_jusante = round(energia['nivel_jusante'].diff().mean(),3)
                # delta_montante = round(energia['nivel_montante'].diff().mean(),3)
                # st.metric(label="Potência Máxima(MW)", value=potencia_max, delta=delta,
                #           delta_color="normal")
                # st.metric(label="Nível Jusante Máximo(m)", value=nivel_jusante_max, delta=delta_jusante,
                #           delta_color="normal")
                # st.metric(label="Nível Montante Máximo(m)", value=nivel_montante_max, delta=delta_montante,
                #           delta_color="normal")
            #
            # with col2:
            #     pass
                # nivel = value['nivel']
                # energia = value['energia']
                # st.bar_chart(energia['potencia_atual_p'], use_container_width=True)
                # niveis_component(nivel)
                # with col11:
                #     fig = go.Figure(data=go.Bar(y=value['nivel_jusante']))
                #     fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
                #     st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1
                # with col12:
                #     fig = go.Figure(data=go.Bar(y=value['nivel_montante']))
                #     fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
                #     st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1




