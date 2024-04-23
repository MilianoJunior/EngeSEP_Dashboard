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

    # index = 0

    # for ta in tab:
    #     with ta:
    #         minisparklines(tables['table_name'].values[index])
    #     index += 1

# def gauge_chart(velocidade_atual, velocidade_referencia, velocidade_maxima, velocidade_segura, velocidade_atencao, margem_erro):
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number+delta",
#         value=velocidade_atual,
#         title={'text': "Velocidade da Turbina"},
#         delta={'reference': velocidade_referencia},
#         gauge={'axis': {'range': [None, velocidade_maxima]},
#                'steps': [
#                    {'range': [0, velocidade_segura], 'color': "lightgreen"},
#                    {'range': [velocidade_segura, velocidade_atencao], 'color': "yellow"},
#                    {'range': [velocidade_atencao, velocidade_maxima], 'color': "red"}],
#                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75,
#                              'value': velocidade_atual + margem_erro}}
#     ))
#
#     fig.update_layout(autosize=True,
#                       width=200,
#                       height=250,
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')
#     st.plotly_chart(fig, use_container_width=True)


# def minisparklines(name_table):
#     ''' criar um dataframe com dados aleatórios '''
#     global cont
#
#     cont += 1
#     # print('Interação: ', cont, name_table)
#     df = get_datas(name_table)
#
#     if df.empty:
#         st.write('Sem dados')
#     else:
#         df['data_hora'] = pd.to_datetime(df['data_hora'])
#         df.set_index('data_hora', inplace=True)
#         last_index = df.index[0]
#         last_index_str = last_index.strftime('%d/%m/%Y %H:%M')
#         columns_init = [col for col in df.columns if 'energia' in col]
#         columns_metric = [col for col in df.columns if 'velocidade' in col or 'temp' in col or 'distribuidor' in col or 'pressao' in col or 'nivel' in col]
#         df = df.drop(columns=['id'])
#         dfs = {}
#         for col in columns_init:
#             dfs[col] = get_period(df, col, 'D')  # Supondo que isto retorna um DataFrame agregado por dia
#
#         resp = None
#         prompt = f'Para os dados da usina existe alguma previsão ou alerta que gostaria de fazer? Acrescente os alertas e previsões dentro das tags nos <alerta> alerta </alerta> ou <previsao> previsao </previsao>, para eu usar regex com python e colocar nos componentes st.warning(text) e st.info(text) \n'
#
#         data_hora_db = last_index_str
#         data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M')  # Formato: 01/01/2022 00:00
#
#         def get_unit(col):
#             ''' Retorna a unidade de medida de uma coluna '''
#             unidade = {
#                 'temp': '°C',
#                 'velocidade': 'RPM',
#                 'distribuidor': '%',
#                 'pressao': 'bar',
#                 'nivel': 'm'
#             }
#             for key in unidade.keys():
#                 if key in col:
#                     return unidade[key]
#             return ''
#
#         def get_previous_non_zero(values):
#             for value in reversed(values):
#                 if value != 0:
#                     return value
#             return 1
#
#         col = st.columns([.4,.3,.3])
#         altura = 750
#
#         def get_data_for_plot(df, column, period):
#             if period == 'dia':
#                 df_plot = df[column].resample('D').mean()
#             elif period == 'semana':
#                 df_plot = df[column].resample('W').mean()
#             elif period == 'mês':
#                 df_plot = df[column].resample('M').mean()
#             else:
#                 df_plot = df[column].resample('H').mean()
#             return df_plot
#
#         # primeira coluna
#         with col[0]:
#             with st.container(height=altura):
#                 titulo('Histórico', f'Última atualização {data_hora_db}')
#                 for i, (key, turbine) in enumerate(dfs.items()):
#                     if not turbine.empty:
#                         name_plot = key.replace('_', ' ').replace('ug', 'UG-')
#                         st.write(name_plot)
#                         st.bar_chart(turbine, use_container_width=True)
#         # segunda coluna
#         with col[1]:
#             with st.container(height=altura):
#                 titulo('Métricas', f'Última atualização {data_hora_db}')
#                 count = 0
#                 for coll in columns_metric:
#                     if count % 3 == 0:
#                         col1, col2, col3 = st.columns(3)
#                     name = coll.replace('_', ' ').replace('ug', 'UG-')
#                     unit = get_unit(coll)
#                     valor = f'{str(round(df[coll].values[-1],2))} {unit}'
#                     percent = f'{round((df[coll].values[-1] - get_previous_non_zero(df[coll].values[:-1])) / get_previous_non_zero(df[coll].values[:-1]) * 100, 2)} %'
#                     prompt += f'{name}: {valor} ({percent}) \n'
#                     if count % 3 == 0:
#                         col1.metric(name, valor, percent)
#                     elif count % 3 == 1:
#                         col2.metric(name, valor, percent)
#                     else:
#                         col3.metric(name, valor, percent)
#                     count += 1
#                     style_metric_cards()
#
#         # terceira coluna
#         print('--------------------------------------------------------------')
#         print('Prompt: ', prompt, len(prompt))
#         print('--------------------------------------------------------------')
#         with col[2]:
#             with st.container(height=altura):
#                 titulo('HAWKING IA ', f'Última atualização {data_hora_atual}')
#
#                 if resp == None:
#                     resp = gemini(prompt)
#                     print('Resposta: ', resp)
#                     if '<alerta>' in resp:
#                         # usar regex para pegar o texto entre as tags
#                         alerta = re.findall(r'<alerta>(.*?)</alerta>', resp)
#                         for al in alerta:
#                             st.warning(al)
#                         # st.warning(alerta)
#
#                     if '<previsao>' in resp:
#                         # usar regex para pegar o texto entre as tags
#                         previsao = re.findall(r'<previsao>(.*?)</previsao>', resp)
#                         for prev in previsao:
#                             st.info(prev)
#                         # st.info(previsao)
#
#                     if 'Erro' in resp:
#                         st.error(resp)
#
#                     # st.write(resp)

def page_principal():
    ''' Página principal do dashboard que cotém as comparações entre as usinas'''

    # inserir o título
    titulo('Principal', 'Página principal')

    # ranking
    ranking_component()

    # # Consulta para obter as tabelas do banco de dados
    # chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    #
    # # cria um gráfico de barras
    # st.bar_chart(chart_data)
    #
    # # cria uma linha de tempo
    # timeline_component()

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

