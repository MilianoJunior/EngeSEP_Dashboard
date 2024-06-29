import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_timeline import timeline
from libs.funcoes import (get_datas, get_ranking, get_niveis, resample_data, get_energia, calculate_production)
import streamlit as st
# import tensorflow as tf
import random
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import os
import numpy as np
import base64
# from sklearn.model_selection import train_test_split
from libs.api import gemini
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
        data_inicial = (pd.to_datetime('today') - pd.Timedelta(days=30)).strftime('%d-%m-%Y %H:%M:%S')
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

'''
Tenho o seguinte componente, e gostaria de criar 
'''
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

    # Adiciona anotação no centro do gráfico de pizza
    fig.update_layout(
        annotations=[dict(text=f'{round(producao, 2)} MW', x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color='black'))]
    )

    # Configurando layout do gráfico
    fig.update_layout(title=f'Eficência : {start_date} até {end_date}')

    # Mostrando o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)


def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def chatbot_component(df):
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

        prompt_init = '''De acordo com as informações abaixo, Quanto de energia foi gerada hoje e no total? /n'''

        if not df.empty:
            colunas = list(df.columns)
            for i, row in df.iterrows():
                prompt_init += f'''{i} {colunas[0]}: {round(row[colunas[0]],2)} {colunas[1]}: {round(row[colunas[1]],2)}  {colunas[2]}: {round(row[colunas[2]],2)} /n'''

        # print(prompt_init)

        resp = gemini(prompt_init)

        message = resp


        # message = "Olá, eu sou o Hawking, como posso te ajudar?"
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

    # Cria um título
    st.subheader('Estatísticas')

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
        chatbot_component(df)

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




# import time
# import pandas as pd
# from streamlit_extras.colored_header import colored_header
# from streamlit_timeline import timeline
# from libs.funcoes import (get_datas, get_ranking, get_niveis, resample_data, get_energia, calculate_production)
# import streamlit as st
# # import tensorflow as tf
# import random
# import plotly.graph_objects as go
# import plotly.figure_factory as ff
# import plotly.express as px
# import os
# import numpy as np
# import base64
# # from sklearn.model_selection import train_test_split
# from libs.api import gemini
# def titulo(label, description, color_name="gray-70"):
#     ''' Componente 01 -  Cria um título com descrição '''
#
#     # retorna o título com descrição
#     # return colored_header(label=label, description=description, color_name=color_name)
#     return colored_header(label=label,description='', color_name=color_name)
#
# def tabs(tables: list):
#     ''' Componente 02 - Cria as abas do dashboard '''
#
#     # acrescenta as abas de configurações
#     return st.tabs(tables)
#
# def check_password():
#     ''' Componente 03 - Autenticação do usuário'''
#
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
#
# def timeline_component(dados=None):
#     ''' Componente 04 - Timeline '''
#
#     # cria um título
#     st.subheader('Timeline')
#
#     # retorna a timeline
#     return timeline(data=dados)
#
# def radio_period():
#     ''' Componente 05 - Botões de escolha '''
#
#     # cria um título
#     st.subheader('Escolha uma opção')
#
#     # cria um botão de escolha
#     choice = st.radio('Escolha uma opção', ['2 min', '30 min', 'Diário', 'Semanal', 'Mensal', 'Anual'])
#
#     # retorna a escolha
#     return choice
#
# def select_date():
#     ''' Componente 06 - Seleção de datas '''
#
#     # inicializa as colunas
#     col1, col2, col3 = st.columns([2.0, 2.0, 2.0])
#
#     # seleciona o período de tempo
#     with col1:
#         # dict para converter o período de tempo
#         periodo = {'2 min': '2min', '30 min': '30min','Hora': 'h', 'Diário': 'd', 'Semanal': 'w', 'Mensal': 'm', 'Anual': 'YE'}
#         # seleciona o período de tempo resamplado
#         period = st.selectbox(
#             'Selecione o período',
#             ('2 min', '30 min', 'Hora', 'Diário', 'Semanal', 'Mensal', 'Anual'),  # Opções para o seletor
#             index=3  # Índice da opção padrão
#         )
#         period = periodo.get(period, 'h')
#
#     # seleciona a data inicial
#     with col2:
#         # seleciona a data inicial, que é a data de hoje menos 30 dias
#         data_inicial = (pd.to_datetime('today') - pd.Timedelta(days=7)).strftime('%d-%m-%Y %H:%M:%S')
#         start_date = st.date_input('Data Inicial', value=pd.to_datetime(data_inicial, dayfirst=True),
#                                    format="DD-MM-YYYY")
#     # seleciona a data final
#     with col3:
#         # seleciona a data final, que é a data de hoje
#         data_end = (pd.to_datetime('today') + pd.Timedelta(days=1)).strftime('%d-%m-%Y %H:%M:%S')
#         end_date = st.date_input('Data Final', value=pd.to_datetime(data_end, dayfirst=True), format="DD-MM-YYYY")
#
#     # retorna o período de tempo, a data inicial e a data final
#     return period, start_date, end_date
#
# def niveis_component(dados, start_date, end_date):
#     ''' Componente 07 - Níveis jusante e montante '''
#     # cria um objeto do tipo figura
#     fig = go.Figure()
#     # adiciona linha reta no gráfico para o nível máximo
#     fig.add_shape(type="line",
#                   x0=dados.index[0], y0=405.3, x1=dados.index[-1], y1=405.3,
#                   line=dict(color="red", width=2, dash="dashdot"),name='Nível vertimento')
#     fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_montante'], mode='lines', name='Montante'))
#     fig.add_trace(go.Scatter(x=dados.index, y=dados['nivel_jusante'], mode='lines', name='Jusante'))
#
#     start_date = start_date.strftime('%d-%m-%Y')
#     end_date = end_date.strftime('%d-%m-%Y')
#
#     # Configurando layout do gráfico
#     fig.update_layout(title=f'Níveis Montante e Jusante : {start_date} até {end_date}',
#                       xaxis_title='Data',
#                       yaxis_title='Nível (m)')
#
#     # Mostrando o gráfico no Streamlit
#     st.plotly_chart(fig, use_container_width=True)
#
# def temperatura_component(dados, start_date, end_date):
#     ''' Componente 08 - Temperatura do gerador '''
#
#     # Cria um DataFrame com dados aleatórios
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
#
# def energia_component(dados, period, start_date, end_date):
#     ''' Componente 08 - Energia acumulada Pie'''
#
#     ''' Preciso criar um gráfico de pizza com a energia acumulada, onde o valor de referência é a potência nominal da usina'''
#     # calcula o intervalo de tempo em horas
#     intervalo = (end_date - start_date).total_seconds() / 3600
#     periodo = {'2min': 2/60, '30min': 1/2, 'h': intervalo, 'd': intervalo, 'w': intervalo, 'm': intervalo, 'YE': intervalo}
#     potencia_nominal = 3.15  # MW/h
#     referencia = potencia_nominal * periodo.get(period, 1)
#
#     producao = dados['acumulador_energia_p'].sum()
#
#     print(producao, referencia, period, intervalo)
#
#     fig = go.Figure()
#     fig.add_trace(go.Pie(labels=['Energia Acumulada', 'Potência Nominal'], values=[producao, referencia], hole=0.7))
#
#     # Adiciona anotação no centro do gráfico de pizza
#     fig.update_layout(
#         annotations=[dict(text=f'{round(producao, 2)} MW', x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color='black'))]
#     )
#
#     # Configurando layout do gráfico
#     fig.update_layout(title=f'Eficência : {start_date} até {end_date}')
#
#     # Mostrando o gráfico no Streamlit
#     st.plotly_chart(fig, use_container_width=True)
#
#
# def get_image_base64(image_path):
#     with open(image_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode('utf-8')
#
# # @st.cache(allow_output_mutation=True)
# def chatbot_component(df):
#     ''' Componente 09 - Chatbot personalizado '''
#     st.write("IA - Hawking")
#     messages = st.empty()
#
#     # Obtém o caminho absoluto para o diretório do script Python
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#
#     # Cria o caminho absoluto para a imagem
#     image_path = os.path.join(dir_path, "img.webp")
#
#     # Obtém a imagem em base64
#     image_base64 = get_image_base64(image_path)
#
#     # if "chatbot_messages" not in st.session_state:
#     #     st.session_state['chatbot_messages'] = []
#
#         # print(st.session_state.chatbot_messages)
#
#
#
#     #
#     # # Adicionar mensagem inicial do hawkings
#     # if len(st.session_state.chatbot_messages) == 0:
#     #
#     #     prompt_init = '''De acordo com as informações abaixo, Quanto de energia foi gerada hoje e no total? /n'''
#     #
#     #     if not df.empty:
#     #         colunas = list(df.columns)
#     #         for i, row in df.iterrows():
#     #             prompt_init += f'''{i} {colunas[0]}: {round(row[colunas[0]],2)} {colunas[1]}: {round(row[colunas[1]],2)}  {colunas[2]}: {round(row[colunas[2]],2)} /n'''
#     #
#     #     # print(prompt_init)
#     #
#     #     resp = gemini(prompt_init)
#     #
#     #     message = resp
#     #
#     #
#     #     # message = "Olá, eu sou o Hawking, como posso te ajudar?"
#     #     st.session_state.chatbot_messages.append(message)
#     #     messages.markdown(f"""
#     #                     <div style="display: flex; align-items: center; margin-bottom: 20px;">
#     #                         <img src="data:image/webp;base64,{image_base64}" width="50" style="border-radius: 50%; margin-right: 10px;">
#     #                         <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
#     #                             <b>Usuário</b>: {message}
#     #                         </div>
#     #                     </div>
#     #                 """, unsafe_allow_html=True)
#
#     if prompt := st.text_input("Digite uma mensagem..."):
#         dados = ''
#
#         if not df.empty:
#             colunas = list(df.columns)
#             for i, row in df.iterrows():
#                 dados += f'''{i} {colunas[0]}: {round(row[colunas[0]],2)} {colunas[1]}: {round(row[colunas[1]],2)}  {colunas[2]}: {round(row[colunas[2]],2)} /n'''
#
#         prompt_data = f''' Considere que vc está integrada em um chatbot, interaja com o usuário pedindo informações para responder as perguntas.
#         A pergunta do usuario é: {prompt}, os dados disponíveis são: {dados}/n'''
#
#         resp = gemini(prompt_data)
#
#         st.session_state['chatbot_messages'].append(prompt)
#         st.session_state['chatbot_messages'].append(resp)
#
#         for i, message in enumerate(st.session_state['chatbot_messages']):
#             messages.markdown(f"""
#                 <div style="display: flex; align-items: center; margin-bottom: 20px;">
#                     <img src="data:image/webp;base64,{image_base64}" width="50" style="border-radius: 50%; margin-right: 10px;">
#                     <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
#                         <b>Usuário</b>: {message}
#                     </div>
#                 </div>
#             """, unsafe_allow_html=True)
#
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
#
# def energia_bar_component(dados, period, start_date, end_date):
#     ''' Componente 08 - Energia acumulada Pie'''
#
#     ''' Preciso criar um gráfico de barras com a energia acumulada'''
#     # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
#
#     # st.bar_chart(chart_data)
#     fig = go.Figure(data=go.Bar(y=dados['acumulador_energia_p'], x=dados.index))
#     start_date = start_date.strftime('%d-%m-%Y')
#     end_date = end_date.strftime('%d-%m-%Y')
#
#     # Configurando layout do gráfico
#     fig.update_layout(title=f'Energia Acumulada : {start_date} até {end_date}',
#                         xaxis_title='Data',
#                         yaxis_title='Energia (MW)')
#
#     # fig.update_yaxes(range=[403.1, 408.1])  # Define os limites do eixo y
#     st.plotly_chart(fig, use_container_width=True)  # Faz o gráfico ter a mesma altura que a col1
#
# def get_dados(usina='cgh_aparecida', period='h', start_date=None, end_date=None):
#     ''' Componente 11 - Dados '''
#     # leitura dos dados se for None
#     df_nivel = get_niveis(usina, start_date, end_date)
#
#     # resample dos dados
#     df_nivel = resample_data(df_nivel, period)
#
#     df_energia = get_energia(usina, start_date, end_date)
#
#     df_energia = calculate_production(df_energia,'acumulador_energia', period)
#
#     return df_nivel, df_energia
#
#
# def generate_response(prompt):
#     ''' Gera a resposta do chatbot '''
#     # Gera a resposta do chatbot
#     response = random.choice(['1 Olá, como posso te ajudar?', ' 2 Olá, tudo bem?', ' 3 Olá, em que posso ajudar?'])
#
#     return response
#
# def process_data(period, start_date, end_date):
#     ''' Processa os dados e graficos'''
#     print('Processo data')
#     time.sleep(5)
#     print('Processo dta Finalizado')
#     st.write(period, start_date, end_date)
#
# def process_bot(prompt):
#     ''' Processa o chatbot '''
#     print('Processo bot')
#     time.sleep(2)
#     print('Processo bot Finalizado')
#     st.write(prompt)
#
#
# def ranking_component(dados=None):
#     ''' Componente 05 - Ranking '''
#
#     def generate_dataframes():
#         for data in get_ranking(period, start_date, end_date):
#             yield data
#
#     # cria as colunas
#     col1, col2, col3 = st.columns([3.3, 4.0, 2.7], gap='small')  # Ajusta o tamanho das colunas
#
#     col11, col12 = st.columns([0.5, 0.5], gap='small')  # Ajusta o tamanho das colunas
#
#     usina = 'cgh_aparecida'
#
#     with col1:
#         period, start_date, end_date = select_date()
#     # leitura dos dados se for None
#     df_nivel = get_niveis(usina, start_date, end_date)
#
#     # resample dos dados
#     df_nivel = resample_data(df_nivel, period)
#
#     df_energia = get_energia(usina, start_date, end_date)
#
#     df_energia = calculate_production(df_energia,'acumulador_energia', period)
#
#
#     with col1:
#
#         # merge dataframes
#         df = pd.merge(df_nivel, df_energia, on='data_hora', how='inner')
#
#         # mudar o nome da coluna energia
#         df.rename(columns={'acumulador_energia_p': 'Energia Prod. (MW)', 'nivel_montante': 'Nível Montante (m)',
#                             'nivel_jusante': 'Nível Jusante (m)'}, inplace=True)
#
#         # cria um objeto do tipo figura
#         st.dataframe(df)
#
#         # cria um objeto chatbot
#         chatbot_component(df)
#
#     with col2:
#         # nivel de jusante e montante
#         niveis_component(df_nivel, start_date, end_date)
#
#         # get_ranking(period, start_date, end_date)
#         energia_bar_component(df_energia, period, start_date, end_date)
#
#     with col3:
#         # with col11:
#             # energia do gerador
#         energia_component(df_energia, period, start_date, end_date)
#     # with col12:
#         statistics_component(df)
#
#         # temperatura do gerador
#         # temperatura_component(df_nivel, start_date, end_date)


# def ranking_component(dados=None):
#     ''' Componente 05 - Ranking '''
#
#     # cria as colunas
#     col1, col2, col3 = st.columns([3.3, 4.0, 2.7], gap='small')  # Ajusta o tamanho das colunas
#
#     usina = 'cgh_aparecida'
#
#
#
#     # print('Antes: ', st.session_state.get('conversa', False))
#     #
#     # if st.session_state.get('conversa', False):
#     #     valor = '1'
#     # else:
#     #     valor = '2'
#     #     st.session_state['conversa'] = []
#     #
#     # print(valor)
#     # print('Depois: ', st.session_state['conversa'])
#     #
#     # if len(st.session_state['conversa']) == 0:
#     #     print('entrou')
#     #     st.session_state['conversa'] = [
#     #                                         {
#     #                                             'User': None,
#     #                                             'Robo': 'Bem vindo, como posso ajudar?',
#     #
#     #                                         },
#     #
#     #     ]
#
#
#     # Verifica se a usina foi alterada
#     # st.write('User 1: ', valor,' - ', st.session_state.get('usina', False))
#     inicio = time.time()
#
#     with col1:
#         period, start_date, end_date = select_date()
#
#         if period:
#             print(period)
#             process_data(period, start_date, end_date)
#
#         prompt = st.chat_input("diga algo...")
#
#         if prompt:
#             print('2 - ', prompt, type(prompt))
#
#             process_bot(prompt)
#
#     print('Tempo: ', round(time.time() - inicio,3))
#     print('_____________')
#             # st.session_state['conversa'].append({ 'Robo': generate_response(prompt), 'User': prompt})
#             #
#             # for i, message in enumerate(st.session_state['conversa']):
#             #     print(i, message)
#             #     st.write(f"Robo: {message['Robo']}")
#             #     if not message['User'] is None:
#             #         st.write(f"User: {message['User']}")
#             #     st.divider()
#             # print('-------------------')
#
#     # with col2:
#     #
#     #     usina = 'cgh_aparecida'
#     #     # setar parametros
#     #     period, start_date, end_date = select_date()
#     #
#     #     df_nivel, df_energia = get_dados(usina, period, start_date, end_date)
#     #     # merge dataframes
#     #     df = pd.merge(df_nivel, df_energia, on='data_hora', how='inner')
#     #
#     #     # mudar o nome da coluna energia
#     #     df.rename(columns={'acumulador_energia_p': 'Energia Prod. (MW)', 'nivel_montante': 'Nível Montante (m)',
#     #                        'nivel_jusante': 'Nível Jusante (m)'}, inplace=True)
#     #
#     #     # cria um objeto do tipo figura
#     #     st.dataframe(df)
#
#
#     # cria um título
#
#     return False

def analise_dados():
    pass



    # with col1:
    #     period, start_date, end_date = select_date()
    #     st.write(st.session_state)
    #     if not st.session_state.get('usina', False):
    #         st.session_state['usina'] = usina
    #         st.session_state['period'] = pd.to_datetime('today')
    #         print(st.session_state['usina'])
    #         print(st.session_state['period'])
    #
    # if st.session_state['usina'] != usina:
    #     st.session_state['usina'] = usina
    #     st.session_state['period'] = pd.to_datetime('today')
    #
    # # leitura dos dados se for None
    # df_nivel = get_niveis(usina, start_date, end_date)
    #
    # # resample dos dados
    # df_nivel = resample_data(df_nivel, period)
    #
    # df_energia = get_energia(usina, start_date, end_date)
    #
    # df_energia = calculate_production(df_energia,'acumulador_energia', period)
    #
    # with col1:
    #
    #     # merge dataframes
    #     df = pd.merge(df_nivel, df_energia, on='data_hora', how='inner')
    #
    #     # mudar o nome da coluna energia
    #     df.rename(columns={'acumulador_energia_p': 'Energia Prod. (MW)', 'nivel_montante': 'Nível Montante (m)',
    #                         'nivel_jusante': 'Nível Jusante (m)'}, inplace=True)
    #
    #     # cria um objeto do tipo figura
    #     st.dataframe(df)
    #
    #     # cria um objeto chatbot
    #     chatbot_component(df)
    #
    # with col2:
    #     # nivel de jusante e montante
    #     niveis_component(df_nivel, start_date, end_date)
    #
    #     # get_ranking(period, start_date, end_date)
    #     energia_bar_component(df_energia, period, start_date, end_date)
    #
    # with col3:
    #     # with col11:
    #         # energia do gerador
    #     energia_component(df_energia, period, start_date, end_date)
    # # with col12:
    #     statistics_component(df)
    #
    #     # temperatura do gerador
    #     # temperatura_component(df_nivel, start_date, end_date)

# def normalizacao(df):
#     ''' Normalização dos dados '''
#     # normaliza os dados
#     df['nivel_montante_norm'] = (df['nivel_montante'] - df['nivel_montante'].min()) / (df['nivel_montante'].max() - df['nivel_montante'].min())
#     df['nivel_jusante_norm'] = (df['nivel_jusante'] - df['nivel_jusante'].min()) / (df['nivel_jusante'].max() - df['nivel_jusante'].min())
#     df['distribuidor_norm'] = (df['distribuidor'] - df['distribuidor'].min()) / (df['distribuidor'].max() - df['distribuidor'].min())
#     df['rotor_norm'] = (df['posicao_rotor'] - df['posicao_rotor'].min()) / (df['posicao_rotor'].max() - df['posicao_rotor'].min())
#
#     return df

# def modelo_matematico():
#     ''' Modelo matemático da usina '''
#
#     # cria o modelo
#     modelo = tf.keras.models.Sequential([
#         tf.keras.layers.Dense(4, activation='relu'),
#         tf.keras.layers.Dense(4, activation='relu'),
#         tf.keras.layers.Dense(1, activation='linear')  # Alterado para 'linear' para saída contínua
#     ])
#
#     # compila o modelo
#     modelo.compile(optimizer='adam', loss='mse', metrics=['mae', 'mse'])  # Adicionado mae como métrica
#
#     return modelo


# def rede_neural_analise(df):
#     ''' Rede neural que encontra o modelo matemático da usina '''
#     # entrada: nivel_montante, nivel_jusante, distribuidor, rotor
#     # saída: energia gerada
#
#     # normalização dos dados
#     df = normalizacao(df)
#
#     # separa os dados em treino e teste
#     X = df[['nivel_montante_norm', 'nivel_jusante_norm', 'distribuidor_norm', 'rotor_norm']]
#     y = df['acumulador_energia']
#
#     # separa os dados em treino e teste (80% treino e 20% teste)
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
#     # cria o modelo
#     modelo = modelo_matematico()
#
#     # treina o modelo
#     modelo.fit(X_train, y_train, epochs=250)
#
#     # verifica a acurácia do modelo treinado
#     loss = modelo.evaluate(X, y)
#
#     # imprime a acurácia
#     print('Acurácia do modelo:', loss)
#
#     return modelo





def analise_dados():
    ''' Componente 11 - Análise de dados '''

    # cria as variáveis
    usina = 'cgh_aparecida'
    data_init = '2024-04-01'
    data_end = '2024-05-02'
    path = os.path.join(os.getcwd(), 'data', f'{usina}.csv')

    dados_interpolacao = [[10.00, 3.00], [26.00,6.99],[35.00, 14.00],
                          [40.00, 18.01], [45.00,22.00],[50.00, 25.00],
                          [55.00, 28.00], [60.00,34.00],[65.00, 41.00],
                          [70.00, 45.00]]
    df_inter = pd.DataFrame(dados_interpolacao, columns=['distribuidor', 'rotor'])

    print(df_inter.head())

    # path = os.path.join(os.getcwd(), 'data', f'{usina}.csv')

    # leitura dos dados
    try:
        dados = pd.read_csv(path)
    except Exception as e:
        print('Erro ao ler os dados', e)
        dados = get_datas(usina, data_init, data_end)
        dados.to_csv(path, index=False)
    #
    st.dataframe(dados)
    # st.subheader('Análise de Dados')
    # # separa as colunas data_hora, acumulador_energia, nivel_montante, nivel_jusante, distribuidor, posicao_rotor
    #
    # df_select = dados[['data_hora', 'acumulador_energia', 'nivel_montante', 'nivel_jusante', 'distribuidor', 'posicao_rotor']]
    #
    # # mostra os dados
    # st.dataframe(df_select)
    #
    # # Cria um modelo matemático para a usina
    # modelo = rede_neural_analise(df_select)



    '''
    # criar um heatmap com os dados
    # cria um gráfico de linha com os dados
    # criar um heatmap com os dados
    df_select_corr = df_select.drop('data_hora', axis=1).corr()  # remove a coluna data_hora para a correlação
    # O Plotly espera listas de strings para os eixos x e y
    fig = ff.create_annotated_heatmap(
        z=df_select_corr.to_numpy(),  # usa os valores da matriz de correlação
        x=df_select_corr.columns.tolist(),  # rótulos das colunas para o eixo x
        y=df_select_corr.columns.tolist(),  # rótulos das colunas para o eixo y
        annotation_text=df_select_corr.round(2).to_numpy(),
        # arredonda os valores para 2 casas decimais para as anotações
        showscale=True  # mostra a barra de cores com a escala
    )
    st.plotly_chart(fig, use_container_width=True)

    # Identificar períodos em que a usina está operacional (potência gerada > 0)
    dados_operacionais = df_select[df_select['acumulador_energia'] > 0]

    # Normalização Min-Max das variáveis de interesse
    dados_operacionais['rotor_norm'] = (dados_operacionais['posicao_rotor'] - dados_operacionais[
        'posicao_rotor'].min()) / (dados_operacionais['posicao_rotor'].max() - dados_operacionais[
        'posicao_rotor'].min())
    dados_operacionais['distribuidor_norm'] = (dados_operacionais['distribuidor'] - dados_operacionais[
        'distribuidor'].min()) / (dados_operacionais['distribuidor'].max() - dados_operacionais['distribuidor'].min())


    st.dataframe(dados_operacionais)

    # Criar gráficos de linha para as variáveis normalizadas
    fig = go.Figure()

    # Adicionando a linha do rotor
    fig.add_trace(go.Scatter(x=dados_operacionais['data_hora'], y=dados_operacionais['rotor_norm'],
                             mode='lines', name='Rotor Normalizado'))

    # Adicionando a linha do distribuidor
    fig.add_trace(go.Scatter(x=dados_operacionais['data_hora'], y=dados_operacionais['distribuidor_norm'],
                             mode='lines', name='Distribuidor Normalizado'))

    # Atualizar layout para adicionar título e labels
    fig.update_layout(title='Análise do Rotor e Distribuidor ao longo do tempo',
                      xaxis_title='Data e Hora',
                      yaxis_title='Valores Normalizados',
                      hovermode='x')

    st.plotly_chart(fig, use_container_width=True)

    df_select_corr = dados_operacionais.drop('data_hora', axis=1).corr()  # remove a coluna data_hora para a correlação

    fig = ff.create_annotated_heatmap(
        z=df_select_corr.to_numpy(),  # usa os valores da matriz de correlação
        x=df_select_corr.columns.tolist(),  # rótulos das colunas para o eixo x
        y=df_select_corr.columns.tolist(),  # rótulos das colunas para o eixo y
        annotation_text=df_select_corr.round(2).to_numpy(),
        # arredonda os valores para 2 casas decimais para as anotações
        showscale=True  # mostra a barra de cores com a escala
    )
    st.plotly_chart(fig, use_container_width=True)


    


    print(dados.head())
    print(dados.shape)'''



