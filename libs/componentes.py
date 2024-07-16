import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_total, calculos, get_ranking, get_niveis, resample_data, get_energia, calculate_production)
import streamlit as st
import random
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import os
import numpy as np
import base64
from libs.api import gemini
import threading
import time
import asyncio
from queue import Queue

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
def titulo(label, description, color_name="gray-70"):
    ''' Componente 01 -  Cria um título com descrição '''
    return colored_header(label=label,description='', color_name=color_name)
@timeit
def select_date():
    ''' Componente 06 - Seleção de datas '''
    col1, col2, col3 = st.columns([2.0, 2.0, 2.0])

    with col1:
        periodo = {'2 min': '2min', '30 min': '30min','Hora': 'h', 'Diário': 'd', 'Semanal': 'w', 'Mensal': 'm', 'Anual': 'YE'}
        period_name = st.selectbox(
            'Selecione o período',
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

    return period, period_name, start_date, end_date
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
            <p style="font-size: 20px; margin: 0;">Energia Total Gerada</p>
            <p style="font-size: 16px; margin: 0;">{round(total, 2)} MWh/mês</p>
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
                <p style="font-size: 20px; margin: 0;">{mes_texto.upper()}</p>
                <p style="font-size: 16px; margin: 0;">{round(producao, 2)} MWh/mês</p>
                <p style="font-size: 12px; margin: 0; color: {delta_color};">{delta_sign}{delta}%</p>
            </div>
            ''', unsafe_allow_html=True)
# @timeit
# def card_component(df_mes, total):
#     ''' Componente 09 - Card '''
#     meses_pt_br = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho", 7: "julho", 8: "agosto",
#                    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
#
#     with st.container():
#         metric_card_settings = {
#             "border_size_px": 1,  # Cor do delta positivo
#             "border_color": "#CCC",  # Cor do delta negativo
#             "border_radius_px": 10,  # Raio da borda do cartão
#             "border_left_color": "#4169E1",  # Cor da borda esquerda
#             "box_shadow": "0 4px 6px rgba(0,0,0,0.1)",  # Sombra do cartão
#         }
#         st.metric(label='Energia Total Gerada', value=f'{round(total,2)} MWh/mês',delta_color='normal')
#         anterior = 0
#         df_mes = df_mes[::-1]
#         for i, index in enumerate(df_mes.index):
#             mes_numero = index.month
#             mes_texto = meses_pt_br[mes_numero]
#             producao = df_mes.values[i][0]
#             if i == len(df_mes) - 1:
#                 delta = 0
#             else:
#                 delta = round((producao-df_mes.values[i+1][0]) / df_mes.values[i+1][0], 2)
#             st.metric(label=f'{mes_texto.upper()}', value=f'{round(producao,2)} MWh/mês', delta=f'{delta}%', delta_color='normal')
#
#         style_metric_cards(**metric_card_settings)

@timeit
def get_image_base64(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@timeit
async def IA(prompt):
    await asyncio.sleep(2)  # Simular tempo de resposta da IA
    return f"Resposta para: {prompt}"

@timeit
@st.cache_data
def cached_response(prompt):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(IA(prompt))
    return response

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
                prompt_init += f'''{i} {colunas[0]}: {round(row[colunas[0]],2)} {colunas[1]}: {round(row[colunas[1]],2)}  {colunas[2]}: {round(row[colunas[2]],2)} /n'''

        # resp = gemini(prompt_init)
        resp = 'Olá, tudo bem? Como posso te ajudar?'

        message = resp

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

@timeit
def ranking_component(dados=None):
    ''' Componente 05 - Ranking '''
    col1, col2, col3 = st.columns([3.3, 4.4, 2.3], gap='small')  # Ajusta o tamanho das colunas
    usina = 'cgh_aparecida'

    with col1:
        period, period_name, start_date, end_date = select_date()

        dfs = calculos(usina, period, start_date, end_date)

        st.dataframe(dfs['df_merge'])
        chatbot_component(dfs['df_merge'])

    with col2:
        niveis_component(dfs['df_nivel'], start_date, end_date)
        energia_bar_component(dfs['df_energia'], period_name, start_date, end_date)

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
