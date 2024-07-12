
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import tensorflow as tf
# Importa o modelo de rede neural
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import requests
import json
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import Callback
from sklearn.model_selection import train_test_split
from keras import regularizers
import time
import random
from scipy.interpolate import interp1d
from libs.database import Database
import streamlit as st


def time_decorator(func):
    ''' Decorator para calcular o tempo de execução de uma função '''

    global data_hoje, path_data, name_plant
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resposta =  func(*args, **kwargs)
        name_function = func.__name__
        print(f'{name_function}: Tempo de execução: {round(time.time() - inicio, 8)} segundos')
        return resposta

    return wrapper

@time_decorator
def search_file_csv():
    ''' Procura um arquivo csv no diretório data que seja o mais recente '''

    files = os.listdir(path_data)
    for file in files:
        if file.endswith('.csv') and data_hoje in file:
            return file

    return None

@time_decorator
def download_data():
    ''' Busca os dados de uma usina no banco de dados atualizados '''
    try:
        file = search_file_csv()                        # buscar o arquivo csv mais recente

        if file is not None:
            query = f'SELECT * FROM {name_plant}'
            with Database() as db:                      # criar uma conexão com o banco de dados
                dados = db.fetch_all(query)

                name_file = os.path.join(os.getcwd(), 'data', f'{usina}_{data_hoje}.csv')
            # dados.to_csv(path, index=False)
        #
        # return path

    except Exception as e:
        raise Exception(f'Erro ao buscar os dados: {e}')

def salvar_modelo(model, path):
    ''' Salva o modelo treinado em um arquivo '''

    try:
        # Salva o modelo em um arquivo
        model.save(path)

    except Exception as e:
        raise Exception(f'Erro ao salvar o modelo: {e}')

def carregar_modelo(path):
    ''' Carrega um modelo treinado de um arquivo '''

    try:
        # Carrega o modelo do arquivo
        model = tf.keras.models.load_model(path)

        return model

    except Exception as e:
        raise Exception(f'Erro ao carregar o modelo: {e}')

def mostrar_pesos(model):
    ''' Mostra os pesos das camadas de um modelo '''

    try:
        # Mostra os pesos das camadas
        for layer in model.layers:
            print(layer.get_weights())

    except Exception as e:
        raise Exception(f'Erro ao mostrar os pesos: {e}')


def redes_neurais(X, Y, nr):
    ''' Treina uma rede neural com os dados de entrada X e saída Y '''

    model = MLPRegressor(hidden_layer_sizes=(1000, 1000),
                         activation='relu',
                         solver='adam',
                         max_iter=10000,
                         random_state=42)

    # Treina o modelo
    model.fit(X.values, Y.values.ravel())

    return model

def preparar_dados(df):
    ''' Prepara os dados para treinamento do modelo '''

    variavel_predicao = 'potencia_ativa'

    # excluir colunas com mais de 50% de valores nulos e valores conferidos manualmente
    df = df[df['distribuidor'] > 0]
    df = df[df['uhrv_pressao'] > 95]
    df = df[df['tensao_excitacao'] < 200]
    df = df[df['tensao_excitacao'] > 0]
    df = df[df['corrente_excitacao'] > 0]  # 28934
    df = df[df['frequencia'] < 6200]  # 28934
    df = df[df['potencia_reativa'] > -500]  # 28988
    df = df[df['fp'] > 90]  # 28988
    df = df[df['temp_casq_rad_comb'] > 30]  # 28962
    df = df[df['nivel_montante'] > 402]  # 28988
    df = df[df['distribuidor'] > 0]
    df = df[df['posicao_rotor'] != 99]
    df = df[df['posicao_rotor'] != 98]
    df = df[df['posicao_rotor'] < 100]

    # excluir colunas com mais de 50% de valores nulos
    df_ = df[df == 0].count()
    df_ = df_[df_ > len(df) * 0.5]
    df = df.drop(columns=df_.index)

    # transformar a coluna data_hora em datetime
    df['data_hora'] = pd.to_datetime(df['data_hora'])

    # transformar a coluna data_hora em senoidal
    df['hora'] = np.sin(2 * np.pi * df['data_hora'].dt.hour / 24)
    df['dia'] = np.sin(2 * np.pi * df['data_hora'].dt.day / 30)

    # excluir colunas desnecessárias
    colunas_remover = ['data_hora','id', 'corrente_neutro', 'temp_tiristor_01']
    df.drop(columns=colunas_remover, inplace=True)

    # reseta o index
    df.reset_index(drop=True, inplace=True)

    # criar uma cópia do DataFrame
    df_copy = df.copy()

    # normalizar os dados
    df_copy, scalers = normalize_data(df_copy, list(df_copy.columns))

    # dividir os dados em X e Y
    Y = df.pop(variavel_predicao).to_frame()
    X = df

    # dividir os dados em X_norm e Y_norm normalizados para treinamento
    Y_norm = df_copy.pop(variavel_predicao).to_frame()
    X_norm = df_copy

    dados = {
        'X': X,
        'Y': Y,
        'X_norm': X_norm,
        'Y_norm': Y_norm,
        'scalers': scalers,
        'df': df
    }

    return dados

def normalize_data(df, column_names):
    ''' Normaliza os dados de um DataFrame '''
    scalers = {}
    for column in column_names:
        scaler = MinMaxScaler(feature_range=(0, 1))
        df[column] = scaler.fit_transform(df[[column]])
        scalers[column] = scaler
    return df, scalers


def desnormalize_data(df, column_names, scalers):
    ''' Desnormaliza os dados de um DataFrame '''
    for column in column_names:
        df[column] = scalers[column].inverse_transform(df[[column]])

    return df

class PrintCallback(Callback):
    def __init__(self, training_data):
        super(PrintCallback, self).__init__()
        self.training_data = training_data

    def on_epoch_end(self, epoch, logs=None):
        ''' Função chamada ao final de cada época '''

        # Obtendo dados de treinamento
        x, y, scalers, nr, objeto_progress = self.training_data

        # Obtendo previsões do modelo
        predictions = self.model.predict(x)

        # transformando os dados em um numpy array
        expected = y.to_numpy()

        # Desnormalizando os dados
        predictions = scalers['potencia_ativa'].inverse_transform(predictions)

        # Calculando o erro
        error = np.abs(expected - predictions).mean()

        # Imprimindo média do erro
        total = round(epoch/nr,2)

        objeto_progress.progress(total, text=f'Epoch {epoch + 1}, Mean Error: {round(error)}')

        # Imprimindo média do erro
        i = len(expected) - 1
        print('_' * 50)
        print(f'Previsto: {predictions[i][0]}, Esperado: {expected[i][0]}, Erro: {np.abs(expected[i][0] - predictions[i][0])}')
        print(f'\nEpoch {epoch + 1}, Mean Error: {error}\n, Total: {total}%\n')

def redes_neurais_tf(X_norm, Y_norm, X, Y, nr, scalers, learning_rate=0.0001):
    ''' Treina uma rede neural com os dados de entrada X e saída Y usando TensorFlow '''

    # Configuração da semente aleatória para reprodutibilidade
    tf.random.set_seed(42)
    np.random.seed(42)

    neurons1 = random.randint(100, 10000)
    neurons2 = random.randint(100, 10000)
    activation1 = random.choice(['relu', 'tanh', 'sigmoid', 'linear','softmax','softplus','softsign','selu','elu','exponential'])
    activation2 = random.choice(
        ['relu', 'tanh', 'sigmoid', 'linear', 'softmax', 'softplus', 'softsign', 'selu', 'elu', 'exponential'])

    optimizer_name = random.choice(['adam', 'sgd', 'rmsprop', 'adadelta', 'adagrad', 'adamax', 'nadam', 'ftrl'])
    learning_rate = round(random.uniform(0.0001, 0.1),4)

    # Dividindo os dados em conjuntos de treinamento e teste
    neurons1 = 10000
    neurons2 = 5000
    activation1 = 'relu'
    activation2 = 'relu'
    learning_rate = 0.001
    epochs = 100
    optimizer_name = 'adam'

    with tf.device('/device:GPU:0'):

        # Criação do modelo sequencial
        model = Sequential()

        model.add(Dense(neurons1, activation=activation1, input_shape=(X.shape[1],))) # L2 regularization for biases
        model.add(Dense(neurons2, activation=activation2))  # L2 regularization for biases

        model.add(Dense(neurons2, activation=activation2))

        # Adicionando a camada de saída
        model.add(Dense(1, activation='linear'))

        # Selecionando o otimizador com a taxa de aprendizagem personalizada
        if optimizer_name == 'adam':
            optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        elif optimizer_name == 'sgd':
            optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
        elif optimizer_name == 'rmsprop':
            optimizer = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
        elif optimizer_name == 'adadelta':
            optimizer = tf.keras.optimizers.Adadelta(learning_rate=learning_rate)
        elif optimizer_name == 'adagrad':
            optimizer = tf.keras.optimizers.Adagrad(learning_rate=learning_rate)
        elif optimizer_name == 'adamax':
            optimizer = tf.keras.optimizers.Adamax(learning_rate=learning_rate)
        elif optimizer_name == 'nadam':
            optimizer = tf.keras.optimizers.Nadam(learning_rate=learning_rate)
        elif optimizer_name == 'ftrl':
            optimizer = tf.keras.optimizers.Ftrl(learning_rate=learning_rate)
        else:
            optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

        # Compilando o modelo
        model.compile(optimizer=optimizer, loss='mean_absolute_error')

        objeto_progress = st.empty()

        print('##################' * 5)
        print(f'Epochs: {nr} - Configuração escolhida: Neurons1={neurons1}, Activation1={activation1}, Neurons2={neurons2}, Activation2={activation2}, Optimizer={optimizer_name}, Learning Rate={learning_rate}')
        print('##################' * 5)
        print(model.summary())

        # treinanmento do modelo
        model.fit(X_norm, Y_norm, epochs=nr, batch_size=32, verbose=0, callbacks=[PrintCallback((X_norm, Y, scalers, nr, objeto_progress))])

        objeto_progress = st.empty()


    return model

def equacao(x, y):
    ''' Cria uma equação de interpolação '''

    interpolacao = interp1d(x, y, kind='linear')

    return interpolacao

def plot_interpolation1(df1):
    ''' Plota a interpolação de uma linha de dados '''

    # Cria uma nova figura
    fig = go.Figure()

    # Adiciona a linha de interpolação ao gráfico com cor azul
    fig.add_trace(go.Scatter(x=df1['distribuidor'], y=df1['posicao_rotor'], mode='lines', name='Distribuidor X Rotor', line=dict(color='blue'), text=df1['distribuidor']))

    # Atualiza o layout do gráfico
    fig.update_layout(xaxis_title='Distribuidor ', yaxis_title='Posição do Rotor', showlegend=True)

    # Altera o grid do gráfico e retira o título
    fig.update_xaxes(nticks=20)  # Aumenta o número de linhas de grade no eixo x
    fig.update_yaxes(nticks=20)  # Aumenta o número de linhas de grade no eixo y

    return fig

def plot_graph(df):
    ''' Plota a interpolação de uma linha de dados '''

    # Cria uma nova figura
    fig = go.Figure()

    df['data_hora'] = pd.to_datetime(df['data_hora'])

    # Adiciona a linha de interpolação ao gráfico com cor azul
    # fig.add_trace(go.Scatter(x=df['data_hora'], y=df['potencia_ativa'], mode='line', name='Potência Ativa', line=dict(color='blue')))
    fig.add_trace(go.Bar(x=df['data_hora'], y=df['potencia_ativa'], name='Potência Ativa'))

    # Atualiza o layout do gráfico
    fig.update_layout(xaxis_title='Tempo', yaxis_title='Potência Ativa', showlegend=True)

    # Altera o grid do gráfico e retira o título
    fig.update_xaxes(nticks=20)  # Aumenta o número de linhas de grade no eixo x
    fig.update_yaxes(nticks=20)  # Aumenta o número de linhas de grade no eixo y

    return fig



@time_decorator
def executor():
    ''' Função principal'''
    # path =download_data()

    query = f'SELECT * FROM cgh_fae'
    with Database() as db:  # criar uma conexão com o banco de dados
        dados = db.fetch_all(query)

    qtd = dados.shape[0]

    dados = dados[dados == 0].count()

    df = pd.DataFrame(columns=['column', 'valores', 'perct'])

    cont = 0

    for i in dados.index:

        print(cont,i, dados[i], qtd)
        df.loc[cont, 'column'] = i
        df.loc[cont, 'valores'] = dados[i]
        df.loc[cont, 'perct'] = (dados[i] / qtd) * 100
        cont += 1
        # dados['perct'] = (dados[i] / len(dados)) * 100

    df.sort_values(by='perct', ascending=False, inplace=True)
    # st.write(dados.index)

    # # Suponha que 'dados' é o seu DataFrame e 'valores' é a coluna que você quer calcular o percentual
    # total = dados['valores'].sum()
    # dados['percentual'] = dados['valores'].apply(lambda x: (x / total) * 100)
    #
    # dados = dados[dados > len(dados) * 0.5]

    st.dataframe(df, height=860)

    # st.dataframe(dados[:10])

    # fig = plot_graph(dados)
    #
    # st.plotly_chart(fig)

    return False
    variavel_predicao = 'potencia_ativa'

    if 'model' not in st.session_state:
        st.session_state.model = None

    # Criar colunas com tamanhos específicos
    col1, col2 = st.columns([.5, .5])

    # 1 passo : Carregar o dataset
    path = os.path.join(os.getcwd(), 'data', 'cgh_aparecida_2024-05-29.csv')
    df = pd.read_csv(path)

    # 2 passo: Preparar os dados
    dados = preparar_dados(df)

    X = dados['X']
    Y = dados['Y']
    X_norm = dados['X_norm']
    Y_norm = dados['Y_norm']
    scalers = dados['scalers']
    df = dados['df']

    # 3 passo: treinar o modelo
    with col1:

        # 3.1 - titulo
        st.write('**Dados de Treinamento**')

        media = Y[variavel_predicao].mean()
        # 3.2 - mostrar os dados de treinamento
        st.write('Quantidade de informações:', X.shape,
                 ' Media:', round(media,3), ' Data:', df.index.min(), ' - ', df.index.max())

        # Criar colunas com tamanhos específicos
        col11, col12, col13, col14 = st.columns([.5, .5, .5, .5])

        # Colocar o input na primeira coluna
        with col11:
            nr = st.number_input('Número loops:', min_value=1, max_value=1000, value=1, step=1)
        with col12:
            btn_treinar = st.button('Treinamento')
        with col13:
            btn_reset = st.button('Resetar parâmetros')
        with col14:
            btn_automatico = st.button('Busca automática')

        if btn_treinar:
            model = redes_neurais(X_norm, Y_norm, nr)
            st.session_state.model = model

        st.divider()

        # criar o titulo
        st.write('**Otimização da Posição do Rotor**')

        # # dados de interpolação
        dados_interpolacao = [[-1, -1], [10.00, 3.00], [26.00, 6.99], [35.00, 14.00],
                              [40.00, 18.01], [45.00, 22.00], [50.00, 25.00],
                              [55.00, 28.00], [60.00, 34.00], [65.00, 41.00],
                              [70.00, 45.00], [100.00, 100.00]]
        # # criar um DataFrame
        df_interpolacao = pd.DataFrame(dados_interpolacao, columns=['distribuidor', 'posicao_rotor'])
        valores_inter = {}

        # valores de interpolação
        valores_interpolacao = [f'col_{i}' for i in range(12)]

        # colunas
        col21, col22 = st.columns([.2, .2])

        for i, s in enumerate(valores_interpolacao):
            if i <= 5:
                with col21:
                    valores_inter[s] = st.slider(s, 0.0, 130.0, df_interpolacao['posicao_rotor'].values[i] ) #, on_change=prever(df, valores_inter))
            else:
                with col22:
                    valores_inter[s] = st.slider(s, 0.0, 130.0, df_interpolacao['posicao_rotor'].values[i]) #, on_change=prever(df, valores_inter))

        with col2:
            # otimizar a posição do rotor
            otimizador(df, valores_inter, st.session_state.model, X, Y, X_norm, Y_norm, scalers,automatico=btn_automatico, reset=btn_reset)

cont = 0

@time_decorator
def otimizador(df, valores_inter, model, X, Y, X_norm, Y_norm, scalers, variavel_predicao='potencia_ativa', automatico=False, reset=False):
    ''' Otimiza a posição do rotor '''

    global cont

    cont += 1
    chave = False
    maximo_valor = -1000
    inter = 0

    objeto_textob = st.empty()
    objeto_texto = st.empty()
    objeto_rotor = st.empty()
    objeto_dataframe = st.empty()
    df_x_ = None
    error_mean = 0

    distribuidor = [0.0, 10.0, 26.00, 35.00, 40.00, 45.00, 50.00, 55.00, 60.00, 65.00, 70.00, 100.00]

    posicao_rotor = list(valores_inter.values())

    if len(posicao_rotor) != len(distribuidor):
        print(cont, 'Não executa: ', cont, len(posicao_rotor), len(distribuidor))
        return False

    print(cont, 'Executa: ', cont, len(posicao_rotor), len(distribuidor))

    # if cont % 12 == 0:
    print(cont, '- Multiplo de 12: ', cont)
    # 1 passo: encontrar a equação de interpolação
    dados_interpolacao = list(zip(distribuidor, posicao_rotor))
    df_interpolacao = pd.DataFrame(dados_interpolacao, columns=['distribuidor', 'posicao_rotor'])
    interpolacao = equacao(df_interpolacao['distribuidor'], df_interpolacao['posicao_rotor'])

    # 2 passo: substituir a posição do rotor pelos dados da equação de interpolação
    X['posicao_rotor'] = interpolacao(df['distribuidor'])

    col31, col32 = st.columns([.3, .7])

    with col31:
        st.dataframe(df_interpolacao, height=460)

    with col32:
        fig = plot_interpolation1(df_interpolacao)
        st.plotly_chart(fig)

    if model is None:
        st.info('Treine o modelo antes de otimizar a posição do rotor')
        objeto_dataframe.dataframe(X_norm['posicao_rotor'].describe().to_frame().T)

        return False
    else:
        st.info('Modelo treinado')
        scala = MinMaxScaler(feature_range=(0, 1))
        X_norm['posicao_rotor'] = scala.fit_transform(X[['posicao_rotor']])
        scalers['posicao_rotor'] = scala
        objeto_dataframe.dataframe(X_norm['posicao_rotor'].describe().to_frame().T)
        Y_pred = st.session_state.model.predict(X_norm)
        Y_pred_desnormalized = desnormalize_data(pd.DataFrame(Y_pred, columns=[variavel_predicao]),
                                                 [variavel_predicao], scalers)
        Y_pred_desnormalized.rename(columns={variavel_predicao: f'{variavel_predicao}_pred'}, inplace=True)
        error = (Y[variavel_predicao] - Y_pred_desnormalized[f'{variavel_predicao}_pred'])
        error = error.to_frame()
        error.columns = ['error']

        # Calcular o erro médio
        error_mean = error['error'].mean()

        df_x = pd.concat([Y, Y_pred_desnormalized, error], axis=1)
        st.write('Erro Médio quadratico:', round(error_mean, 3))
        st.dataframe(df_x)

    print(cont, ' Posição do Rotor:', posicao_rotor, 'Tamanho:', len(posicao_rotor), 'Automatico: ', automatico, 'Reset:', reset)

    return True


