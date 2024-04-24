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
                query = f'SELECT * FROM {usina} ORDER BY id DESC LIMIT 200'   # query para retornar os valores da tabela
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

def calculate_production(df, column, period, usina):
    '''Calcula a produção de energia corrigida para o período especificado de maneira ajustada.'''

    try:
        format_usinas = {
            'cgh_aparecida': [1, 1],
            'cgh_fae': [1, 1000],
            'cgh_frozza': [1, 1],
            'cgh_granada': [1, 100],
            'cgh_maria_luz': [1, 100],
            'cgh_parisoto': [1, 1],
            'cgh_ponte_caida': [1, 100],
            'cgh_ponte_serrada': [1, 1],
            'cgh_sebastiao_paz_almeida': [1, 1],
        }

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



def main_calculate(usina, period, potencia_max=2.5):
    ''' gerencia o cálculo de produção e eficiência '''

    try:
        # 1 passo: sanitizar os argumentos
        period_get = {'h': 2, 'D': 30, 'W': '1W', 'M': '1M', 'Y': '1Y'}

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

        # 3 passo: estabelecer o período de busca
        data_init = (pd.Timestamp.now() - pd.Timedelta(days=period_get.get(period, 1))).strftime('%Y-%m-%d %H:%M:%S')
        data_end = (pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')

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
        potencia_atual= energia.sum(axis=1)
        potencia_atual = potencia_atual.to_frame()
        potencia_atual.columns = ['potencia_atual']

        # 9 passo: Potencia maxima está definida, definir o nível de água máximo
        nivel_max = nivel_agua.max() #format_usinas[usina][2]

        # 10 passo: resample para o período desejado
        potencia_atual = calculate_production(potencia_atual, 'potencia_atual', period, usina)

        # 11 passo: resample para o período desejado para o nível de água
        nivel_agua = nivel_agua.resample(period).mean()
        nivel_montante = nivel_montante.resample(period).mean()


        # 12 passo: calcular a eficiência Eficiência[i] = (potencia_atual[i] / potencia_max) / (nivel_atual[i] / nivel_max)
        A1 = potencia_atual / potencia_max
        # A2 = nivel_agua / nivel_max

        # 13 passo: Substitui valores nulos ou 0 por 1 em A1
        # A2 = A2.replace(0, 1)
        # A2 = A2.fillna(1)

        # 12 passo:  Merge A1 e A2 com base no índice comum
        # merged_df = A1.merge(A2, left_index=True, right_index=True)

        # 13 passo: Dividir os valores de A1 pelos valores de A2
        # eficiencia = merged_df['potencia_atual_p'].div(merged_df[column_nivel_agua[0]])
        eficiencia = A1

        # 14 passo: Transformar a série em um DataFrame
        if isinstance(eficiencia, pd.Series):
            eficiencia = eficiencia.to_frame()
        eficiencia.columns = ['eficiencia']


        # 14 passo: Exibir o DataFrame resultante
        # print(eficiencia.head())
        print(eficiencia.shape)

        # merge com potencia_atual
        eficiencia = eficiencia.merge(potencia_atual, left_index=True, right_index=True)
        eficiencia = eficiencia.merge(nivel_agua, left_index=True, right_index=True)
        eficiencia = eficiencia.merge(nivel_montante, left_index=True, right_index=True)

        data[usina] = eficiencia

        return data
    except Exception as e:
        raise Exception(f' main_calculate ->: {e}')


def get_ranking(period='2min'):
    ''' Retorna o ranking das usinas '''
    try:
        usina = 'cgh_aparecida'
        potencia_max = 2.5
        data = main_calculate(usina, period, potencia_max)  # consulta os dados para o período
        # usinas = get_tables()  # busca as tabelas do banco de dados
        #
        # data = {}  # Inicializa um dicionário vazio para armazenar os dados de todas as usinas
        #
        # for index in range(0, usinas.shape[0]):  # para cada usina, busca as informações
        #     usina = usinas.loc[index, 'table_name']  # busca o nome da usina
        #
        #     potencia_max = usinas.loc[index, 'potencia_instalada']
        #     data_usina = main_calculate(usina, period, potencia_max)  # consulta os dados para o período
        #     data.update(data_usina)  # Adiciona os dados da usina atual ao dicionário de dados
        #     print(f'Progresso: {index / usinas.shape[0]}')
        #     yield index / usinas.shape[0]
        #
        # medias = {}
        # for key, usina in data.items():
        #     if not usina.empty:
        #         medias[key] = usina['eficiencia'].mean()

        # print(medias)
        # # ordena o dicionário de dados com base na média da eficiência
        #
        # print(data)
        # print(type(data))

        #     print(usina, data[usina].shape)
        # # Calcula a média da eficiência para cada usina e ordena o dicionário de dados com base na média da eficiência
        # data = {usina: df for usina, df in
        #         sorted(data.items(), key=lambda item: item[1]['eficiencia'].mean() if 'eficiencia' in item[1].columns and not item[1].empty else float('-inf'), reverse=True)}

        yield data
    except Exception as e:
        raise Exception(f'Erro ao buscar o ranking: {e}')

# def get_ranking(period='h'):
#     ''' Retorna o ranking das usinas '''
#     try:
#         usinas = get_tables()  # busca as tabelas do banco de dados
#
#         # cria um DataFrame vazio
#         df = pd.DataFrame(columns=['data hora', 'nome', 'producao', 'nível água', 'eficiência'])
#
#         data = {}  # Inicializa um dicionário vazio para armazenar os dados de todas as usinas
#
#         for index in range(0, usinas.shape[0]):  # para cada usina, busca as informações
#             usina = usinas.loc[index, 'table_name']  # busca o nome da usina
#             # get_max_nivel(usina)
#
#             potencia_max = usinas.loc[index, 'potencia_instalada']
#             data_usina = main_calculate(usina, period, potencia_max)  # consulta os dados para o período
#             data.update(data_usina)  # Adiciona os dados da usina atual ao dicionário de dados
#
#         # Calcula a média da eficiência para cada usina e ordena o dicionário de dados com base na média da eficiência
#         data = {usina: df for usina, df in
#                 sorted(data.items(), key=lambda item: item[1]['eficiencia'].mean(), reverse=True)}
#
#         return data
#     except Exception as e:
#         raise Exception(f'Erro ao buscar o ranking: {e}')

    # try:
    #     usinas = get_tables()                           # busca as tabelas do banco de dados
    #
    #     # cria um DataFrame vazio
    #     df = pd.DataFrame(columns=['data hora','nome', 'producao','nível água', 'eficiência'])
    #     percent = usinas.shape[0]
    #
    #     for index in range(0, usinas.shape[0]):         # para cada usina, busca as informações
    #         usina = usinas.loc[index, 'table_name']     # busca o nome da usina
    #         # get_max_nivel(usina)
    #
    #         potencia_max = usinas.loc[index, 'potencia_instalada']
    #         data = main_calculate(usina, period, potencia_max)       # consulta os dados para o período
    #         data.update(data_usina)  # Adiciona os dados da usina atual ao dicionário de dados
    #
    #         # retorna o progresso
    #         yield index / percent
    #
    #     # Calcula a média da eficiência para cada usina e ordena o dicionário de dados com base na média da eficiência
    #     data = {usina: df for usina, df in
    #             sorted(data.items(), key=lambda item: item[1]['eficiencia'].mean(), reverse=True)}
    #
    #
    #
    #     return data
    # except Exception as e:
    #     raise Exception(f'Erro ao buscar o ranking: {e}')