from mysql.connector import Error
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
import os
import time

load_dotenv()

senhas = {
            'remote': {
                'host': os.getenv('MYSQLHOST'),
                'user': os.getenv('MYSQLUSER'),
                'password': os.getenv('MYSQLPASSWORD'),
                'database': os.getenv('MYSQLDATABASE'),
                'port': os.getenv('MYSQLPORT'),
                'token': 'Bearer '
            },
            'local': {
                'host': os.getenv('MYSQLHOST_LOCAL'),
                'user': os.getenv('MYSQLUSER_LOCAL'),
                'password': os.getenv('MYSQLPASSWORD_LOCAL'),
                'database': os.getenv('MYSQLDATABASE_LOCAL'),
                'port': os.getenv('MYSQLPORT_LOCAL'),
                'token': 'Bearer '
            }
}

class Database:
    ''' Classe para gerenciar a conexão com o banco de dados '''
    def __init__(self):
        ''' Inicializa a classe de conexão com o banco de dados '''
        choice_db = 'remote'

        # Obter as variáveis de ambiente
        self.host = senhas[choice_db]['host']
        self.user = senhas[choice_db]['user']
        self.password = senhas[choice_db]['password']
        self.database = senhas[choice_db]['database']
        self.port = senhas[choice_db]['port']
        self.token = senhas[choice_db]['token']
        self.connection = None

    def __enter__(self):
        ''' Inicia a conexão com o banco de dados '''

        # Conectar ao banco de dados
        self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Fecha a conexão com o banco de dados '''

        # Fechar a conexão com o banco de dados
        self.close()

    def connect(self):
        ''' Conecta ao banco de dados '''

        try:
            # Conectar ao banco de dados através do conector mysql e as variáveis de ambiente
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                use_pure=True,
                connection_timeout=30
            )

        except Exception as e:
            raise Exception("Erro ao conectar ao banco de dados")

    def ensure_connection(self):
        ''' Garante que a conexão com o banco de dados está ativa '''

        # Verificar se a conexão está ativa
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def insert_data(self, table, data: pd.DataFrame):
        ''' Insere dados em uma tabela do banco de dados '''

        try:
            # Garantir que a conexão com o banco de dados está ativa
            self.ensure_connection()

            # Criar um cursor para executar a query
            cursor = self.connection.cursor(buffered=True)

            # Inserir os dados na tabela
            for index, row in data.iterrows():
                if index > 10:
                    query = f"INSERT INTO {table} ({','.join(data.columns)}) VALUES ({','.join(['%s']*len(data.columns))})"
                    cursor.execute(query, tuple(row))
                    self.connection.commit()
                    print(f"Inserting row {index} in table {table}")
                    print(f"Query: {query}")
                    print(f"Values: {tuple(row)}")
                    print('-'*50)
                    time.sleep(0.01)


        except Exception as e:
            raise Exception(f"Erro ao inserir dados na tabela {table} {e}")

    def execute_query(self, query, params=None):
        ''' Executa uma query no banco de dados '''

        try:
            # Garantir que a conexão com o banco de dados está ativa
            self.ensure_connection()

            # Criar um cursor para executar a query
            cursor = self.connection.cursor(buffered=True)

            # Executar a query
            cursor.execute(query, params or ())

            # Commitar a query
            self.connection.commit()

            return cursor

        except Exception as e:
            raise Exception(f"Erro ao executar query {e}")

    def fetch_all(self, query, params=None)->pd.DataFrame:
        ''' Busca todos os dados de uma query '''

        try:
            # Executar a query
            cursor = self.execute_query(query, params)

            # Obter os nomes das colunas do cursor
            columns = cursor.column_names

            # inverter o nome das colunas
            columns = [self.reverse_rename(col) for col in columns]

            # Obter todos os dados
            result = cursor.fetchall()

            # Criar um DataFrame com os dados e as colunas
            df = pd.DataFrame(result, columns=columns)

            #converter a coluna data_hora para datetime
            if 'data_hora' in df.columns:
                df['data_hora'] = pd.to_datetime(df['data_hora'])

            return df

        except Exception as e:
            raise Exception(f"Erro ao executar query {e}")

    def close(self):
        ''' Fecha a conexão com o banco de dados '''

        try:
            # Verificar se a conexão está ativa e fechar
            if self.connection and self.connection.is_connected():
                self.connection.close()

        except Exception as e:
            raise Exception(f"Erro ao fechar conexão {e}")


    def reverse_rename(self, abbr):
        '''Inverte o nome das colunas'''

        try:
            # Mapeamento dos nomes das colunas
            mapping = {
                'id': 'id',
                '101s': 'ug01_status',
                '201ae': 'ug01_acumulador_energia',
                '301na': 'ug01_nivel_agua',
                '401tfA': 'ug01_tensao_fase_A',
                '501tfB': 'ug01_tensao_fase_B',
                '601tfC': 'ug01_tensao_fase_C',
                '701cfA': 'ug01_corrente_fase_A',
                '801cfB': 'ug01_corrente_fase_B',
                '901cfC': 'ug01_corrente_fase_C',
                '1001te': 'ug01_tensao_excitacao',
                '1101ce': 'ug01_corrente_excitacao',
                '1201f': 'ug01_frequencia',
                '1301pa': 'ug01_potencia_ativa',
                '1401pr': 'ug01_potencia_reativa',
                '1501pa': 'ug01_potencia_aparente',
                '1601f': 'ug01_fp',
                '1701d': 'ug01_distribuidor',
                '1801v': 'ug01_velocidade',
                '1901hm': 'ug01_horimetro_mecanico',
                '2001he': 'ug01_horimetro_eletrico',
                '2101teA': 'ug01_temp_enrol_A',
                '2201teB': 'ug01_temp_enrol_B',
                '2301teC': 'ug01_temp_enrol_C',
                '2401tme': 'ug01_temp_mancal_estat',
                '2501tmc': 'ug01_temp_mancal_comb',
                '2601tme': 'ug01_temp_mancal_escora',
                '2701tou': 'ug01_temp_oleo_uhrv',
                '2801tou': 'ug01_temp_oleo_uhlm',
                '2901tc': 'ug01_temp_csu2',
                '3001te': 'ug01_temp_excitatriz',
                '3101vmgx': 'ug01_vibr_mancal_guia_x',
                '3201vmgY': 'ug01_vibr_mancal_guia_Y',
                '3301vmcX': 'ug01_vibr_mancal_comb_X',
                '3401vmcY': 'ug01_vibr_mancal_comb_Y',
                '3501vmcZ': 'ug01_vibr_mancal_comb_Z',
                '3601clA': 'ug01_corrente_linha_A',
                '3701clB': 'ug01_corrente_linha_B',
                '3801clC': 'ug01_corrente_linha_C',
                '3901csP': 'ug01_corrente_seq_P',
                '4001csN': 'ug01_corrente_seq_N',
                '4101csZ': 'ug01_corrente_seq_Z',
                '4201tb': 'ug01_tensao_barra',
                '4301tt': 'ug01_tensao_te',
                '4402s': 'ug02_status',
                '4502ae': 'ug02_acumulador_energia',
                '4602tfA': 'ug02_tensao_fase_A',
                '4702tfB': 'ug02_tensao_fase_B',
                '4802tfC': 'ug02_tensao_fase_C',
                '4902cfA': 'ug02_corrente_fase_A',
                '5002cfB': 'ug02_corrente_fase_B',
                '5102cfC': 'ug02_corrente_fase_C',
                '5202te': 'ug02_tensao_excitacao',
                '5302ce': 'ug02_corrente_excitacao',
                '5402f': 'ug02_frequencia',
                '5502pa': 'ug02_potencia_ativa',
                '5602pr': 'ug02_potencia_reativa',
                '5702pa': 'ug02_potencia_aparente',
                '5802f': 'ug02_fp',
                '5902d': 'ug02_distribuidor',
                '6002v': 'ug02_velocidade',
                '6102hm': 'ug02_horimetro_mecanico',
                '6202he': 'ug02_horimetro_eletrico',
                '6302teA': 'ug02_temp_enrol_A',
                '6402teB': 'ug02_temp_enrol_B',
                '6502teC': 'ug02_temp_enrol_C',
                '6602tme': 'ug02_temp_mancal_estat',
                '6702tmc': 'ug02_temp_mancal_comb',
                '6802tme': 'ug02_temp_mancal_escora',
                '6902tou': 'ug02_temp_oleo_uhrv',
                '7002tou': 'ug02_temp_oleo_uhlm',
                '7102tc': 'ug02_temp_csu2',
                '7202te': 'ug02_temp_excitatriz',
                '7302vmgx': 'ug02_vibr_mancal_guia_x',
                '7402vmgY': 'ug02_vibr_mancal_guia_Y',
                '7502vmcX': 'ug02_vibr_mancal_comb_X',
                '7602vmcY': 'ug02_vibr_mancal_comb_Y',
                '7702vmcZ': 'ug02_vibr_mancal_comb_Z',
                'data_hora': 'data_hora'
            }

            # busca o valor da chave correspondente
            valor = mapping.get(abbr, abbr)

            return valor
        except Exception as e:
            raise Exception(f'Error convert column {e}')