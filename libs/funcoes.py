# Importar as bibliotecas
from libs.database import Database
import pandas as pd

def get_datas(usina,data_init, data_end):
    ''' Retorna os valores de um período '''

    try:
        query = f'SELECT * FROM {usina} WHERE data_hora BETWEEN "{data_init}" AND "{data_end}"'
        with Database() as db:                    # criar uma conexão com o banco de dados
            #  Faz a busca dos dados
            dados = db.fetch_all(query)

            # se não houver valores, retorna os últimos 20000 valores
            if dados.shape[0] == 0:
                query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 20000'   # query para retornar os valores da tabela
                return db.fetch_all(query)                                      # retorna os valores da tabela

            return dados          # retorna os valores da tabela

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

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

        return df_resampled

    except Exception as e:
        raise Exception(f"Erro ao calcular a produção de energia {e}")


def main_calculate(usina, period):
    ''' gerencia o cálculo de produção e eficiência '''

    # condicao do periodo
    period_get = {'H': 1, 'D': 30, 'W': '1W', 'M': '1M', 'Y': '1Y'}

    # dimunuir o periodo para buscar os dados
    data_init = (pd.Timestamp.now() - pd.Timedelta(days=period_get.get(period, 1))).strftime('%Y-%m-%d %H:%M:%S')
    data_end = (pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')

    # buscar os dados
    print('###################################### Buscar os dados ############################################')
    dados = get_datas(usina, data_init, data_end)
    print(usina, ' Data:', dados.shape)

    # separar as colunas que contém energia
    dados.set_index('data_hora', inplace=True)
    dados = dados[[column for column in dados.columns if 'energia' in column.lower()]]

    # calcular a produção de energia
    data = {}
    for s in dados.columns:
        if usina not in data:
            data[usina] = calculate_production(dados, s, period)
        else:
            data[usina] = pd.concat([data[usina], calculate_production(dados, s, period)], axis=1)
    return data

def get_ranking(period='h'):
    ''' Retorna o ranking das usinas '''

    try:
        usinas = get_tables()                           # busca as tabelas do banco de dados

        # cria um DataFrame vazio
        df = pd.DataFrame(columns=['data hora','nome', 'producao','nível água', 'eficiência'])

        for index in range(0, usinas.shape[0]):         # para cada usina, busca as informações
            usina = usinas.loc[index, 'table_name']     # busca o nome da usina
            data = main_calculate(usina, period)       # consulta os dados para o período

            yield data

        # return data
    except Exception as e:
        raise Exception(f'Erro ao buscar o ranking: {e}')