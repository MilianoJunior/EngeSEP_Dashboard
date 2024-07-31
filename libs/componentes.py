import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_total, calculos,
                          get_weather, get_ranking, get_niveis,
                          resample_data, get_energia, calculate_production,
                          timeit)
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
import locale
from bs4 import BeautifulSoup

# cont = 0
# # decorador para tempo de execução
# def timeit(method):
#     ''' Decorador para medir o tempo de execução de uma função '''
#     def timed( *args, **kw):
#         global cont
#         cont += 1
#         name = method.__name__
#         espaco = '-' * (50 - len(name))
#         print(cont, name, espaco)
#         ts = time.time()
#         result = method(*args, **kw)
#         te = time.time()
#         saida = f'{name}: {round(te - ts,5)} s'
#         espaco = '-' * (50 - len(saida))
#         print(' '*len(str(cont)), saida, espaco)
#
#         return result
#     return timed
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

# Definir o locale para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def calculo(EngMes):
    valor = (EngMes * 622 * 0.3838) + (EngMes * 467 * 0.6162)
    valor_formatado = locale.currency(valor, grouping=True)
    return valor_formatado

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
            valor = calculo(producao)
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
                <p style="font-size: 20px; margin: 0;">{round(producao, 2)}
                <span style="font-size: 12px; color: blue;"> MWh/mês</span></p>
                <p style="font-size: 18px; margin: 0;">{valor} <span style="font-size: 12px; color: blue;"> Receita bruta estimada</span></p>
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
    fig.update_layout(title=f'Energia Acumulada {period_name} : {start_date} até {end_date}',yaxis_title='Energia (MWh)')
    st.plotly_chart(fig, use_container_width=True)

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

