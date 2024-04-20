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