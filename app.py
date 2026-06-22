import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

# Centralizando o título principal do Dashboard
st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Análise Estratégica de Notas Fiscais, SLAs e Custos de Frete</p>", unsafe_allow_html=True)
st.markdown("---")

# --- CONSTRUÇÃO/MODIFICAÇÃO: Conexão e Carregamento dos Dados ---
def carregar_dados():
    conexao = sqlite3.connect("torre_controle_final.db")
    query = """
        SELECT 
            f.id_entrega,
            f.numero_nota_fiscal,
            t.nome_transportadora,
            c.nome_cliente,
            c.cidade,
            c.estado,
            c.regiao,
            f.segmento_operacao,
            f.data_emissao,
            f.data_previsao_entrega,
            f.data_entrega_real,
            f.valor_nota_fiscal,
            f.peso_kg,
            f.custo_frete_tabela,
            f.custo_frete_cobrado,
            f.status_entrega,
            f.motivo_gargalo
        FROM f_entregas f
        JOIN d_transportadoras t ON f.id_transportadora = t.id_transportadora
        JOIN d_clientes c ON f.id_cliente = c.id_cliente
    """
    df = pd.read_sql_query(query, conexao)
    conexao.close()
    
    # Convertendo colunas de data para o formato datetime
    df['data_emissao'] = pd.to_datetime(df['data_emissao'])
    return df

df_original = carregar_dados()

# --- CONSTRUÇÃO/MODIFICAÇÃO: Criação dos Filtros Dinâmicos na Barra Lateral ---
st.sidebar.header("🎯 Painel de Filtros Cruzados")

# Filtro 1: Segmento de Operação (Com opção 'Todos')
lista_segmentos = ["Todos"] + list(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Selecione o Segmento:", lista_segmentos)

# Filtro 2: Região de Destino (Com opção 'Todos')
lista_regioes = ["Todos"] + list(df_original["regiao"].unique())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", lista_regioes)

# Filtro 3: Status de Entrega (Com opção 'Todos')
lista_status = ["Todos"] + list(df_original["status_entrega"].unique())
status_selecionado = st.sidebar.selectbox("Status da Entrega:", lista_status)

# Filtro 4: Transportadora (Com opção 'Todos')
lista_transportadoras = ["Todos"] + list(df_original["nome_transportadora"].unique())
transportadora_selecionada = st.sidebar.selectbox("Transportadora:", lista_transportadoras)

# Aplicando a lógica dos filtros no DataFrame de visualização
df_filtrado = df_original.copy()

if segmento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento_operacao"] == segmento_selecionado]

if regiao_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["regiao"] == regiao_selecionada]

if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_entrega"] == status_selecionado]

if transportadora_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nome_transportadora"] == transportadora_selecionada]


# --- CONSTRUÇÃO/MODIFICAÇÃO: Seção de KPIs Principais (Cards de Topo) ---
st.subheader("📊 Indicadores de Performance Operacional")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_entregas = len(df_filtrado)
    st.metric(label="Total de Entregas (NFs)", value=f"{total_entregas}")

with col2:
    faturamento_frete = df_filtrado["custo_frete_cobrado"].sum()
    st.metric(label="Total Frete Cobrado", value=f"R$ {faturamento_frete:,.2f}")

with col3:
    # Cálculo do OTIF: Entregas No Prazo / Total de Entregas
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    st.metric(label="Taxa de OTIF (SLA)", value=f"{taxa_otif:.1f}%")

with col4:
    # Cálculo de Estouro de Frete: Onde o cobrado foi maior que o acordado em tabela
    df_filtrado["desvio_frete"] = df_filtrado["custo_frete_cobrado"] - df_filtrado["custo_frete_tabela"]
    prejuizo_frete = df_filtrado[df_filtrado["desvio_frete"] > 0]["desvio_frete"].sum()
    st.metric(label="Prejuízo (Frete Estourado)", value=f"R$ {prejuizo_frete:,.2f}")

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Seção Gráfica Gráficos Estratégicos ---
st.subheader("📈 Análise de Tendências e Volumetria")
graf1, graf2 = st.columns(2)

with graf1:
    # Gráfico 1: Evolução de Entregas por Região ao Longo do Tempo (Linhas)
    df_linha = df_filtrado.groupby(['data_emissao', 'regiao']).size().reset_index(name='qtd_entregas')
    df_linha = df_linha.sort_values(by='data_emissao')
    
    fig_linha = px.line(
        df_linha, 
        x='data_emissao', 
        y='qtd_entregas', 
        color='regiao',
        title="Evolução do Volume de Entregas por Região",
        labels={'data_emissao': 'Data de Emissão', 'qtd_entregas': 'Qtd Notas Fiscais'},
        markers=True
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with graf2:
    # Gráfico 2: Divisão de Status das Entregas (Rosca / Pizza)
    df_pizza = df_filtrado["status_entrega"].value_counts().reset_index()
    df_pizza.columns = ["Status", "Quantidade"]
    
    fig_pizza = px.pie(
        df_pizza, 
        names="Status", 
        values="Quantidade", 
        title="Distribuição por Status de Entrega",
        hole=0.4
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Tabela de Dados Operacionais e Detalhamento ---
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")

# Selecionando colunas chave para a exibição ficar limpa
colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", 
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]

# Exibindo a tabela formatada
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)