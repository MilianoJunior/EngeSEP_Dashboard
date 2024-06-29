'''
Qual o meu nível de experiência com design de interfaces?

Sou entusiasta em design de interfaces, sempre projeto minhas interfaces no figma. Uso layouts e depois crio os componentes.
Para mim, o design é o produto do conhecimento e aplicação de regras claras. Sempre acesso o Material Design do google para me inspirar
e acredito que cada detalhe é importante para o sucesso de um projeto.

Quais são os meus principais objetivos e metas com relação ao design de interfaces?

Meu objetivo é deixar claro as informações que desejo passar, quero usar componentes graficos que contenham informações
da evolução da unidade geradora, quais os pontos de falha, quais os pontos de sucesso, quero que o usuário consiga entender.
Vou usar o streamlit para criar um dashboard que contenha gráficos e tabelas que mostrem a evolução da unidade geradora.

O Ranking é uma forma muito intuitiva que pode gerar insights para o usuário, quero usar isso para mostrar a evolução da unidade geradora.

Qual feedback você tem recebido sobre o seu trabalho de design de interfaces?

Dividi a interface atual em 3 colunas, cada coluna apresenta uma informação diferente, a primeira coluna apresenta
um grafico de bar, a segunda apresenta metricas com setas, e a terceira apresenta o HAWKING, que é um modelo de IA que
conversa com o usuário e apresenta informações sobre a unidade geradora.
'''

'''

Os dados são de unidades geradoras de energia, onde cada tabela representa uma usina, as principais informações
que estão nas tabelas são:
    - Energia gerada
    - Velocidade da turbina;
    - Tensão das fases;
    - Corrente das fases;
    - Fator de potência;
    - Tensão de sincronismo;
    - Corrente de sincronismo;
    - Temperatura do gerador;
    - Temperatura do óleo das unidades: Lubrificação dos mancais e regulador de velocidade;
    - Pressão do óleo das unidades;
    - Nível do óleo das unidades;
    - Posição do Distribuidor;
Existem outras informações que fazem parte de cada unidade geradora que não são comuns a todas as usinas, dependendo
do tipo de unidade geradora.
Pretendo criar um indicador de energia gerada de acordo com a potência nominal da usina e a potência gerada, considerando
o nível de água do reservatório, a velocidade da turbina, a temperatura do gerador, a pressão do óleo, a temperatura do mancais
e outros fatores que influenciam na geração de energia.
Através do indicador de eficiência, vou criar um Raking das usinas que estão gerando mais energia. E ajustar
parametros que influenciam na geração de energia.
Os parâmetros que influenciam na geração de energia e são possíveis de ajustar são:

    - Ajuste da relação posicao do distribuidor x posição do rotor, quando a turbina for kaplan;

Pode me ajudar a criar esse indicador de eficiência e o ranking das usinas que estão gerando mais energia?
'''
'''
Considere a seguinte imagem em anexo, preciso criar uma caricatura desta imagem, preciso que ela seja realista com os
mesmos traços da imagem, mas que não seja uma cópia fiel, preciso que seja uma caricatura, que não seja engraçada
'''

'''
Os dados são de unidades geradoras de energia, onde cada tabela representa uma usina, as principais informações
que estão nas tabelas são:
    - Energia gerada
    - Velocidade da turbina;
    - Tensão das fases;
    - Corrente das fases;
    - Fator de potência;
    - Tensão de sincronismo;
    - Corrente de sincronismo;
    - Temperatura do gerador;
    - Temperatura do óleo das unidades: Lubrificação dos mancais e regulador de velocidade;
    - Pressão do óleo das unidades;
    - Nível do óleo das unidades;
    - Posição do Distribuidor;
    - Posição do Rotor;
    
Preciso otimizar o desempenho da usina, e melhorar a eficiência da geração de energia, para isso preciso ajustar
as variaveis que são possíveis de ajustar, como a relação entre a posição do distribuidor e a posição do rotor tenho
a seguinte relação (distribuidor, rotor) em valores percentuais, onde o rotor é a variável passiveis de ajuste:

dados_interpolacao = [[10.00, 3.00], [26.00,6.99],[35.00, 14.00],
                          [40.00, 18.01], [45.00,22.00],[50.00, 25.00],
                          [55.00, 28.00], [60.00,34.00],[65.00, 41.00],
                          [70.00, 45.00]]
                          
Verificando os seus resultados, percebi que não expliquei o suficiente sobre a relação entre a posição do distribuidor e a posição do rotor,
percebi usando o value_counts dos dados para essas duas variaveis que a relação programada via software possui atrasos quando é persistida
no banco de dados. Mas no final, preciso de uma nova tabela de dados de interpolacao que me ajude a encontrar a melhor relação para a geração
de energia.
                          
Pode me ajudar otimizar o desempenho da usina? 
                          

'''

'''
Por favor, em um primeiro momento vamos encontrar as variaveis que complementam melhor a performace do acumulador_energia,
se vc perceber, essa coluna contem o valor acumulado de energia gerada que está em MWh, a potencia máxima da usina é de 3.150 MWh,
fiz um resample com o pandas e tenhos os valores de energia gerada a cada 1 hora, vc pode fazer o mesmo e verificar que a eficiência
da usina está variando bastante, considerando a questão da água no qual a posição do distribuidor e a posição do rotor são variáveis
para manter o nivel jusante sempre constante, temos também outras possibilidades, mas se me ajudar a formular uma equação que
me ajude a encontrar a melhor relação entre essas variáveis, seria ótimo. Observe que quando o valor do distribuidor está muito baixo ou valores 
negativos, o valor percentual do rotor está proximo de 100%, isso significa que a turbina está com a comporta fechada e parada.
Eu tenho uma ideia para otimizar esses valores, mas pode me sugerir algo?

'''

'''
Tenho um csv que contem os dados de uma usina geradora de energia, os dados são de 1 em 1 minuto, e contem as seguintes colunas:

Variaveis preditoras:

'temp_uhlm_oleo', 'uhrv_pressao', 'temp_uhrv_oleo', 'distribuidor',
'velocidade', 'posicao_rotor', 'temp_manc_casq_comb',
'temp_manc_casq_esc', 'tensao_fase_A', 'tensao_fase_B', 'tensao_fase_C',
'corrente_fase_A', 'corrente_fase_B', 'corrente_fase_C',
'corrente_neutro', 'tensao_excitacao', 'corrente_excitacao',
'frequencia', 'potencia_ativa', 'potencia_reativa', 'potencia_aparente',
'fp', 'temp_enrol_A', 'temp_enrol_B', 'temp_enrol_C',
'temp_nucleo_estator_01', 'temp_nucleo_estator_02',
'temp_nucleo_estator_03', 'temp_tiristor_02', 'temp_tiristor_03',
'temp_crowbar_01', 'temp_crowbar_02', 'temp_transf_excitacao',
'temp_casq_rad_comb', 'temp_mancal_casq_guia', 'temp_mancal_cont_esc',
'nivel_montante', 'nivel_jusante', 'horimetro_eletrico',
'correnteL_fase_A', 'correnteL_fase_B', 'correnteL_fase_C', 'hora',
'dia', 'dif_acumulador_energia'

Variavel target:

'acumulador_energia'

Preciso encontrar uma rede neural que represente a geracão de energia, para encontrar a melhor relação entre a posição do distribuidor e a posição do rotor.


'''