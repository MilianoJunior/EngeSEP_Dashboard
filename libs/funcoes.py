# Importar as bibliotecas
from libs.database import Database
import pandas as pd

def get_datas(usina):
    ''' Retorna os valores de um período '''

    try:
        # query que retorna os ultimos 10 registros da tabela
        query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 20000'

        # criar uma conexão com o banco de dados
        with Database() as db:

            # retorna os valores da tabela
            return db.fetch_all(query)

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def get_columns(usina):
    ''' Retorna as colunas da tabela '''

    try:
        # query para retornar as colunas da tabela
        query = f'SHOW COLUMNS FROM {usina}'

        # criar uma conexão com o banco de dados
        with Database() as db:

            # retorna os valores da tabela
            return db.fetch_all(query)

    except Exception as e:
        raise Exception(f'Erro ao buscar as colunas: {e}')

def get_tables():
    ''' Retorna informações sobre as tabelas '''

    try:
        # query para retornar as tabelas do banco de dados
        query = 'SELECT * FROM Usinas'

        # criar uma conexão com o banco de dados
        with Database() as db:

            # retorna os valores da tabela
            return db.fetch_all(query)

    except Exception as e:
        raise Exception(f'Erro ao buscar as tabelas: {e}')

def calculate_production(df, column, period):
    '''Calcula a produção de energia corrigida para o período especificado de maneira ajustada.'''

    try:
        # converter a column para float
        df[column] = df[column].astype(float)

        # define o nome da coluna
        columnp = column + '_p'

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

        return df_resampled

    except Exception as e:
        raise Exception(f"Erro ao calcular a produção de energia {e}")

def calculate_efficiency(df, column, period):
    pass

def get_ranking(period='H'):
    ''' Retorna o ranking das usinas '''

    try:
        # busca informações sobre as usinas
        usinas = get_tables()

        print(usinas)

        # cria um DataFrame vazio
        df = pd.DataFrame(columns=['data hora','nome', 'producao','nível água', 'eficiência'])

        # para cada usina, busca as informações
        for index in range(0, usinas.shape[0]):

            # busca o nome da usina
            usina = usinas.loc[index, 'table_name']

            print('Usina:', usina)

            # busca as colunas da usina
            columns = get_columns(usina)

            print('Colunas:', columns)

            # separa as colunas que contém energia
            colunas = [column for column in columns['Field'].values if 'energia' in column.lower()]

            print('Colunas:', colunas)
            #
            # # busca as informações da usina e adiciona ao DataFrame
            # df_ranking = get_datas(usina)
            #

            #
            # # data hora como index
            # df_ranking.set_index('data_hora', inplace=True)
            #
            # # filtra as colunas que contém energia
            # df_ranking = df_ranking.loc[:, colunas]
            #
            # for column in df_ranking.columns:
            #     df_ranking = calculate_production(df_ranking, column, period)
            #     df['producao'] = df_ranking[columnp]
            #     return df

            # calcula a produção de energia

            return None

    except Exception as e:
        raise Exception(f'Erro ao buscar as tabelas: {e}')