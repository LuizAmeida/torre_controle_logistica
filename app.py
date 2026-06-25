import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Torre de Controle Logística",
    layout="wide",
    page_icon="🛸"
)

# ============================================
# MAPEAMENTO DE ESTADOS - NOME COMPLETO
# ============================================
ESTADOS_MAP = {
    "SP": "São Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    "ES": "Espírito Santo",
    "PR": "Paraná",
    "SC": "Santa Catarina",
    "RS": "Rio Grande do Sul",
    "BA": "Bahia",
    "CE": "Ceará",
    "PE": "Pernambuco",
    "MA": "Maranhão",
    "GO": "Goiás",
    "MT": "Mato Grosso",
    "PA": "Pará",
    "AM": "Amazonas"
}

# Mapeamento reverso para consultas no banco
ESTADOS_REVERSE = {v: k for k, v in ESTADOS_MAP.items()}

# ============================================
# FORÇA A RECRIAÇÃO DO BANCO
# ============================================
db_path = "torre_controle_final.db"

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("🗑️ Banco antigo removido")
    except Exception as e:
        print(f"⚠️ Erro ao remover: {e}")

try:
    import gerar_banco
    gerar_banco.criar_e_povoar_banco()
    print("✅ Banco recriado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao recriar: {e}")
    st.error(f"❌ Erro ao criar banco: {e}")
    st.stop()

# ============================================
# CARREGA OS DADOS
# ============================================
@st.cache_data(ttl=300)
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
    df['data_emissao'] = pd.to_datetime(df['data_emissao'])
    
    # ===== CONVERTE ESTADOS PARA NOME COMPLETO =====
    df['estado_exibicao'] = df['estado'].map(ESTADOS_MAP).fillna(df['estado'])
    
    return df

df_original = carregar_dados()

if df_original.empty:
    st.error("❌ Nenhum dado encontrado!")
    st.stop()

# ============================================
# TÍTULO
# ============================================
st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Solução Gerencial: Auditoria Automática de Fretes, Análise de SLA e Controle de Metas</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================
# FILTROS - USANDO NOME COMPLETO DOS ESTADOS
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

# Estados com nome completo
lista_estados = ["Todos"] + sorted(df_original["estado_exibicao"].unique())
estado_selecionado_exibicao = st.sidebar.selectbox("Selecione o Estado de Destino:", lista_estados)

# Converte de volta para sigla para filtrar
estado_selecionado = ESTADOS_REVERSE.get(estado_selecionado_exibicao, estado_selecionado_exibicao) if estado_selecionado_exibicao != "Todos" else "Todos"

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
# GRÁFICOS - USANDO NOME COMPLETO
# ============================================
st.subheader("📈 Volumetria e Distribuição de SLAs")
graf1, graf2 = st.columns(2)

with graf1:
    # Usa estado_exibicao (nome completo)
    df_estado = df_filtrado.groupby(['estado_exibicao', 'status_entrega']).size().reset_index(name='quantidade')
    df_estado = df_estado.rename(columns={'estado_exibicao': 'estado'})
    fig_estado = px.bar(
        df_estado, x='estado', y='quantidade', color='status_entrega',
        title="Ocorrências Logísticas por Estado de Destino",
        labels={'estado': 'Estado', 'quantidade': 'Qtd Notas Fiscais'},
        barmode='group',
        category_orders={'estado': sorted(df_estado['estado'].unique())}
    )
    fig_estado.update_layout(xaxis={'tickangle': 45})
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
# TABELA FINAL - USANDO NOME COMPLETO
# ============================================
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")

# Cria uma cópia com estado_exibicao
df_tabela = df_filtrado.copy()
df_tabela['estado'] = df_tabela['estado_exibicao']

colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", "estado",
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]
st.dataframe(df_tabela[colunas_exibicao], use_container_width=True)

# ============================================
# BOTÃO RECARREGAR
# ============================================
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()
