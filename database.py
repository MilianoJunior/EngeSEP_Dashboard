import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

class Database:

    def __init__(self):
        self.host = os.getenv('MYSQLHOST')
        self.user = os.getenv('MYSQLUSER')
        self.password = os.getenv('MYSQLPASSWORD')
        self.database = os.getenv('MYSQLDATABASE')
        self.port = os.getenv('MYSQLPORT')
        # print(f"host: {self.host}, user: {self.user}, password: {self.password}, database: {self.database}, port: {self.port}")
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _handle_error(self, err_msg, exception):
        full_msg = f"class Database: {err_msg}: {exception}"
        print(full_msg)
        raise Exception(full_msg)

    def _debug(self, msg):
        if os.getenv('DEBUG') == 'True':
            if 'new' in msg:
                print(f"{'-' * 20} {msg} {'-' * 20}")
            else:
                print(msg)

    def connect(self):
        try:
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
            self._handle_error("Erro ao conectar ao banco de dados", e)

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def execute_query(self, query, params=None):
        try:
            self._debug(f"Executando query: {query}, params: {params}")
            self.ensure_connection()
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Exception as e:
            self._handle_error("Erro ao executar query", e)

    def fetch_all(self, query, params=None):
        try:
            cursor = self.execute_query(query, params)
            # Obter os nomes das colunas do cursor
            columns = cursor.column_names
            # inverter o nome das colunas
            columns = [self.reverse_rename(col) for col in columns]
            # Obter todos os dados
            result = cursor.fetchall()
            # Criar um DataFrame com os dados e as colunas
            df = pd.DataFrame(result, columns=columns)
            self._debug(f"Resultado dados: {df}")
            return df
        except Exception as e:
            self._handle_error("Erro ao buscar todos os dados", e)

    def close(self):
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("Conexão com o banco de dados encerrada!")
        except Exception as e:
            self._handle_error("Erro ao fechar conexão", e)


    def reverse_rename(self, abbr):
        try:
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
            valor = mapping.get(abbr, abbr)
            return valor
        except Exception as e:
            self.error(e)