import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Solução Gerencial: Auditoria Automática de Fretes, Análise de SLA e Controle de Metas</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================
# CRIA O BANCO DE DADOS DIRETAMENTE NO APP
# ============================================
DB_PATH = "torre_controle.db"

def criar_banco():
    """Cria o banco de dados do zero"""
    
    # Remove banco antigo se existir
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    # Cria tabelas
    cursor.execute("DROP TABLE IF EXISTS f_entregas;")
    cursor.execute("DROP TABLE IF EXISTS d_transportadoras;")
    cursor.execute("DROP TABLE IF EXISTS d_clientes;")

    cursor.execute("""
        CREATE TABLE d_transportadoras (
            id_transportadora INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_transportadora TEXT NOT NULL,
            tipo_transporte TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE d_clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL,
            cidade TEXT,
            estado TEXT,
            regiao TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE f_entregas (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_nota_fiscal TEXT NOT NULL,
            id_transportadora INTEGER,
            id_cliente INTEGER,
            segmento_operacao TEXT,
            data_emissao TEXT,
            data_previsao_entrega TEXT,
            data_entrega_real TEXT,
            valor_nota_fiscal REAL,
            peso_kg REAL,
            custo_frete_tabela REAL,
            custo_frete_cobrado REAL,
            status_entrega TEXT,
            motivo_gargalo TEXT,
            FOREIGN KEY (id_transportadora) REFERENCES d_transportadoras(id_transportadora),
            FOREIGN KEY (id_cliente) REFERENCES d_clientes(id_cliente)
        );
    """)

    # Transportadoras
    transportadoras = [
        ("Alfa Transportes", "Lotação"),
        ("Beta Logística", "Fracionado"),
        ("Gama Express", "Fracionado"),
        ("Delta Cargas", "Lotação"),
        ("Omega Trans", "Refrigerado"),
        ("Sigma Fretes", "Granel"),
        ("Zeta Distribuidores", "Fracionado"),
        ("Theta Operador Logístico", "Lotação")
    ]
    cursor.executemany("INSERT INTO d_transportadoras (nome_transportadora, tipo_transporte) VALUES (?, ?);", transportadoras)

    # Clientes - 15 estados
    clientes = [
        ("CD São Paulo", "São Paulo", "SP", "Sudeste"),
        ("Filial Rio de Janeiro", "Rio de Janeiro", "RJ", "Sudeste"),
        ("Atacado Belo Horizonte", "Belo Horizonte", "MG", "Sudeste"),
        ("Operador Vitória", "Vitória", "ES", "Sudeste"),
        ("Cooperativa Curitiba", "Curitiba", "PR", "Sul"),
        ("Logística Joinville", "Joinville", "SC", "Sul"),
        ("Terminal Porto Alegre", "Porto Alegre", "RS", "Sul"),
        ("Distribuidora Salvador", "Salvador", "BA", "Nordeste"),
        ("Hub Fortaleza", "Fortaleza", "CE", "Nordeste"),
        ("Polo Recife", "Recife", "PE", "Nordeste"),
        ("Logística São Luís", "São Luís", "MA", "Nordeste"),
        ("Agro Goiânia", "Goiânia", "GO", "Centro-Oeste"),
        ("Plataforma Cuiabá", "Cuiabá", "MT", "Centro-Oeste"),
        ("Norte Belém", "Belém", "PA", "Norte"),
        ("Polo Manaus", "Manaus", "AM", "Norte")
    ]
    cursor.executemany("INSERT INTO d_clientes (nome_cliente, cidade, estado, regiao) VALUES (?, ?, ?, ?);", clientes)

    # Gera 100 entregas
    import random
    from datetime import datetime, timedelta
    
    segmentos = ["E-Commerce", "Varejo", "Indústria", "Agronegócio", "Medicamentos", "Alimentos"]
    status_opcoes = ["Entregue No Prazo", "Atrasado", "Retido na Barreira Fiscal", "Extraviado"]
    gargalos_opcoes = {
        "Entregue No Prazo": "Nenhum Operacional",
        "Atrasado": "Atraso no Carregamento",
        "Retido na Barreira Fiscal": "Fiscalização / SEFAZ",
        "Extraviado": "Sinistro / Roubo de Carga"
    }

    random.seed(42)
    data_base = datetime(2026, 6, 1)

    for i in range(1, 101):
        nf = f"NF-2026-{i:03d}"
        id_transp = random.randint(1, 8)
        id_clie = random.randint(1, 15)
        seg = random.choice(segmentos)
        
        d_emissao = data_base + timedelta(days=random.randint(0, 15))
        d_previsao = d_emissao + timedelta(days=random.randint(3, 7))
        
        sorteio_status = random.choices(status_opcoes, weights=[0.68, 0.18, 0.10, 0.04], k=1)[0]
        gargalo = gargalos_opcoes[sorteio_status]
        
        if sorteio_status == "Entregue No Prazo":
            d_entrega = d_previsao - timedelta(days=random.randint(0, 2))
            data_entrega_str = d_entrega.strftime('%Y-%m-%d')
        elif sorteio_status == "Extraviado":
            data_entrega_str = "Não Entregue"
        else:
            d_entrega = d_previsao + timedelta(days=random.randint(2, 6))
            data_entrega_str = d_entrega.strftime('%Y-%m-%d')

        valor_nf = round(random.uniform(5000, 120000), 2)
        peso = round(random.uniform(50, 4000), 2)
        
        frete_tabela = round(valor_nf * random.uniform(0.02, 0.05), 2)
        if random.random() > 0.75:
            frete_cobrado = round(frete_tabela + random.uniform(150, 1200), 2)
        else:
            frete_cobrado = frete_tabela

        cursor.execute("""
            INSERT INTO f_entregas (
                numero_nota_fiscal, id_transportadora, id_cliente, segmento_operacao,
                data_emissao, data_previsao_entrega, data_entrega_real, valor_nota_fiscal,
                peso_kg, custo_frete_tabela, custo_frete_cobrado, status_entrega, motivo_gargalo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (nf, id_transp, id_clie, seg, 
              d_emissao.strftime('%Y-%m-%d'), 
              d_previsao.strftime('%Y-%m-%d'), 
              data_entrega_str, 
              valor_nf, peso, frete_tabela, frete_cobrado, 
              sorteio_status, gargalo))

    conexao.commit()
    conexao.close()
    print("✅ Banco criado com sucesso!")

# ============================================
# CRIA O BANCO E CARREGA OS DADOS
# ============================================

# Cria o banco (se não existir)
if not os.path.exists(DB_PATH):
    with st.spinner("Criando banco de dados..."):
        criar_banco()

# Carrega os dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados():
    conexao = sqlite3.connect(DB_PATH)
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
    df['data_emissao'] = pd.to_datetime(df['data_emissao'])
    return df

df_original = carregar_dados()

# Verifica
if df_original.empty:
    st.error("❌ Nenhum dado encontrado!")
    st.stop()

# ============================================
# FILTROS
# ============================================
st.sidebar.header("🎯 Painel de Filtros Cruzados")

data_minima = df_original["data_emissao"].min().date()
data_maxima = df_original["data_emissao"].max().date()

st.sidebar.markdown("📅 **Filtro por Período Temporal:**")
periodo_selecionado = st.sidebar.date_input(
    "Selecione o intervalo de análise:",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima
)

st.sidebar.markdown("---")

lista_segmentos = ["Todos"] + sorted(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Selecione o Segmento:", lista_segmentos)

lista_regioes = ["Todos"] + sorted(df_original["regiao"].unique())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região Geográfica:", lista_regioes)

lista_estados = ["Todos"] + sorted(df_original["estado"].unique())
estado_selecionado = st.sidebar.selectbox("Selecione o Estado de Destino:", lista_estados)

lista_status = ["Todos"] + sorted(df_original["status_entrega"].unique())
status_selecionado = st.sidebar.selectbox("Status da Entrega:", lista_status)

lista_transportadoras = ["Todos"] + sorted(df_original["nome_transportadora"].unique())
transportadora_selecionada = st.sidebar.selectbox("Transportadora:", lista_transportadoras)

# ============================================
# APLICA FILTROS
# ============================================
df_filtrado = df_original.copy()

if isinstance(periodo_selecionado, tuple) and len(periodo_selecionado) == 2:
    data_inicio, data_fim = periodo_selecionado
    df_filtrado = df_filtrado[
        (df_filtrado["data_emissao"].dt.date >= data_inicio) & 
        (df_filtrado["data_emissao"].dt.date <= data_fim)
    ]

if segmento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento_operacao"] == segmento_selecionado]
if regiao_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["regiao"] == regiao_selecionada]
if estado_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_selecionado]
if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_entrega"] == status_selecionado]
if transportadora_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nome_transportadora"] == transportadora_selecionada]

# ============================================
# INDICADORES
# ============================================
st.subheader("📊 Indicadores de Performance Operacional")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_entregas = len(df_filtrado)
    st.metric(label="Total de Entregas (NFs)", value=f"{total_entregas}")

with col2:
    faturamento_frete = df_filtrado["custo_frete_cobrado"].sum()
    st.metric(label="Total Frete Cobrado", value=f"R$ {faturamento_frete:,.2f}")

with col3:
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    desvio_meta = taxa_otif - 95.0
    st.metric(
        label="Taxa de OTIF (SLA)", 
        value=f"{taxa_otif:.1f}%", 
        delta=f"{desvio_meta:.1f}% vs Meta (95%)", 
        delta_color="normal" if desvio_meta >= 0 else "inverse"
    )

with col4:
    df_filtrado["desvio_frete"] = df_filtrado["custo_frete_cobrado"] - df_filtrado["custo_frete_tabela"]
    prejuizo_frete = df_filtrado[df_filtrado["desvio_frete"] > 0]["desvio_frete"].sum()
    percentual_perda = (prejuizo_frete / faturamento_frete * 100) if faturamento_frete > 0 else 0.0
    st.metric(
        label="Prejuízo (Frete Estourado)", 
        value=f"R$ {prejuizo_frete:,.2f}", 
        delta=f"{percentual_perda:.1f}% de vazamento", 
        delta_color="inverse"
    )

st.markdown("---")

if taxa_otif >= 95.0:
    st.success(f"🏅 **Classificação de Mercado - Zona de Excelência:** O nível de serviço atual está em **{taxa_otif:.1f}%**.")
elif taxa_otif >= 85.0:
    st.warning(f"⚠️ **Classificação de Mercado - Zona de Atenção:** O nível de serviço está em **{taxa_otif:.1f}%**.")
else:
    st.error(f"🚨 **Classificação de Mercado - Zona Crítica:** O nível de serviço desabou para **{taxa_otif:.1f}%**.")

st.markdown("---")

# ============================================
# GRÁFICOS
# ============================================
st.subheader("📈 Volumetria e Distribuição de SLAs")
graf1, graf2 = st.columns(2)

with graf1:
    df_estado = df_filtrado.groupby(['estado', 'status_entrega']).size().reset_index(name='quantidade')
    fig_estado = px.bar(
        df_estado, x='estado', y='quantidade', color='status_entrega',
        title="Ocorrências Logísticas por Estado de Destino",
        labels={'estado': 'Estado', 'quantidade': 'Qtd Notas Fiscais'},
        barmode='group'
    )
    st.plotly_chart(fig_estado, use_container_width=True)

with graf2:
    df_pizza = df_filtrado["status_entrega"].value_counts().reset_index()
    df_pizza.columns = ["Status", "Quantidade"]
    fig_pizza = px.pie(df_pizza, names="Status", values="Quantidade", title="Distribuição Geral por Status de Entrega", hole=0.4)
    st.plotly_chart(fig_pizza, use_container_width=True)

st.markdown("---")

st.subheader("🚛 Performance de Parceiros e Auditoria de Custos")
graf3, graf4 = st.columns(2)

with graf3:
    df_transp = df_filtrado.groupby(['nome_transportadora', 'status_entrega']).size().reset_index(name='entregas')
    fig_barra_transp = px.bar(
        df_transp, x='nome_transportadora', y='entregas', color='status_entrega',
        title="Nível de Serviço (SLA) por Transportadora",
        labels={'nome_transportadora': 'Transportadora', 'entregas': 'Quantidade'},
        barmode='stack'
    )
    st.plotly_chart(fig_barra_transp, use_container_width=True)

with graf4:
    df_custos = df_filtrado.groupby('segmento_operacao')[['custo_frete_tabela', 'custo_frete_cobrado']].sum().reset_index()
    df_custos_melt = df_custos.melt(id_vars='segmento_operacao', value_vars=['custo_frete_tabela', 'custo_frete_cobrado'],
                                    var_name='Tipo_Custo', value_name='Valor')
    df_custos_melt['Tipo_Custo'] = df_custos_melt['Tipo_Custo'].map({'custo_frete_tabela': 'Frete Contratado', 'custo_frete_cobrado': 'Frete Real Cobrado'})
    fig_comparativo = px.bar(
        df_custos_melt, x='segmento_operacao', y='Valor', color='Tipo_Custo', barmode='group',
        title="Auditoria Financeira por Canal"
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

st.markdown("---")

# ============================================
# TABELA FINAL
# ============================================
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")
colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", "estado",
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)

# ============================================
# BOTÃO RECARREGAR
# ============================================
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()
