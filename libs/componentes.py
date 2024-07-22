import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_total, calculos, get_weather, get_ranking, get_niveis, resample_data, get_energia, calculate_production)
import streamlit as st
import random
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import streamlit.components.v1 as components
# from streamlit_autorefresh import st_autorefresh
import os
import numpy as np
import base64
from libs.api import gemini
import threading
import time
import asyncio
from queue import Queue
import requests
from bs4 import BeautifulSoup

cont = 0
# decorador para tempo de execução
def timeit(method):
    ''' Decorador para medir o tempo de execução de uma função '''
    def timed( *args, **kw):
        global cont
        cont += 1
        name = method.__name__
        espaco = '-' * (50 - len(name))
        print(cont, name, espaco)
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        saida = f'{name}: {round(te - ts,5)} s'
        espaco = '-' * (50 - len(saida))
        print(' '*len(str(cont)), saida, espaco)

        return result
    return timed
@timeit
def get_weather_from_google(city):
    # criar variavel com a data de hoje
    today = pd.to_datetime('today').strftime('%Y/%m/%d')
    dia_literal = pd.to_datetime('today').strftime('%d/%m')

    url = f"https://ciram.epagri.sc.gov.br/index.php/{today}/previsao-5-dias/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    weather = {}
    weather['data'] = today
    weather['descricao'] = None
    for item in range(1, 30):
        try:
            texto = soup.select_one(f'#post-1995 > div > p:nth-child({item})').text
            if dia_literal in texto:
                weather['data'] = texto
            if 'Tempo' in texto:
                weather['descricao'] = texto
                break
            # print(texto)
        except Exception as e:
            pass
            # print(e)

    icon_dict = {
        "Nublado": "icons/cloud.png",
        "Chuva": "icons/raining.png",
        "Parcialmente nublado": "icons/cloudy.png",
        "Trovoada": "icons/thunder.png",
        "Sol": "icons/sun.png",
        "Neve": "icons/snow.png",
        "Guarda-chuva": "icons/umbrella.png",
        "Gotas": "icons/droplets.png",
        "Termômetro": "icons/thermometer.png",
        "Furacão": "icons/hurricane.png",
        "Onda": "icons/wave.png",
        "Vento": "icons/wind.png",
        "Lua": "icons/moon.png",
        # Adicione outros ícones conforme necessário
    }
    if weather['descricao'] is None:
        weather['descricao'] = 'Não foi possível obter a previsão do tempo.'

    for key, value in icon_dict.items():
        if key.lower() in weather['descricao'].lower():
            image_path = os.path.join(os.getcwd(), 'data', value)
            print(key)
        else:
            image_path = os.path.join(os.getcwd(), 'data', 'icons', 'cloudyDay.png')


    weather['icon'] = get_image_base64(image_path)

    return weather


# Função para exibir o componente de previsão do tempo no Streamlit
@timeit
def weather_component(city):
    weather = get_weather_from_google(city)

    if weather:
        # st.markdown(f"##### Previsão do Tempo para Chapecó")
        texto = ''
        for key, value in weather.items():
            if key == 'icon':
                continue
            texto += f'<p style="margin: 0; font-size: 12px; font-weight: bold;">{value}</p>'

        # Exibir o componente com a previsão do tempo
        st.markdown(
            f"""
                       <div style="display: flex; align-items: center; border: 1px solid #ccc; padding: 10px; border-radius: 10px; background-color: #2c2f33; color: #ffffff;">
                           <img src="data:image/png;base64,{weather['icon']}" style="width: 80px; height: 80px;" alt="Icone Chuva"/>
                           <div style="margin-left: 20px;">
                                <p style="margin: 0; font-size: 20px; font-weight: bold;"> Chapecó </p>
                                <p style="margin: 0; font-size: 16px; font-weight: bold;">{weather['data']}</p>
                                <p style="margin: 0; font-size: 14px; font-weight: bold;">{weather['descricao']}</p>
                           </div>
                       </div>
                   """,
            unsafe_allow_html=True
        )
    else:
        st.error("Não foi possível obter a previsão do tempo.")

@timeit
def titulo(label, description, color_name="gray-70"):
    ''' Componente 01 -  Cria um título com descrição '''
    return colored_header(label=label,description='', color_name=color_name)

def get_datas():
    ''' Função para obter os dados das usinas '''
    periodo = {'2 min': '2min', '30 min': '30min', 'Hora': 'h', 'Diário': 'd', 'Semanal': 'w', 'Mensal': 'm',
               'Anual': 'YE'}
    period_name = 'Diário'
    data_inicial = (pd.to_datetime('today') - pd.Timedelta(days=30)).strftime('%d-%m-%Y %H:%M:%S')
    data_end = (pd.to_datetime('today') + pd.Timedelta(days=1)).strftime('%d-%m-%Y %H:%M:%S')

    st.session_state['period'] = periodo.get(period_name, 'h')
    st.session_state['period_name'] = period_name
    st.session_state['start_date'] = pd.to_datetime(data_inicial, dayfirst=True)
    st.session_state['end_date'] = pd.to_datetime(data_end, dayfirst=True)


@timeit
def select_date():
    ''' Componente 06 - Seleção de datas '''
    col1, col2, col3, col4 = st.columns([2.0, 2.0, 2.0, 2.0])

    with col1:
        periodo = {'2 min': '2min', '30 min': '30min','Hora': 'h', 'Diário': 'd', 'Semanal': 'w', 'Mensal': 'm', 'Anual': 'YE'}
        period_name = st.selectbox(
            'Período',
            ('2 min', '30 min', 'Hora', 'Diário', 'Semanal', 'Mensal', 'Anual'),  # Opções para o seletor
            index=3  # Índice da opção padrão
        )
        period = periodo.get(period_name, 'h')

    with col2:
        data_inicial = (pd.to_datetime('today') - pd.Timedelta(days=30)).strftime('%d-%m-%Y %H:%M:%S')
        start_date = st.date_input('Data Inicial', value=pd.to_datetime(data_inicial, dayfirst=True),
                                   format="DD-MM-YYYY")
    with col3:
        data_end = (pd.to_datetime('today') + pd.Timedelta(days=1)).strftime('%d-%m-%Y %H:%M:%S')
        end_date = st.date_input('Data Final', value=pd.to_datetime(data_end, dayfirst=True), format="DD-MM-YYYY")

    with col4:
        if st.button("Atualizar"):
            st.session_state['period'] = period
            st.session_state['period_name'] = period_name
            st.session_state['start_date'] = start_date
            st.session_state['end_date'] = end_date
            st.cache_data.clear()
            st.rerun()

    # return period, period_name, start_date, end_date
@timeit
def niveis_component(dados, start_date, end_date):
    ''' Componente 07 - Níveis jusante e montante '''
    fig = go.Figure()
    fig.add_shape(type="line",
                  x0=dados.index[0], y0=405.3, x1=dados.index[-1], y1=405.3,
                  line=dict(color="red", width=2, dash="dashdot"),name='Nível vertimento')
    fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_montante'], mode='lines', name='Montante'))
    fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_jusante'], mode='lines', name='Jusante'))

    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')

    fig.update_layout(title=f'Níveis Montante e Jusante : {start_date} até {end_date}',
                      # xaxis_title='Data',
                      yaxis_title='Nível (m)')

    st.plotly_chart(fig, use_container_width=True)

@timeit
def card_component(df_mes, total):
    ''' Componente 09 - Card '''
    meses_pt_br = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 7: "julho", 8: "agosto",
                   9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}

    with st.container():
        metric_card_settings = {
            "border_size_px": 5,  # Cor do delta positivo
            "border_color": "#CCC",  # Cor do delta negativo
            "border_radius_px": 10,  # Raio da borda do cartão
            "border_left_color": "#4169E1",  # Cor da borda esquerda
            "box_shadow": "0 4px 6px rgba(0,0,0,0.1)",  # Sombra do cartão
        }
        st.markdown(f'''
        <div style="border: {metric_card_settings['border_size_px']}px solid {metric_card_settings['border_color']}; 
                    border-left: {metric_card_settings['border_size_px']}px solid {metric_card_settings['border_left_color']}; 
                    border-radius: {metric_card_settings['border_radius_px']}px; 
                    box-shadow: {metric_card_settings['box_shadow']}; 
                    padding: 10px; margin-bottom: 10px;">
            <p style="font-size: 28px; margin: 0;">Energia Total Gerada 2024</p>
            <p style="font-size: 24px; margin: 0;">{round(total, 2)}<span style="font-size: 16px; color: blue;"> MWh</span></p>
        </div>
        ''', unsafe_allow_html=True)

        df_mes = df_mes[::-1]
        for i, index in enumerate(df_mes.index):
            mes_numero = index.month
            mes_texto = meses_pt_br[mes_numero]
            producao = df_mes.values[i][0]
            if i == len(df_mes) - 1:
                delta = 0
            else:
                delta = round((producao - df_mes.values[i + 1][0]) / df_mes.values[i + 1][0] * 100, 2)

            delta_color = "green" if delta > 0 else "red" if delta < 0 else "black"
            delta_sign = "+" if delta > 0 else ""

            st.markdown(f'''
            <div style="border: {metric_card_settings['border_size_px']}px solid {metric_card_settings['border_color']}; 
                        border-left: {metric_card_settings['border_size_px']}px solid {metric_card_settings['border_left_color']}; 
                        border-radius: {metric_card_settings['border_radius_px']}px; 
                        box-shadow: {metric_card_settings['box_shadow']}; 
                        padding: 10px; margin-bottom: 10px;">
                <p style="font-size: 26px; margin: 0;">{mes_texto.upper()}</p>
                <p style="font-size: 20px; margin: 0;">{round(producao, 2)}<span style="font-size: 12px; color: blue;"> MWh/mês</span></p>
                <p style="font-size: 14px; margin: 0; color: {delta_color};">{delta_sign}{delta}%</p>
            </div>
            ''', unsafe_allow_html=True)

        city = "Chapeco"
        weather_component(city)

@st.cache_data
def get_image_base64(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@timeit
def chatbot_component(df):
    ''' Componente 09 - Chatbot personalizado '''
    st.write("IA - Hawking")
    messages = st.empty()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    image_path = os.path.join(dir_path, "img.webp")
    image_base64 = get_image_base64(image_path)

    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []

    if len(st.session_state.chatbot_messages) == 0:

        prompt_init = '''De acordo com as informações abaixo, Quanto de energia foi gerada hoje e no total? /n'''

        if not df.empty:
            colunas = list(df.columns)
            for i, row in df.iterrows():
                prompt_init += f'''{i} {colunas[0]}: {round(row[colunas[0]], 2)} {colunas[1]}: {round(row[colunas[1]], 2)}  {colunas[2]}: {round(row[colunas[2]], 2)} /n'''

        resp = 'Olá, tudo bem? Como posso te ajudar?'

        message = resp

        st.session_state.chatbot_messages.append(message)
        messages.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="data:image/webp;base64,{image_base64}" width="50" style="border-radius: 50%; margin-right: 10px;">
                            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                                <b>Usuário</b>: {message}
                            </div>
                            <span class="led"></span>
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
                    <span class="led"></span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .led {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #4169E1;
            animation: blink 3s infinite;
            margin-left: 10px;
        }

        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        </style>
    """, unsafe_allow_html=True)

@timeit
def energia_bar_component(dados, period_name, start_date, end_date):
    ''' Componente 08 - Energia acumulada Bar'''
    fig = go.Figure(data=go.Bar(y=dados['acumulador_energia_p'], x=dados.index))
    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')
    fig.update_layout(title=f'Energia Acumulada {period_name} : {start_date} até {end_date}',
                        # xaxis_title='Data',
                        yaxis_title='Energia (MWh)')
    st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1

@st.cache_data
def get_dados():
    usina = 'cgh_aparecida'
    dfs = calculos(usina, st.session_state['period'], st.session_state['start_date'], st.session_state['end_date'])
    return dfs
@timeit
def ranking_component(dados=None):
    ''' Componente 05 - Ranking '''
    # count = st_autorefresh(interval=60000, limit=100, key="fizzbuzzcounter")
    col1, col2, col3 = st.columns([3.3, 4.7, 2.0], gap='medium')  # Ajusta o tamanho das colunas
    usina = 'cgh_aparecida'
    with col1:
        if 'period' not in st.session_state:
            get_datas()

        dfs = get_dados()
        with st.container(height=500):
            chatbot_component(dfs['df_merge'])

        with st.container(height=400):
            select_date()
            st.dataframe(dfs['df_merge'])

    with col2:
        energia_bar_component(dfs['df_energia'], st.session_state['period_name'], st.session_state['start_date'], st.session_state['end_date'])
        niveis_component(dfs['df_nivel'], st.session_state['start_date'], st.session_state['end_date'])

    with col3:
        card_component(dfs['df_mes'], dfs['total'])



#                   ## Ranking ##
# 1 ranking_component ---------------------------------
# 2 select_date ---------------------------------------
#   select_date: 0.00348 s ----------------------------
# 3 chatbot_component ---------------------------------
# 4 get_image_base64 ----------------------------------
#   get_image_base64: 0.0 s ---------------------------
#   chatbot_component: 0.00797 s ----------------------
# 5 niveis_component ----------------------------------
#   niveis_component: 0.00252 s -----------------------
# 6 energia_bar_component -----------------------------
#   energia_bar_component: 0.002 s --------------------
# 7 card_component ------------------------------------
#   card_component: 4.57378 s -------------------------
#   ranking_component: 13.07216 s ---------------------

# 1 ranking_component ---------------------------------
# 2 select_date ---------------------------------------
#   select_date: 0.00201 s ----------------------------
# 3 chatbot_component ---------------------------------
# 4 get_image_base64 ----------------------------------
#   get_image_base64: 0.00099 s -----------------------
#   chatbot_component: 0.00878 s ----------------------
# 5 niveis_component ----------------------------------
#   niveis_component: 0.03074 s -----------------------
# 6 energia_bar_component -----------------------------
#   energia_bar_component: 0.00301 s ------------------
# 7 card_component ------------------------------------
#   card_component: 0.002 s ---------------------------
#   ranking_component: 5.00485 s ----------------------


















# @timeit
# def statistics_component(data_df):
#     ''' Componente 10 - Estatísticas '''
#
#     # Cria um título
#     st.subheader('Estatísticas')
#
#     # Gera estatísticas descritivas
#     stats_df = data_df.describe()
#
#     # Mostra as estatísticas no Streamlit
#     st.dataframe(stats_df)

# @timeit
# def tabs(tables: list):
#     ''' Componente 02 - Cria as abas do dashboard '''
#     return st.tabs(tables)
# @timeit
# def check_password():
#     ''' Componente 03 - Autenticação do usuário'''
#     def password_entered():
#         ''' Verifica se a senha está correta '''
#
#         # verifica se a senha está correta com a senha do ambiente
#         if btn_password == os.getenv('PASSWORD') and btn_user == os.getenv('USERNAME'):
#
#             # se a senha estiver correta, retorna True e seta a variável de sessão
#             st.session_state["password_correct"] = True
#
#             # limpa a senha
#             del st.session_state["password"]
#         else:
#
#             # se a senha estiver errada, retorna False e seta a variável de sessão
#             st.session_state["password_correct"] = False
#
#     # Verifica se a senha está correta
#     if st.session_state.get("password_correct", False):
#         return True
#
#     # Cria o formulário de autenticação
#     st.subheader('Dashboard EngeSEP')
#
#     # Input para o usuário
#     btn_user = st.text_input("Usuário", key="username")
#
#     # Input para a senha
#     btn_password = st.text_input("Password", type="password", key="password")
#
#     # botão para verificar a senha
#     btn = st.button("Enter", on_click=password_entered)
#
#     # se a senha estiver correta, retorna True
#     if "password_correct" in st.session_state:
#         st.error("😕 Password incorrect")
#
#     # retorna False
#     return False
# @timeit
# def timeline_component(dados=None):
#     ''' Componente 04 - Timeline '''
#
#     # cria um título
#     st.subheader('Timeline')
#
#     # retorna a timeline
#     return timeline(data=dados)
#
# @timeit
# def temperatura_component(dados, start_date, end_date):
#     ''' Componente 08 - Temperatura do gerador '''
#     dados = pd.DataFrame(index=range(0, 10), columns=[f'temperatura_gerador_{str(s)}' for s in range(0, 10)])
#     for s in range(0, 10):
#         for p in range(0, 10):
#             dados.loc[s, f'temperatura_gerador_{str(p)}'] = random.randint(0, 100)
#
#     fig = go.Figure()
#     for i in range(0, 10):
#         fig.add_trace(go.Scatter(x=dados.index, y=dados[f'temperatura_gerador_{str(i)}'], mode='lines', name=f'Gerador {str(i)}'))
#
#     start_date = start_date.strftime('%d-%m-%Y')
#     end_date = end_date.strftime('%d-%m-%Y')
#
#     # Configurando layout do gráfico
#     fig.update_layout(title=f'Temperatura do Gerador : {start_date} até {end_date}',
#                         xaxis_title='Data',
#                         yaxis_title='Temperatura (°C)')
#
#     # Mostrando o gráfico no Streamlit
#     st.plotly_chart(fig, use_container_width=True)

# @timeit
# def energia_component(usina, dados, period, start_date, end_date):
#     ''' Componente 08 - Energia acumulada Pie'''
#     df = get_total(usina)
#     total = float(df['acumulador_energia'].values[-1])
#     df_mes = calculate_production(df, 'acumulador_energia', 'ME')
#     meses_pt_br = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 7: "julho", 8: "agosto",
#                    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
#     st.markdown(''':blue[PRODUÇÃO DE ENERGIA] ''')
#     fig = go.Figure()
#     fig.add_trace(
#         go.Pie(values=[total], hole=0.8, marker=dict(colors=["#000000"]), showlegend=False,
#                textinfo='none'))
#     fig.update_layout(
#         annotations=[dict(text=f'{total} MW <br> Total', x=0.5, y=0.5, font_size=11, showarrow=False,
#                           font=dict(color='black'))],
#         width = 200,
#         height = 200,
#         margin=dict(l=20, r=20, t=20, b=20)  # Ajuste de margens
#     )
#     first_column = st.columns(1)
#     columns = st.columns(1)
#     with st.container():
#         with first_column[0]:
#             st.plotly_chart(fig, use_container_width=True)
#
#         cont = 0
#         colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Lista de cores para alternar
#
#         for i, (index, row) in enumerate(df_mes.iterrows()):
#             mes_numero = index.month
#             mes_texto = meses_pt_br[mes_numero]
#             producao = row['acumulador_energia_p']
#
#             fig = go.Figure()
#             fig.add_trace(
#                 go.Pie(values=[producao], hole=0.8, marker=dict(colors=[colors[i % len(colors)]]), showlegend=False,
#                        textinfo='none'))
#             fig.update_layout(
#                 annotations=[dict(text=f'{producao} MW <br> {mes_texto}', x=0.5, y=0.5, font_size=11, showarrow=False,
#                                   font=dict(color='black'))],
#                 width=150,
#                 height=150,
#                 margin=dict(l=20, r=20, t=20, b=20)  # Ajuste de margens
#             )
#             with columns[0]:
#                 st.plotly_chart(fig, use_container_width=True)
#
#             cont += 1
# def relogio():
#     clock_html = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             .clock {
#                 width: 200px;
#                 height: 200px;
#                 border: 10px solid #333;
#                 border-radius: 50%;
#                 position: relative;
#                 margin: auto;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#             }
#
#             .hand {
#                 width: 50%;
#                 height: 6px;
#                 background: #333;
#                 position: absolute;
#                 top: 50%;
#                 transform-origin: 100%;
#                 transform: translateY(-50%);
#             }
#
#             .hour {
#                 height: 8px;
#             }
#
#             .minute {
#                 height: 6px;
#             }
#
#             .second {
#                 height: 4px;
#                 background: red;
#             }
#
#             .number {
#                 position: absolute;
#                 font-size: 18px;
#                 font-weight: bold;
#                 text-align: center;
#             }
#
#             .number1 { top: 10px; left: 50%; transform: translateX(-50%); }
#             .number2 { top: 35px; left: 85px; transform: translateX(-50%); }
#             .number3 { top: 90px; right: 10px; transform: translateY(-50%); }
#             .number4 { bottom: 35px; right: 35px; transform: translateX(-50%); }
#             .number5 { bottom: 10px; left: 50%; transform: translateX(-50%); }
#             .number6 { bottom: 35px; left: 35px; transform: translateX(-50%); }
#             .number7 { bottom: 90px; left: 10px; transform: translateY(-50%); }
#             .number8 { top: 35px; left: 15px; transform: translateX(-50%); }
#         </style>
#     </head>
#     <body>
#         <div class="clock">
#             <div class="hand hour" id="hour"></div>
#             <div class="hand minute" id="minute"></div>
#             <div class="hand second" id="second"></div>
#             <div class="number number1">12</div>
#             <div class="number number2">1</div>
#             <div class="number number3">3</div>
#             <div class="number number4">5</div>
#             <div class="number number5">6</div>
#             <div class="number number6">7</div>
#             <div class="number number7">9</div>
#             <div class="number number8">11</div>
#         </div>
#         <script>
#             function updateClock() {
#                 const now = new Date();
#                 const seconds = now.getSeconds();
#                 const minutes = now.getMinutes();
#                 const hours = now.getHours();
#
#                 const secondDegrees = ((seconds / 60) * 360) + 90;
#                 const minuteDegrees = ((minutes / 60) * 360) + ((seconds/60)*6) + 90;
#                 const hourDegrees = ((hours / 12) * 360) + ((minutes/60)*30) + 90;
#
#                 document.getElementById('second').style.transform = `rotate(${secondDegrees}deg)`;
#                 document.getElementById('minute').style.transform = `rotate(${minuteDegrees}deg)`;
#                 document.getElementById('hour').style.transform = `rotate(${hourDegrees}deg)`;
#             }
#
#             setInterval(updateClock, 1000);
#             updateClock(); // Inicializar o relógio na carga
#         </script>
#     </body>
#     </html>
#     """
#
#     # Use o Streamlit para exibir o relógio em um contêiner
#     st.components.v1.html(clock_html, height=300, width=300)

'''
A competição Gemini API Developer
Patrocinado pela Google LLC
Regras oficiais

NÃO É NECESSÁRIO COMPRAR QUALQUER TIPO PARA PARTICIPAR OU GANHAR. NULO ONDE FOR PROIBIDO. VÁLIDO SOMENTE PARA INSCRITOS (ATENDER A QUALIFICAÇÃO NECESSÁRIA CONFORME ABAIXO NA SEÇÃO 4) NOS SEGUINTE: faz A PARTICIPAÇÃO NESTA PROMOÇÃO CONSTITUI A ACEITAÇÃO DESTAS REGRAS OFICIAIS.

Estas Regras oficiais foram redigidas em inglês, mas podem ser traduzidas para outros idiomas. Em caso de conflito ou inconsistências entre qualquer versão traduzida do Regulamento oficial e a versão em inglês do Regulamento oficial, a versão em inglês prevalecerá, regerá e controlará, a menos que expressamente proibido pela legislação aplicável. Anulado fora de nos países listados e onde for proibido por lei, norma ou regulamento.

A Concorrência de desenvolvedores de APIs do Gemini (a “Promoção”) é um desafio baseado em habilidades em que os participantes que atendem a todos requisitos de qualificação podem enviar um formulário de inscrição (“formulário”) e uma demonstração em vídeo de sua inscrição (o “app”) que apresente um aplicativo/projeto novo e/ou inovador. O app/projeto integra um modelo Gemini model* pela API Gemini.

*Não é preciso comprar nada para participar ou ganhar o prêmio. A participação é sem custo financeiro e todos os participantes têm a mesma chance de ganhar, independente de fazerem upgrade para um nível pago em qualquer modelo disponível PUBLICAMENTE. Embora os níveis pagos possam oferecem benefícios como limites maiores de taxa, eles não influenciarão a seleção do vencedor. O vencedor vai ser escolhidos com base nos critérios descritos nestas Regras oficiais.

Para participar da Promoção, você precisa concordar com estas Regras oficiais (“Regras”), os Termos de Privacidade do Patrocinador Política (https://policies.google.com/privacy) e termos de uso dos produtos do Google. Cada inscrição enviada para a Promoção será avaliada, e os vencedores serão escolhido/determinado de acordo com estas Regras. Confira abaixo todos os detalhes, incluindo instruções de inscrição requisitos e critérios de julgamento.


1. CONTRATO COM VINCULAÇÃO:
Para participar da Promoção, Você ("Você" ou "Participante") precisa concordar com estas Regras. Você concorda que o Envio da Sua inscrição significa que você concorda com estas Regras. A menos que Você concorde com essas Regras e cumpra-as, não poderá enviar uma à Promoção, e Você não estará qualificado para receber qualquer prêmio descrito nestas Regras. Essas Regras formam uma contrato legal vinculativo entre Você e o Patrocinador (definido abaixo) com relação a esta Promoção. Portanto, leia-os. com cuidado antes de entrar. Sem limitação, este contrato exige que Você indenize e libere todas as reivindicações contra as Entidades de promoção e concordar com a arbitragem sem remédio judicial de classe e limitação de Seus direitos e medidas judiciais. Todas as disputas serão resolvidas por arbitragem vinculativa sem tutela de urgência, conforme explicado abaixo.

AVISOS ESPECÍFICOS DO PAÍS:
Se alguma disposição destas regras for inválida de acordo com as leis, normas ou regulamentos de um determinado país, ela só será se aplicam somente dentro do permitido. Além das declarações de responsabilidade fiscal contidas nestas Regras oficiais, os vencedores são sujeito a cumprir a declaração de renda e, se aplicável, ao pagamento dos impostos devidos de acordo com as leis, regras e as regulamentações do país de residência do vencedor. Ao participar da Promoção, os Participantes concordam expressamente com aceitar que, para tudo o que está relacionado à interpretação, ao desempenho e à aplicação dessas Regras, cada uma se submetem expressamente às leis dos Estados Unidos da América e à jurisdição do órgão tribunais no Condado de Santa Clara, no estado da Califórnia, Estados Unidos da América, renunciando expressamente a qualquer outro jurisdição que possa corresponder a ele em virtude de seu domicílio atual ou futuro ou em virtude de qualquer outro causa.

LEGISLAÇÃO APLICÁVEL/JURISDIÇÃO:
A menos que as leis relevantes para o domicílio do Participante especifiquem o contrário, todas as questões e questões relacionadas ao construção, validade, interpretação e aplicabilidade destas Regras ou dos direitos e obrigações dos Participantes ou Patrocinador em relação à Promoção serão regidos e interpretados de acordo com as leis do Mountain View, Califórnia, Estados Unidos.

2. PATROCINADOR
A Promoção é patrocinada pela Google LLC, 1600 Amphitheatre Pkwy, Mountain View, CA 94043 USA (“Google” ou "Patrocinador").

3. PERÍODO DE PROMOÇÃO:
A Promoção começa quando Envios são aceitos a partir de:

12h, Horário de Greenwich
14 de maio de 2024
até 23h59 (Horário de Greenwich)
12 de agosto de 2024
("Período da Promoção").

OS PARTICIPANTES SÃO RESPONSÁVEIS POR DETERMINAR O FUSO HORÁRIO CORRESPONDENTE EM SUAS RESPECTIVAS JURISDIÇÕES.

4. QUALIFICAÇÃO:
No momento da participação e durante o Período de promoção, você precisa: (1) ser um residente legal de um dos 50 Estados Unidos, incluindo o Distrito de Colúmbia ou um dos seguintes países ou territórios: Arg vai e e e e e e e e e e e e e e e e e e e e e e e e e e e e e e também e e e e e e e e também e também e também e também e e e e e e e e e e e e e (2) ser maior de idade na Sua jurisdição de residência; (3) se inscrever como um indivíduo, não como parte de um grupo; e (4) não ser uma pessoa ou entidade sujeita a sanções ou controles de exportação dos EUA ou proibido de entrar nos termos de quaisquer outras leis aplicáveis (o "Participante"). Todas as leis e leis nacionais e locais as regulamentações do país de residência do Participante forem aplicáveis. Os residentes de países sob o embargo dos EUA não estão qualificadas para participar. A Promoção é nula onde for proibida por lei.

Funcionários, diretores, estagiários, contratados, representantes, agentes e funcionários oficiais do Google de o Google e suas respectivas empresas controladoras, subsidiárias, afiliadas e agências de publicidade e promoção, e qualquer empresa envolvida no design, execução, produção ou julgamento desta promoção (coletivamente, a "Promoção Entidades”), e suas famílias imediatas (pais, irmãos, filhos, cônjuges e companheiros), bem como as respectivas respectivos cônjuges e parceiros, independentemente de onde moram) e membros das famílias (relacionados) ou não) das Entidades Patrocinadoras não estão qualificados para participar desta Promoção.

O Patrocinador reserva-se o direito de verificar a elegibilidade e de resolver todas as disputas a qualquer momento.

5. COMO PARTICIPAR:
NÃO É NECESSÁRIO COMPRAR QUALQUER TIPO PARA PARTICIPAR OU GANHAR. Para participar da promoção, você precisa atender a todos os requisitos requisitos listados acima. Acesse https://ai.google.dev/competition (“Site da Promoção”) durante o Período de Promoção e siga as instruções fornecidas para preparar uma demonstração em vídeo do aplicativo que apresente uma nova projeto inovador que integra um modelo Gemini disponível publicamente pela API Gemini e Opcional: um (1) ou mais dos seguintes produtos do Google; Flutter, Android, Chrome, ARCore ou Firebase. Depois, enviar as seguintes informações: (1) nome; (2) sobrenome; (3) endereço de e-mail; (4) País/território de Residência (5) enviar Seu vídeo; e (6) código de suporte (coletivamente, o "Envio").

O envio deve atender aos seguintes requisitos de envio:
Criar um produto ou serviço novo e inovador que integre um modelo do Gemini disponível publicamente usando o API Gemini.
Envie um formulário de inscrição e uma demonstração em vídeo do aplicativo integrando um aplicativo Gemini* pela API Gemini.
Observação: nenhuma compra é necessária para participar ou ganhar. A participação é sem custo financeiro e todos os participantes têm um chances de ganhar, independentemente de terem escolhido fazer upgrade para um nível pago em qualquer um modelo de machine learning. Embora os níveis pagos ofereçam benefícios como limites maiores de taxa, eles não influenciarão o para selecionar o vencedor. O vencedor será escolhido com base nos critérios descritos no Regras.
Opcional: uma ou mais das seguintes tecnologias para desenvolvedores do Google podem ser usadas com a API Gemini: Flutter, Android, Chrome/Web, ARCore ou Firebase.
A duração máxima do vídeo é de 3 minutos. A duração mínima do vídeo é de 30 segundos.
Envios de vídeos com mais de três minutos de duração, somente os primeiros três minutos serão avaliados.
Envios de vídeos com menos de 30 segundos serão desqualificados.
Você pode usar narrações originais gravadas, vozes moduladas por IA ou criar vozes geradas com IA. Não há requisitos para o tipo de voz a ser incluída.
Faça upload do código junto com seu envio. Não fornecer o código pode resultar na desqualificação do Seu Envio.
Use a página de Envio para enviar Seu vídeo. Se Seu vídeo exceder 50 MB, faça o upload de uma versão em baixa resolução e inclua um link para fazer o download dela no Formulário de envio. Envios por e-mail não serão aceitos.

Ao enviar um vídeo com o código correspondente, Você garante que Seu Envio: • não contém nenhum conteúdo que infrinja quaisquer direitos de propriedade intelectual (PI) de terceiros e que Você possui ou tem todos os direitos necessários para o Envio, incluindo todos e quaisquer direitos de propriedade intelectual; • não divulgar nenhuma informação que constitua violação de uma obrigação de confidencialidade; • não contenha nenhum vírus, worm, software espião ou outros componentes ou instruções maliciosos, enganosos ou criados para limitar ou prejudicar a funcionalidade de um computador; e • não está sujeito a termos de licença que exijam que qualquer software ou documentação que incorpore ou seja derivado de Suas contribuições seja licenciado para outras pessoas.

Os envios que contiverem elementos proibidos e/ou que violem a legislação ou que de alguma outra forma sejam considerados pelo Patrocinador, a seu critério exclusivo, sejam prejudiciais ao Patrocinador ou a qualquer outra pessoa ou parte afiliada à Promoção ou inapropriados de qualquer forma, poderão ser desqualificados. O Patrocinador pode, a seu exclusivo e absoluto critério, desqualificar qualquer Participante que seja responsável por um Envio que o Patrocinador considere violar os requisitos de Envio ou estas Regras. O Patrocinador também pode, a seu exclusivo critério, desqualificar qualquer Participante que tenha um comportamento depreciativo ou depreciativo com o Patrocinador, os membros do painel de julgadores ou qualquer outra pessoa ou parte afiliada a esta Promoção, ou de qualquer outro Participante, ou que seja considerado antiesportivo pelo Patrocinador.

Os envios são aceitos a qualquer momento durante o Período da Promoção. Ela precisa ser enviada até 23h59, no Horário de Greenwich, de 12 de agosto de 2024. Os envios serão nulos se estiverem, total ou parcialmente, atrasados, ilegíveis, incompletos, alterados, falsificados, infringindo direitos de terceiros (incluindo direitos autorais), danificados, obtidos por fraude, enviados por meio de qualquer meio automatizado, como script, macro, bot, enviados por meios fraudulentos ou por qualquer meio que subvertam o processo de Envio, a critério exclusivo do Patrocinador.

Limite de 1 (um) envio por pessoa, independentemente do número de endereços de e-mail. Os envios feitos por qualquer pessoa ou endereço de e-mail que excedam o limite estabelecido serão anulados. Todos os Envios serão considerados feitos pelo proprietário da conta autorizada do endereço de e-mail informado no momento do Envio, que precisa cumprir estas Regras e, se aplicável, o possível vencedor da Promoção pode ser obrigado a mostrar uma comprovação de ser o titular autorizado da conta daquele endereço de e-mail. O "titular autorizado da conta" é a pessoa designada a um endereço de e-mail por um provedor de acesso à Internet, provedor de serviços on-line ou outra organização responsável por atribuir o endereço de e-mail para o domínio.

POLÍTICAS E CONSENTIMENTOS PARA FUNCIONÁRIOS:
Se um Participante fizer o upload de um Envio na Promoção e esse Envio violar qualquer regra ou política do empregador do Participante, o Participante poderá ser considerado não qualificado e desqualificado imediatamente. O Participante reconhece e concorda que o Patrocinador pode, a qualquer momento, solicitar essa documentação do Participante e, a qualquer momento, informar o empregador do Participante e/ou qualquer terceiro sobre a participação do Participante na Promoção e/ou o recebimento ou o possível recebimento de qualquer prêmio. Se o Participante não puder fornecer tal documentação ao Patrocinador em até 5 (cinco) dias úteis, o Patrocinador poderá desqualificar o Participante da qualificação para participar e ganhar um prêmio na Promoção.

RODADA DE AVALIAÇÃO
O Patrocinador avaliará cada Participante e seu Envio. Seu Envio, incluindo Seu vídeo e código, será avaliado com base nos seguintes critérios de julgamento (os "Critérios de Julgamento"), ponderados igualmente:

Os envios serão avaliados pelos jurados do Google que se destacarem nas 5 (cinco) categorias a seguir, relacionadas a este desafio: impacto, notável, criatividade, utilidade e execução. Cada critério será pontuado em uma escala de 1 (discordo totalmente) a 5 (concordo totalmente). Estes são os critérios de julgamento:

Categoria 1: impacto
A solução é fácil e agradável de usar para todos, inclusive pessoas com deficiência? (máximo de 5 pontos)
Essa solução tem potencial para contribuir significativamente para a sustentabilidade ambiental?(máximo de 5 pontos)
Essa solução tem potencial para contribuir significativamente para melhorar a vida das pessoas? (máximo de 5 pontos)

Categoria 2: Observabilidade
O envio é surpreendente para quem conhece bem os modelos de linguagem grandes (LLM)? (máximo de 5 pontos)
O envio é surpreendente para quem não conhece muito bem o LLM? (máximo de 5 pontos)

Categoria 3: criatividade
O envio é diferente de aplicativos existentes e bem conhecidos em termos de funcionalidade? (máximo de 5 pontos)
.
O envio difere dos aplicativos existentes e bem conhecidos na experiência do usuário? (máximo de 5 pontos)
.
A inscrição é implementada com o uso de abordagens criativas de resolução de problemas? (máximo de 5 pontos)

Categoria 4: utilidade
O envio inclui uma segmentação/perfil de usuário bem definido? (máximo de 5 pontos)
O envio identifica como a solução atende às necessidades específicas do usuário? (máximo de 5 pontos)
Como a solução, conforme implementada, ajuda os usuários a atender a essas necessidades? (máximo de 5 pontos)

Categoria 5: execução
A solução foi bem projetada e segue as práticas de engenharia de software? (máximo de 5 pontos)
O componente LLM da solução foi bem projetado e segue as práticas recomendadas de machine learning (ML)/LLM? (máximo de 5 pontos)

Pontuação máxima: 65
No caso de empate, o Patrocinador avaliará os Envios com relação ao impacto geral do vídeo para determinar o vencedor aplicável. As decisões do Patrocinador são finais e vinculantes.
Usando os resultados da pontuação nos Critérios de Julgamento, o Patrocinador selecionará onze (11) vencedores em potencial como vencedores confirmados que estarão qualificados para receber um Prêmio (definido na seção "Prêmios" abaixo) (coletivamente, os "Vencedores Confirmados"). Para ser um Vencedor confirmado, o Patrocinador precisa notificar cada vencedor em potencial por e-mail, conforme fornecido no Envio, a partir de 4 de setembro de 2024 ou até que a avaliação seja concluída. Cada Possível Vencedor deverá (a) responder à notificação do Patrocinador, (b) assinar e devolver uma Declaração de Elegibilidade e Liberar e preencher uma W9 (somente residentes nos EUA), WBEN (somente residentes do Canadá) ou quaisquer documentos fiscais conforme exigido pelo possível vencedor com base no local de residência principal e (c) fornecer quaisquer informações e documentos adicionais que possam ser necessários para o Patrocinador ou seus agentes ou representantes, no prazo de três (3) dias úteis. Se um Possível Vencedor não responder ou fornecer as informações e documentações necessárias dentro desse período ou não estiver em conformidade com estas Regras, será considerado que esse Possível Vencedor perdeu o Prêmio e será desqualificado, e um Possível Vencedor alternativo poderá ser selecionado entre todos os demais Participantes qualificados com a classificação mais alta com base nos critérios de seleção descritos neste documento. A notificação por telefone será considerada recebida quando o Vencedor em potencial participar de uma conversa ao vivo com o Patrocinador (ou seus agentes ou representantes) ou quando uma mensagem for deixada no serviço de correio de voz ou na secretária eletrônica do Possível Vencedor, o que ocorrer primeiro. A notificação por e-mail será considerada recebida quando o Possível Vencedor responder ao e-mail do Patrocinador. Todos os requisitos de notificação, bem como outros requisitos contidos nestas Regras, serão rigorosamente aplicados.

*O Melhor Envio Geral será determinado pelo Participante que tiver a maior pontuação nas categorias combinadas de Impacto, Criatividade e Utilidade. Em caso de empate, o Patrocinador determinará o Melhor Prêmio de Envio Geral. A decisão do patrocinador é final e vinculante.

**O People's Choice Award será determinado por votação on-line. Para conferir as inscrições e votar, acesse o site da promoção em (https://ai.google.dev/competition) e clique no link para o People's Choice Award. Os envios serão postados on-line de 16 de agosto de 2024 até, pelo menos, 26 de agosto de 2024 para votação pública. A votação será encerrada a partir de 26 de agosto de 2024. As inscrições com o maior número de votos serão escolhidos para o vencedor do People's Choice Award. Em caso de empate, o Patrocinador determinará o vencedor. A decisão do patrocinador é final e vinculante.

7. PRÊMIOS:
Sujeitos aos termos desta seção, os Prêmios são chamados coletivamente de ("Prêmios"):

Melhor envio geral:um vencedor: DeLorean clássico convertido em carro elétrico e mais US $60.000 (recebidos por cheque ou transferência eletrônica). Valor de varejo estimado: US$ 260.000.
Melhor app Flutter nas inscrições:um vencedor: US$ 50.000
Melhor app Android nas inscrições: 1 vencedor: US$ 50.000
Melhor app da Web nas inscrições: 1 vencedor: US$ 50.000
Melhor uso do app ARCore no envio:um vencedor: US$ 50.000
Melhor uso do app Firebase no envio: 1 vencedor: US$ 50.000
App mais criativo:um vencedor: US$ 200.000
Melhor app de jogo: 1 vencedor: USD 50.000
App mais útil:um vencedor: US$ 200.000
App mais impactante:um vencedor: US$ 300.000
**People's Choice Award:1 vencedor: troféu físico (sem valor de varejo)
Valor total do prêmio: US$ 1.260.000
Os participantes podem ganhar mais de 1 (um) prêmio.

Todos os detalhes do Prêmio ficam a critério exclusivo do Patrocinador. Se o Vencedor não puder aceitar, usar ou acessar um prêmio ou parte de um prêmio por qualquer motivo (veículo e/ou dinheiro), ele será desqualificado e o Patrocinador não será responsável por uma compensação alternativa. O Prêmio (ou qualquer parte dele) é fornecido "no estado em que se encontra" sem garantias, expressas ou implícitas, pelo Patrocinador. Com base no local residencial do Vencedor do Melhor Envio Geral, o prêmio de Melhor Envio Geral (o "veículo") pode ser dividido para fins de envio e reconstruído no local residencial dos Vencedores sob a supervisão da empresa que modificou o veículo, à custa do Patrocinador.

Divulgação adicional dos prêmios em dinheiro: os Vencedores dos Estados Unidos ou do Distrito de Colúmbia receberão o prêmio em dinheiro como cheque (enviado para o endereço fornecido durante o processo de notificação, conforme descrito na seção 6 acima). Os Vencedores internacionais receberão o prêmio em dinheiro por transferência eletrônica e precisarão enviar os detalhes da transferência. Os fundos serão emitidos dentro de quatro a seis semanas após a confirmação dos Vencedores.

Divulgações adicionais sobre o Melhor Prêmio de Envio Geral: o Vencedor será o único responsável por quaisquer tributos federais, estaduais e locais e todas as taxas e despesas relacionadas à aceitação do prêmio não especificadas como pagas pelo Patrocinador neste documento, incluindo custos de licenciamento, seguro, título e taxas de registro incorridos pelo vencedor com relação à aceitação, coleta/transporte ou uso do Prêmio, gasolina e veículo, e todas as outras despesas relacionadas à aceitação, ao encargo e às despesas de serviço, custos de transporte, despesas de manutenção, custos de transporte, despesas de manutenção, custos de transporte, despesas de manutenção, custos de transporte, despesas de manutenção, custos de transporte, cobranças e custos de transporte associados. O valor do prêmio é tributável como receita, e o Vencedor receberá um formulário 1099 do IRS (ou equivalente) para o valor total do prêmio selecionado, conforme declarado neste documento. O vencedor será responsável por todos os aspectos da operação do prêmio automóvel. O vencedor precisa ter uma carteira de habilitação válida que permita operar o veículo do prêmio no estado/província/país de residência dele e comprovação do seguro exigido por lei antes da entrega. Além disso, talvez seja necessário apresentar comprovantes dessa documentação, bem como números de identificação do contribuinte, antes de ser confirmado como Vencedor.

Caso o Vencedor não possa receber o prêmio ou seja considerado não qualificado por qualquer motivo, o Vencedor será desqualificado e um vencedor alternativo poderá ser selecionado. O Patrocinador reserva-se o direito de fornecer um prêmio de valor igual ou maior (quando permitido por lei), a seu exclusivo critério. O prêmio não pode ser substituído, atribuído, transferido ou resgatado em dinheiro; entretanto, o Patrocinador reserva para si o direito de substituir os prêmios equivalentes a critério dele. O Patrocinador não é responsável por qualquer atraso ou cancelamento da entrega de prêmios devido a circunstâncias imprevistas ou a que estejam fora do controle do Patrocinador. Se o comerciante em potencial cancelar o pedido por motivos fora do controle do Patrocinador e o prêmio não puder ser entregue, nenhuma compensação adicional será fornecida ou, se um prêmio substituto for fornecido, a diferença de valor entre o prêmio substituto e o prêmio anunciado não será fornecida em dinheiro. O Vencedor do Prêmio assume todo o risco de perda, dano ou roubo do seu prêmio e/ou seu cheque de prêmio é descontado sem permissão após a obtenção da propriedade e o Patrocinador não o substituirá. O prêmio não pode ser usado com outra promoção ou oferta.

Todos os detalhes e restrições dos prêmios não especificados nestas Regras oficiais serão determinados pelo Patrocinador de acordo com seus próprios critérios.

O VENCEDOR É RESPONSÁVEL POR VERIFICAR SEU ESTADO/CONDADO/JURISDIÇÃO EM CONFORMIDADE COM ESSES REQUISITOS DE EMISSÕES APLICÁVEIS E REQUISITOS DE INSPECÇÃO DE SEGURANÇA ANTES DE ACEITAR O PRÊMIO, E PRECISA USAR O PRÊMIO DE ACORDO COM ESSAS REGULAMENTAÇÕES. ALGUMAS JURISDIÇÕES PODEM NÃO PERMITIR AS LIMITAÇÕES OU EXCLUSÕES DE RESPONSABILIDADE POR DANOS INCIDENTAIS OU CONSEQUENCIAIS OU EXCLUSÕES DE GARANTIAS IMPLÍCITAS. ALGUMAS DAS LIMITAÇÕES OU EXCLUSÕES ACIMA PODEM NÃO APLICAR. VERIFIQUE AS LEIS ESTADUAIS E LOCAIS PARA CONHECER AS RESTRIÇÕES OU LIMITAÇÕES RELACIONADAS A ESSAS LIMITAÇÕES OU EXCLUSÕES.

8. IMPOSTOS (SE APLICÁVEL):
OS VENCEDORES CONFIRMADOS SÃO RESPONSÁVEIS POR TODAS AS RELATÓRIOS FISCAIS E DOCUMENTAÇÃO. Cada Vencedor confirmado é responsável por garantir que cumpre toda a legislação fiscal aplicável e os requisitos de registro, que podem incluir, entre outros, o preenchimento de um formulário W-9 (somente nos EUA) e de formulários, conforme exigido pelo governo do país/território de residência do vencedor. O Google e as empresas controladoras, afiliadas, agentes e parceiras do Google não serão responsáveis por quaisquer deduções fiscais que possam ser necessárias.

9. CONDIÇÕES GERAIS:
Todas as leis e regulamentos federais, estaduais, provinciais/territoriais e locais se aplicam. O Patrocinador reserva para si o direito de desqualificar qualquer Participante da Promoção se, a critério exclusivo do Patrocinador ou de seu designado, acreditar razoavelmente que o Participante tentou prejudicar a operação legítima da Promoção trapaceando, enganando ou outras práticas injustas ou irritando, abusando, ameaçando ou assediando qualquer outro participante, espectadores ou o Google (ou seus pais ou afiliados).

10. DIREITOS DE PROPRIEDADE INTELECTUAL:
Entre o Patrocinador e Você, Você detém a propriedade de todos os direitos de propriedade intelectual e industrial (incluindo direitos morais) sobre as informações, em relação ao Seu Envio. como condição de receber o Prêmio, cada Vencedor Confirmado concede ao Google, seus principais, afiliados, afiliados, agentes e empresas parceiras, uma licença perpétua, irrevo , irrevogável, global, global, global, livre de royalties e não exclusiva e não exclusiva para usar, para usar, traduzir, Cada Vencedor Confirmado concorda que, quando legalmente possível, não declarar "direitos morais" ou "droit moral" no conteúdo de vídeo, nas Atribuições em vídeo, nos ensaios ou em outros materiais ou outras gravações criados durante quaisquer Componentes do Programa (incluindo os materiais e recursos complementares, quaisquer nomes, locais, apresentações e imagens correspondentes).

A licença anterior é concedida para os fins declarados acima, inclusive, sem limitação, para permitir que o Patrocinador avalie os Envios. Além do mencionado acima, Você concorda que, se selecionado como um Vencedor Confirmado, Você trabalhará com o Google de boa-fé para disponibilizar partes de parte ou todo o Vídeo para uso perpétuo, mundial e livre de royalties do Google em todas as mídias conhecidas ou posteriormente inventadas, para fins não comerciais, promovendo a Promoção e futuras iterações dela.

11. PRIVACIDADE:
Você concorda que dados pessoais, incluindo, entre outros, nome, endereço de correspondência, número de telefone e endereço de e-mail, podem ser coletados, processados, armazenados e usados com a finalidade de conduzir e administrar a Promoção. Esses dados também podem ser usados pelo Patrocinador para verificar Sua identidade, endereço postal e número de telefone caso Você se qualifique para qualquer prêmio aplicável, bem como para entregar o prêmio aplicável. Ao fornecer dados relacionados à Promoção, Você consente expressamente com tais transferências de dados aos Estados Unidos ou a outros países. Você tem o direito de analisar, retificar ou cancelar quaisquer dados pessoais mantidos pelo Google ou pelo representante que Você forneceu no seu envio por escrito ao Google (Atenção: YouTube THE-IQ Privacy) em 901 Cherry Avenue, San Bruno, CA 94066 EUA. Nos outros casos, todas as informações pessoais coletadas no Seu Envio estão sujeitas à Política de Privacidade do Google, localizada em https://policies.google.com/privacy.

12. PUBLICIDADE:
Exceto quando proibido por lei, ao aceitar o Prêmio, cada Vencedor Confirmado concorda que o Patrocinador, seus pais, afiliados, agentes e empresas parceiras podem usar (no todo ou em parte) o Envio de vídeo para fins publicitários e promocionais sem compensação adicional, a menos que seja proibido por lei ou circunscrito por contrato separado entre um Vencedor confirmado e o Patrocinador. Cada Vencedor Confirmado concorda em divulgar seu nome e imagem nos anúncios físicos e digitais, nos suportes promocionais e no site do Patrocinador, para fins de marketing, sem qualquer remuneração adicional, para todo o mundo e pela duração de 5 (cinco) anos a partir da entrada na Promoção.

13. GARANTIA E INDENIZAÇÃO:
Você garante que Seu Envio é Seu trabalho original e, como tal, Você é o proprietário único e exclusivo e detentor dos direitos do Envio e que Você tem o direito de enviá-lo na Promoção. Você concorda em não enviar qualquer Envio que (a) viole quaisquer direitos de propriedade de terceiros, direitos de propriedade intelectual, direitos de propriedade industrial, direitos pessoais ou morais ou quaisquer outros direitos, incluindo, sem limitação, direitos autorais, marca registrada, patente, segredo comercial, privacidade, publicidade ou obrigações de confidencialidade; ou (b) violar de outra forma qualquer lei local, estadual, provincial/territorial ou federal aplicável, ou violar estas Regras. Você concorda em indenizar, defender e isentar de responsabilidade o Google, suas empresas controladoras, afiliadas, agentes e empresas parceiras por quaisquer reivindicações de terceiros decorrentes de (i) Sua violação destas Regras e (ii) do uso e/ou análise de empresas parceiras, por parte do Google, de suas principais, afiliadas, agentes e parceiras de Seu Envio, se um Vencedor Confirmado, incluindo, sem limitação, qualquer reivindicação, incluindo, sem limitação, quaisquer direitos de propriedade, direitos autorais ou de terceiros, alegando que o uso de tais direitos, direitos de propriedade ou direitos de terceiros ou de tais direitos, tais como direitos de propriedade ou direitos autorais,

14. ELIMINAÇÃO:
O Participante pode retirar Seu Envio a qualquer momento, notificando o Patrocinador. Se um Envio for cancelado, Sua qualificação para ganhar um prêmio será encerrada. Qualquer informação falsa fornecida no contexto da Promoção por Você (ou em Seu nome por Seus representantes ou agentes) com relação à identidade, endereço de correspondência, número de telefone, endereço de e-mail, propriedade de direitos ou conformidade com estas Regras ou similares pode resultar na eliminação imediata da Promoção, bem como desqualificação do recebimento de qualquer prêmio (total ou parcial) caso Você seja um Vencedor Confirmado.

15. INTERNET:
Google is not responsible for any malfunction, in whole or in part, of the Promotion Site, Gemini, Google products, or any late, lost, damaged, misdirected, incomplete, illegible, undeliverable, destroyed, or malfunction of Ads or votes or other related materials due to system errors, failed, incomplete or garbled computer or other telecommunication transmission malfunctions, hardware or software failures of any kind, lost or unavailable network connections, typographical or system/human errors and failures, technical malfunction(s) of any telephone network or lines, cable connections, satellite transmissions, servers or providers, or computer equipment, traffic congestion on the Internet or at the Promotion Site, or any combination thereof, including other telecommunication, cable, digital or satellite malfunctions and/or takedowns or removals by other parties which may limit an Entrant’s ability to participate in the Promotion.

16. DIREITO DE CANCELAR, MODIFICAR OU DESQUALIFICAR:
e por qualquer motivo, a Promoção (ou qualquer parte dela) não for capaz de funcionar conforme planejado pelo motivo de vírus de computador, bug, bug, mau funcionamento do sistema, adulterando, ataque não autorizado, intervenção não autorizada, fraude, fraude, falhas técnicas, falhas técnicas O Patrocinador ainda se reserva o direito de desqualificar qualquer Participante que adultere o processo de Envio ou qualquer outra parte do Site de Promoção ou Promoção. Qualquer tentativa por parte de um Participante de danificar deliberadamente qualquer site ou página, incluindo o Site da Promoção, ou prejudicar a operação legítima da Promoção é uma violação das leis criminais e civis e, caso tal tentativa seja feita, o Patrocinador reserva o direito de buscar indenização de tal Participante até a extensão máxima da legislação aplicável.

17. NÃO É UMA OFERTA OU CONTRATO DE TRABALHO OU OUTRA RELAÇÃO JURÍDICA:
Você reconhece e concorda que em nenhuma circunstância participará da Promoção, o recebimento/recebimento de qualquer componente do Prêmio se Você for um Vencedor Confirmado, ou qualquer item nestas Regras pode ser interpretado como uma oferta ou contrato de trabalho ou outra relação legal com o Google, sua matriz, seus afiliados, agentes e empresas parceiras. Você também reconhece e concorda que está enviando Seu Envio voluntariamente, e não em confiança ou em confiança, e que não existe nenhuma relação confidencial, fiduciária, de agência ou outra relação ou contrato implícito entre Você e o Google, suas empresas controladoras, afiliadas, agentes e parceiros, e que nenhuma relação é estabelecida por Seu Envio de acordo com estas Regras ou qualquer outro ato ou omissões em relação ao Prêmio ou a qualquer outro componente relacionado à Promoção ou a qualquer omissão.

18. FÓRUM E RECURSO A PROCEDIMENTOS JUDICIAIS:
Enquanto permitido por lei, estas Regras deverão ser regidas por, sujeitas a e interpretadas de acordo com as leis do Estado da Califórnia, Estados Unidos da América, excluindo todas as regras de conflito de leis. Se algum termo ou disposição destas Regras for considerado inválido ou não executável, todas as disposições restantes permanecerão vigentes. Até a extensão permitida por lei, os direitos de processar, buscar uma tutela de urgência ou qualquer outro recurso judicial ou qualquer outro procedimento em caso de disputas ou reivindicações resultantes de ou relacionados a esta Promoção são, por meio deste, excluídos, e todos os Participantes renunciam expressamente a todo e qualquer direito.

LEIA: AVISO IMPORTANTE SOBRE A RESOLUÇÃO DE DISPUTAS.

CHOICE OF LAW/JURISDICTION AND DISPUTE RESOLUTION: DISPUTE RESOLUTION, MANDATORY ARBITRATION, AND CHOICE OF LAW/JURISDICTION:
Todas as questões e questões relativas à construção, validade, interpretação e aplicabilidade destas Regras oficiais, ou os direitos e obrigações dos Participantes ou das Entidades da promoção em relação à Promoção, serão regidas e interpretadas de acordo com as leis do Estado da Califórnia, EUA, sem dar efeito a qualquer escolha de lei ou conflito de regras legais (seja do Estado da Califórnia, do Estado dos EUA ou de qualquer outra jurisdição que não seja a jurisdição da Califórnia). O não cumprimento, por parte das Entidades de promoção, de quaisquer termos destas Regras Oficiais não constituirá uma renúncia a essa ou qualquer outra disposição. Ao participar, o Participante concorda que sempre que Você tiver alguma discordância com as Entidades da Promoção (individual ou coletivamente) decorrente, conectada ou de alguma forma relacionada à Promoção, às Regras oficiais ou às Políticas de Privacidade, Você enviará um aviso por escrito ao Patrocinador ("Demanda). O Participante concorda que os requisitos desta Seção de Resolução de Disputas destas Regras oficiais (“Seção de Resolução de Disputas”) serão aplicados até mesmo em caso de discordâncias que possam ter surgido antes da aceitação das Regras oficiais ou das Políticas de Privacidade. O Participante precisa enviar a Demanda para o seguinte endereço (o “Endereço do Aviso”): 1600 Amphitheatre Pkwy, Mountain View, CA 94043 USA, Attention; Departamento Jurídico com uma cópia para o Administrador da Marden-Kane, Inc., 575 Underhill Blvd., Suite 222, Syosset, NY 11791-3416 EUA. O Participante concorda que não tomará nenhuma ação judicial, incluindo entrar com uma ação judicial ou exigir arbitragem, até 10 dias úteis após o Participante enviar uma Demanda. Esta resolução informal de disputas complementa e não renuncia, isenta ou substitui qualquer processo de resolução pré-processo exigido pela legislação estadual ou federal antes de abrir uma ação judicial.

Se a discordância declarada na Demanda não for resolvida de acordo com os critérios do Participante até 10 dias úteis após o recebimento e o Participante tiver a intenção de tomar medidas legais, o Participante concorda em abrir uma solicitação de arbitragem junto à Associação Americana de Arbitragem (o "Arbitrador"). As Entidades de Promoção também concordam que enviaremos toda e qualquer controvérsia com o Participante à arbitragem perante o Árbitro. Esta provisão de arbitragem limita a capacidade do Participante e das Entidades Promocionais de litigar ações judiciais em tribunal e das Entidades do Participante e Promocionais, cada uma concordando em renunciar aos respectivos direitos a um julgamento por júri.

Para qualquer envio de solicitação de arbitragem, o Participante precisa fornecer o serviço adequado de acordo com as regras do Árbitro, e a notificação ao Endereço de Notificação pode não ser suficiente. Se, por qualquer motivo, a Associação Americana de Arbitragem não puder realizar a arbitragem, o Participante poderá registrar o caso em qualquer empresa nacional de arbitragem. O Árbitro aplicará as Regras de Arbitragem de Consumidor da AAA em vigor a partir de 1o de setembro de 2014, disponíveis em (https://www.adr.org/sites/default/files/Consumer-Rules-Web_0.pdf)(e conforme possam ser alteradas) e conforme modificado pelo contrato de arbitragem nesta Seção de Resolução de Disputas. O Participante concorda que o árbitro terá jurisdição única e exclusiva sobre toda e qualquer disputa decorrente ou relacionada à Promoção ou a quaisquer disputas com as Entidades da Promoção, incluindo, mas não se limitando a, disputas quanto à interpretação ou aplicação desta Seção de Resolução de Disputas ou à validade do acordo de arbitragem neste documento. O árbitro tem autoridade para emitir todas e quaisquer medidas judiciais autorizadas por lei, exceto que quaisquer solicitações de tutela de urgência pública devem ser apresentadas em um tribunal de jurisdição competente. A Lei Federal de Arbitragem permite a aplicação de acordos de arbitragem e rege a interpretação e aplicação do contrato de arbitragem. O foro escolhido para a realização da arbitragem é Mountain View, Califórnia.

O Participante concorda que não registrará uma ação coletiva ou coletiva contra as Entidades da Promoção e que não participará de uma ação coletiva contra elas. O participante concorda que não vai unir suas reivindicações às de qualquer outra pessoa.

Não obstante qualquer outra disposição das Regras oficiais ou das Políticas de Privacidade, se esta renúncia de ação coletiva for considerada inválida por um tribunal de jurisdição competente, o contrato de arbitragem será nulo, como se nunca tivesse sido firmado, e qualquer disputa de arbitragem na ocasião será dispensada sem prejuízo e poderá ser recorrida em tribunal. Os participantes consentem irrevogavelmente com a jurisdição única e exclusiva dos tribunais estaduais ou federais do Estado da Califórnia, localizado no condado de San José, na Califórnia, para qualquer ação, processo ou processo decorrente ou relacionado a esta Promoção. Sob nenhuma circunstância o Participante ou as Entidades de promoção concordam com os procedimentos coletivos ou coletivas em arbitragem ou unem reivindicações em arbitragem.

19. LISTA DE VENCEDORES:
Os nomes dos Vencedores dos Prêmios serão informados por e-mail. Envie um e-mail para (GoogleAI@mkpromosource.com), incluindo a Solicitação da lista de vencedores, em TBD ou após a verificação dos vencedores.

O fabricante do veículo não é um participante ou patrocinador desta promoção.
'''