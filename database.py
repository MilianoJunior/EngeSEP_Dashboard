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
        print(f"host: {self.host}, user: {self.user}, password: {self.password}, database: {self.database}, port: {self.port}")
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
                connection_timeout=300
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