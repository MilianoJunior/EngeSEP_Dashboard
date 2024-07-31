# Importar as bibliotecas
from libs.database import Database
import pandas as pd
import time
import numpy as np
from dotenv import load_dotenv
import requests
import os
load_dotenv()



def get_datas(usina,data_init, data_end):
    ''' Retorna os valores de um período '''
    try:
        query = f'SELECT * FROM {usina} WHERE data_hora BETWEEN "{data_init}" AND "{data_end}"'
        with Database() as db:                       # criar uma conexão com o banco de dados
            dados = db.fetch_all(query)              #  Faz a busca dos dados
            if dados.shape[0] == 0:                  # se não houver valores, retorna os últimos 20000 valores
                query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 2000'    # query para retornar os valores da tabela
                return db.fetch_all(query)                                      # retorna os valores da tabela
            return dados                             # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def get_total(usina):
    ''' Retorna os valores de um período '''
    try:
        query = f'SELECT data_hora, acumulador_energia, nivel_montante, nivel_jusante FROM {usina}'
        with Database() as db:                       # criar uma conexão com o banco de dados
            return db.fetch_all(query)                                      # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def get_energia(usina, data_init, data_end):
    ''' Retorna os valores de energia para um período '''

    try:
        # query para retornar os valores da tabela
        query = f'SELECT data_hora, acumulador_energia FROM {usina} WHERE data_hora BETWEEN "{data_init}" AND "{data_end}"'

        with Database() as db:                    # criar uma conexão com o banco de dados
            dados = db.fetch_all(query)           #  Faz a busca dos dados

            # se não houver valores, retorna os últimos 20000 valores
            if dados.shape[0] == 0:
                query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 200'     # query para retornar os valores da tabela
                return db.fetch_all(query)                                      # retorna os valores da tabela

            return dados                           # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def get_niveis(usina, data_init, data_end):
    ''' Retorna os valores de um período '''

    try:
        # query para retornar os valores da tabela
        query = f'SELECT data_hora, nivel_montante, nivel_jusante FROM {usina} WHERE data_hora BETWEEN "{data_init}" AND "{data_end}"'

        with Database() as db:                    # criar uma conexão com o banco de dados
            dados = db.fetch_all(query)           #  Faz a busca dos dados

            # se não houver valores, retorna os últimos 20000 valores
            if dados.shape[0] == 0:
                query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 200'     # query para retornar os valores da tabela
                return db.fetch_all(query)                                      # retorna os valores da tabela

            return dados          # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def resample_data(df, period):
    ''' Resample dos dados para o período desejado '''

    try:
        # df['data_hora'] = pd.to_datetime(df['data_hora'])  # converter a coluna data_hora para datetime
        # df.set_index('data_hora', inplace=True)            # setar a coluna data_hora como index
        df_resampled = df.resample(period).mean()          # resample para o período desejado
        # df_resampled.columns = df_resampled.columns.droplevel()     # Limpa o DataFrame para remover níveis múltiplos nas colunas

        return df_resampled

    except Exception as e:
        raise e

def get_columns(usina):
    ''' Retorna as colunas da tabela '''

    try:
        query = f'SHOW COLUMNS FROM {usina}'        # query para retornar as colunas da tabela
        with Database() as db:                      # criar uma conexão com o banco de dados
            return db.fetch_all(query)              # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar as colunas: {e}')

def get_tables():
    ''' Retorna informações sobre as tabelas '''

    try:
        query = 'SELECT * FROM Usinas'              # query para retornar as tabelas do banco de dados
        with Database() as db:                      # criar uma conexão com o banco de dados
            return db.fetch_all(query)              # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar as tabelas: {e}')

def calculate_production(df, column, period):
    '''Calcula a produção de energia corrigida para o período especificado de maneira ajustada.'''

    try:

        df[column] = df[column].astype(float)           # converter a column para float
        columnp = column + '_p'                         # cria uma nova coluna para a produção de energia

        # Resample para o período desejado e calcula a diferença entre o primeiro e o último valor do período
        df_resampled = df.resample(period).agg({column: ['first', 'last']})

        # Calcula a diferença entre o último e o primeiro valor para obter a produção de energia no período
        df_resampled[columnp] = round(df_resampled[(column, 'last')] - df_resampled[(column, 'first')], 3)

        # Limpa o DataFrame para remover níveis múltiplos nas colunas
        df_resampled.columns = ['First Value', 'Last Value', columnp]

        # Remove linhas onde a produção é NaN ou 0, pois isso indica que não houve produção no período
        df_resampled = df_resampled[df_resampled[columnp].notna() & (df_resampled[columnp] != 0)]

        # exclui as colunas First Value e Last Value
        df_resampled = df_resampled.drop(columns=['First Value', 'Last Value'])

        # Divide os valores pelo formato da usina
        df_resampled[columnp] = df_resampled[columnp]

        return df_resampled

    except Exception as e:
        raise Exception(f"Erro ao calcular a produção de energia {e}")

def retirar_outliers(df, column):
    ''' Retira os outliers de um DataFrame '''

    try:
        # Calcula o primeiro e terceiro quartil
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        # Calcula o intervalo interquartil
        iqr = q3 - q1

        # Calcula os limites inferior e superior
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Retorna os valores sem outliers
        return df[(df[column] > lower_bound) & (df[column] < upper_bound)]

    except Exception as e:
        raise Exception(f"Erro ao retirar outliers {e}")

def get_max_nivel(usina):
    '''nivel máximo'''

    query = f'SELECT * FROM {usina}'
    print('##'*10, usina, '##'*10)
    with Database() as db:  # criar uma conexão com o banco de dados
        dados = db.fetch_all(query)  # retorna os valores da tabela

        dados = dados[[column for column in dados.columns if ('nivel_agua' in column.lower() or 'nivel_jusante' in column.lower())]]

        # retirar os outliers
        for column in dados.columns:
            print(column)
            dados = retirar_outliers(dados, column)

        # valor máximo do nível
        # print(dados.head())
        print(dados.shape)
        print(type(dados))


        print(usina, ' o valor máximo: ',dados.max())

def calculos(usina, period, start_date, end_date):
    ''' Calcula a produção de energia para integrar ao dashboard '''
    df = get_total(usina)
    df['data_hora'] = pd.to_datetime(df['data_hora'])  # converter a coluna data_hora para datetime
    df.set_index('data_hora', inplace=True)  # setar a coluna data_hora como index

    df_nivel = df[['nivel_montante', 'nivel_jusante']]
    df_energia = df[['acumulador_energia']]

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_nivel = df_nivel[(df_nivel.index >= start_date) & (df_nivel.index <= end_date)]
    df_energia = df_energia[(df_energia.index >= start_date) & (df_energia.index <= end_date)]
    df_nivel = resample_data(df_nivel, period)

    df_energia = calculate_production(df_energia,'acumulador_energia', period)
    df_merge = pd.merge(df_nivel, df_energia, on='data_hora', how='inner')
    df_merge.rename(columns={'acumulador_energia_p': 'Energia Prod. (MW)', 'nivel_montante': 'Nível Montante (m)',
                       'nivel_jusante': 'Nível Jusante (m)'}, inplace=True)
    total = float(df['acumulador_energia'].values[-1])
    df_mes = calculate_production(df, 'acumulador_energia', 'ME')

    dfs = {
        'df_merge': df_merge,
        'df_nivel': df_nivel,
        'df_energia': df_energia,
        'df_mes': df_mes,
        'total': total
    }

    return dfs

# Função para obter a previsão do tempo
def get_weather(city):
    ''' Retorna o clima de uma cidade '''
    API_KEY = os.getenv('APITEMPO')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    print(response)
    data = response.json()
    if response.status_code == 200:
        weather = {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
        }
        return weather
    else:
        return None


def main_calculate(usina, period, start_date, end_date, potencia_max=2.5):
    ''' gerencia o cálculo de produção e eficiência '''

    try:
        # 1 passo: sanitizar os argumentos
        period_get = {'h': 1, 'D': 30, 'W': '1W', 'M': '1M', 'Y': '1Y'}

        # 2 passo: definir o formato das usinas para dividir os valores
        format_usinas = {
                        'cgh_aparecida': [1, 1, 405.5],
                        'cgh_fae': [1, 1, 7224],
                        'cgh_frozza': [1, 1, 455.782],
                        'cgh_granada': [1, 1000, 30594],
                        'cgh_maria_luz':[1, 1000, 1580],
                        'cgh_parisoto':[1, 1, 1],
                        'cgh_ponte_caida': [1, 1, 32743],
                        'cgh_ponte_serrada': [1, 1, 1],
                        'cgh_sebastiao_paz_almeida': [1,1, 1500],
        }

        # atualiza o valor da potencia máxima para o formato da usina
        potencia_max = potencia_max * format_usinas[usina][1]

        if start_date is None:
            # 3 passo: estabelecer o período de busca
            data_init = (pd.Timestamp.now() - pd.Timedelta(days=period_get.get(period, 1))).strftime('%Y-%m-%d %H:%M:%S')
            data_end = (pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')
        else:
            data_init = start_date.strftime('%Y-%m-%d %H:%M:%S')
            data_end = end_date.strftime('%Y-%m-%d %H:%M:%S')

        # 4 passo: buscar os dados
        dados = get_datas(usina, data_init, data_end)

        # 5 passo: verificar se há dados
        data = {}
        if dados.shape[0] == 0:
            data[usina] = pd.DataFrame()
            return data

        # 6 passo: setar a data_hora como index
        dados.set_index('data_hora', inplace=True)

        # 7 passo: separar as colunas que contém energia e nível de água
        column_nivel_agua = [column for column in dados.columns if ('nivel_agua' in column.lower() or
                                                                    'nivel_jusante' in column.lower())]
        column_nivel_montante = [column for column in dados.columns if 'nivel_montante' in column.lower()]
        column_energia = [column for column in dados.columns if 'acumulador_energia' in column.lower()]
        energia = dados[column_energia]
        nivel_agua = dados[column_nivel_agua]
        nivel_montante = dados[column_nivel_montante]

        # 8 passo: somar as colunas de energia
        # potencia_atual= energia.sum(axis=1)
        potencia_atual = potencia_atual.to_frame()
        potencia_atual.columns = ['potencia_atual']

        # 9 passo: Potencia maxima está definida, definir o nível de água máximo
        nivel_max = nivel_agua.max() #format_usinas[usina][2]

        # 10 passo: resample para o período desejado
        potencia_atual = calculate_production(potencia_atual, 'potencia_atual', period)

        # 11 passo: resample para o período desejado para o nível de água
        # nivel_agua = nivel_agua.resample(period).mean()
        # nivel_montante = nivel_montante.resample(period).mean()


        # 12 passo: calcular a eficiência Eficiência[i] = (potencia_atual[i] / potencia_max) / (nivel_atual[i] / nivel_max)
        A1 = potencia_atual / potencia_max
        A2 = nivel_agua / nivel_max

        # 13 passo: Substitui valores nulos ou 0 por 1 em A1
        A2 = A2.replace(0, 1)
        A2 = A2.fillna(1)

        # 12 passo:  Merge A1 e A2 com base no índice comum
        merged_df = A1.merge(A2, left_index=True, right_index=True)

        # 13 passo: Dividir os valores de A1 pelos valores de A2
        eficiencia = merged_df['potencia_atual_p'].div(merged_df[column_nivel_agua[0]])
        # eficiencia = A1

        # 14 passo: Transformar a série em um DataFrame
        if isinstance(eficiencia, pd.Series):
            eficiencia = eficiencia.to_frame()
        eficiencia.columns = ['eficiencia']


        # 14 passo: Exibir o DataFrame resultante
        # print(eficiencia.head())
        # print(eficiencia.shape)

        # merge com potencia_atual
        eficiencia = eficiencia.merge(potencia_atual, left_index=True, right_index=True)
        # eficiencia = eficiencia.merge(nivel_agua, left_index=True, right_index=True)
        nivel = nivel_agua.merge(nivel_montante, left_index=True, right_index=True)

        data[usina]['energia'] = eficiencia
        data[usina]['nivel'] = nivel

        return data
    except Exception as e:
        raise Exception(f' main_calculate ->: {e}')


def get_ranking(period='2min',start_date=None, end_date=None):
    ''' Retorna o ranking das usinas '''
    try:
        inicio = time.time()
        print('----' * 10)
        print('111- ', start_date, end_date)
        print('----' * 10)
        usina = 'cgh_aparecida'
        potencia_max = 2.5
        data = main_calculate(usina, period, start_date, end_date, potencia_max)  # consulta os dados para o período
        yield data
    except Exception as e:
        raise Exception(f'Erro ao buscar o ranking: {e}')


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



