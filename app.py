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
    page_title="Torre de Performance Logística",
    layout="wide",
    page_icon="🛸"
)

# ============================================
# CSS PERSONALIZADO PARA MELHORAR VISUALIZAÇÃO
# ============================================
st.markdown("""
    <style>
        /* Bloqueia tradução */
        .goog-te-banner-frame { display: none !important; }
        #goog-gt-tt { display: none !important; }
        .goog-tooltip { display: none !important; }
        .goog-text-highlight { background: transparent !important; border: none !important; }
        .goog-te-gadget { display: none !important; }
        .goog-te-gadget-simple { display: none !important; }
        
        /* Melhora a visualização dos métricas */
        [data-testid="metric-container"] {
            width: 100% !important;
            min-width: 120px !important;
        }
        
        [data-testid="metric-container"] > div {
            width: 100% !important;
            overflow: visible !important;
        }
        
        /* Diminui a fonte dos números para caber melhor */
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            line-height: 1.2 !important;
        }
        
        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            font-size: 0.7rem !important;
        }
        
        /* Ajusta para colunas menores em telas pequenas */
        @media (max-width: 768px) {
            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                font-size: 0.9rem !important;
            }
            [data-testid="metric-container"] [data-testid="stMetricLabel"] {
                font-size: 0.65rem !important;
            }
        }
    </style>
    
    <meta name="google" content="notranslate">
    <meta name="google-translate-custom" content="notranslate">
    <meta http-equiv="Content-Language" content="pt-BR">
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Monitoramento de Frotas Próprias, Transportadoras e Indicadores Operacionais</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================
# MAPEAMENTO DE ESTADOS (NOME COMPLETO)
# ============================================
ESTADOS_MAP = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Minas Gerais",
    "ES": "Espírito Santo", "PR": "Paraná", "SC": "Santa Catarina",
    "RS": "Rio Grande do Sul", "BA": "Bahia", "CE": "Ceará",
    "PE": "Pernambuco", "MA": "Maranhão", "GO": "Goiás",
    "MT": "Mato Grosso", "PA": "Pará", "AM": "Amazonas"
}
ESTADOS_REVERSE = {v: k for k, v in ESTADOS_MAP.items()}

# ============================================
# FORÇA A RECRIAÇÃO DO BANCO (CHAMA O GERADOR)
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
# FUNÇÃO PARA FORMATAR NÚMEROS
# ============================================
def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    if valor is None or pd.isna(valor):
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_numero(valor, decimal=0):
    """Formata número com separador de milhar"""
    if valor is None or pd.isna(valor):
        return "0"
    return f"{valor:,.{decimal}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_km(valor):
    """Formata KM com separador de milhar"""
    if valor is None or pd.isna(valor):
        return "0"
    return f"{valor:,.0f}".replace(",", ".")

# ============================================
# CARREGA OS DADOS
# ============================================
@st.cache_data(ttl=300)
def carregar_dados():
    conexao = sqlite3.connect("torre_controle_final.db")
    query = """
        SELECT 
            f.*,
            t.nome_transportadora,
            t.modalidade,
            c.nome_cliente,
            c.cidade,
            c.estado,
            c.regiao,
            c.tipo_destino,
            m.nome_motorista,
            m.codigo_motorista,
            v.placa,
            v.modelo as veiculo_modelo,
            v.fabricante,
            v.tipo_veiculo,
            v.capacidade_kg,
            fv.nome_fornecedor
        FROM f_entregas f
        JOIN d_transportadoras t ON f.id_transportadora = t.id_transportadora
        JOIN d_clientes c ON f.id_cliente = c.id_cliente
        LEFT JOIN d_motoristas m ON f.id_motorista = m.id_motorista
        LEFT JOIN d_veiculos v ON f.id_veiculo = v.id_veiculo
        LEFT JOIN d_fornecedores fv ON f.id_fornecedor = fv.id_fornecedor
    """
    df = pd.read_sql_query(query, conexao)
    conexao.close()
    
    df['data_emissao'] = pd.to_datetime(df['data_emissao'])
    df['estado_exibicao'] = df['estado'].map(ESTADOS_MAP).fillna(df['estado'])
    
    return df

df_original = carregar_dados()

if df_original.empty:
    st.error("❌ Nenhum dado encontrado!")
    st.stop()

# ============================================
# FILTROS
# ============================================
st.sidebar.header("🎯 Painel de Filtros Cruzados")

data_minima = df_original["data_emissao"].min().date()
data_maxima = df_original["data_emissao"].max().date()

st.sidebar.markdown("📅 **Período:**")
periodo_selecionado = st.sidebar.date_input(
    "Intervalo de análise:",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima
)

st.sidebar.markdown("---")

lista_tipo_operacao = ["Todos"] + sorted(df_original["tipo_operacao"].unique())
tipo_operacao = st.sidebar.selectbox("Tipo de Operação:", lista_tipo_operacao)

lista_segmentos = ["Todos"] + sorted(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Segmento:", lista_segmentos)

lista_estados = ["Todos"] + sorted(df_original["estado_exibicao"].unique())
estado_selecionado_exibicao = st.sidebar.selectbox("Estado:", lista_estados)
estado_selecionado = ESTADOS_REVERSE.get(estado_selecionado_exibicao, estado_selecionado_exibicao) if estado_selecionado_exibicao != "Todos" else "Todos"

lista_status = ["Todos"] + sorted(df_original["status_entrega"].unique())
status_selecionado = st.sidebar.selectbox("Status:", lista_status)

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

if tipo_operacao != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_operacao"] == tipo_operacao]
if segmento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento_operacao"] == segmento_selecionado]
if estado_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_selecionado]
if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_entrega"] == status_selecionado]
if transportadora_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nome_transportadora"] == transportadora_selecionada]

# Separa por tipo para cálculos
df_externa = df_filtrado[df_filtrado["tipo_operacao"] == "externa"] if not df_filtrado.empty else pd.DataFrame()
df_propria = df_filtrado[df_filtrado["tipo_operacao"] == "propria"] if not df_filtrado.empty else pd.DataFrame()

# ============================================
# INDICADORES GERAIS (com colunas mais largas)
# ============================================
st.subheader("📊 Indicadores Gerais de Performance")

# Usa 5 colunas com largura igual
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_entregas = len(df_filtrado)
    st.metric("Total de Entregas", f"{formatar_numero(total_entregas)}")

with col2:
    faturamento_total = df_filtrado["valor_nota_fiscal"].sum()
    st.metric("Faturamento Total", formatar_moeda(faturamento_total))

with col3:
    frete_total = df_filtrado["custo_frete_cobrado"].sum()
    st.metric("Custo Frete Total", formatar_moeda(frete_total))

with col4:
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    st.metric("Taxa OTIF (SLA)", f"{taxa_otif:.1f}%")

with col5:
    if not df_propria.empty:
        km_total = df_propria["km_rodados"].sum()
        st.metric("KM Rodados (Frota)", formatar_km(km_total))
    else:
        st.metric("KM Rodados (Frota)", "0")

st.markdown("---")

# ============================================
# INDICADORES FINANCEIROS
# ============================================
st.subheader("💰 Indicadores Financeiros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if not df_externa.empty:
        vazamento = df_externa["custo_frete_cobrado"].sum() - df_externa["custo_frete_tabela"].sum()
        if vazamento < 0:
            vazamento = 0
        percentual = (vazamento / df_externa["custo_frete_cobrado"].sum() * 100) if df_externa["custo_frete_cobrado"].sum() > 0 else 0
        st.metric(
            "Vazamento em Fretes", 
            formatar_moeda(vazamento)
        )
    else:
        st.metric("Vazamento em Fretes", "R$ 0,00")

with col2:
    if not df_propria.empty:
        custo_operacional = df_propria["custo_combustivel"].sum() + df_propria["custo_manutencao"].sum() + df_propria["custo_pedagio"].sum()
        st.metric("Custo Operacional (Frota)", formatar_moeda(custo_operacional))
    else:
        st.metric("Custo Operacional (Frota)", "R$ 0,00")

with col3:
    if not df_propria.empty:
        custo_combustivel = df_propria["custo_combustivel"].sum()
        st.metric("Custo Combustível", formatar_moeda(custo_combustivel))
    else:
        st.metric("Custo Combustível", "R$ 0,00")

with col4:
    if not df_propria.empty:
        custo_manutencao = df_propria["custo_manutencao"].sum()
        st.metric("Custo Manutenção", formatar_moeda(custo_manutencao))
    else:
        st.metric("Custo Manutenção", "R$ 0,00")

st.markdown("---")

# ============================================
# INDICADORES DE PRODUTIVIDADE
# ============================================
if not df_propria.empty:
    st.subheader("⚡ Indicadores de Produtividade")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_km = df_propria["km_rodados"].mean()
        st.metric("Média KM/Entrega", f"{avg_km:.1f} km")
    
    with col2:
        avg_consumo = df_propria["km_rodados"].sum() / df_propria["litros_combustivel"].sum() if df_propria["litros_combustivel"].sum() > 0 else 0
        st.metric("Consumo Médio", f"{avg_consumo:.1f} km/L")
    
    with col3:
        avg_horas = df_propria["horas_trabalhadas"].mean()
        st.metric("Média Horas/Viagem", f"{avg_horas:.1f} h")
    
    with col4:
        avg_entregas = df_propria["entregas_dia"].mean()
        st.metric("Média Entregas/Dia", f"{avg_entregas:.1f}")
    
    with col5:
        custo_km = df_propria["custo_combustivel"].sum() / df_propria["km_rodados"].sum() if df_propria["km_rodados"].sum() > 0 else 0
        st.metric("Custo/km (Combustível)", f"R$ {custo_km:.2f}")

    st.markdown("---")

# ============================================
# INDICADORES DE QUALIDADE
# ============================================
st.subheader("⭐ Indicadores de Qualidade")

col1, col2, col3, col4 = st.columns(4)

with col1:
    entregas_com_avaria = len(df_filtrado[df_filtrado["avarias"] == True])
    taxa_avaria = (entregas_com_avaria / total_entregas * 100) if total_entregas > 0 else 0
    st.metric("Taxa de Avarias", f"{taxa_avaria:.1f}%")

with col2:
    valor_avaria = df_filtrado["valor_avaria"].sum()
    st.metric("Valor Total de Avarias", formatar_moeda(valor_avaria))

with col3:
    if not df_filtrado.empty:
        nota_media = df_filtrado["nota_satisfacao"].mean()
        st.metric("Satisfação do Cliente", f"{nota_media:.1f}/5")
    else:
        st.metric("Satisfação do Cliente", "0.0/5")

with col4:
    total_reclamacoes = len(df_filtrado[df_filtrado["reclamacao_cliente"] == True])
    taxa_reclamacao = (total_reclamacoes / total_entregas * 100) if total_entregas > 0 else 0
    st.metric("Taxa de Reclamações", f"{taxa_reclamacao:.1f}%")

st.markdown("---")

# ============================================
# CLASSIFICAÇÃO GERAL
# ============================================
if taxa_otif >= 95.0:
    st.success(f"🏅 **Excelência Operacional** - Nível de serviço em **{taxa_otif:.1f}%**")
elif taxa_otif >= 85.0:
    st.warning(f"⚠️ **Zona de Atenção** - Nível de serviço em **{taxa_otif:.1f}%**")
else:
    st.error(f"🚨 **Zona Crítica** - Nível de serviço em **{taxa_otif:.1f}%**")

st.markdown("---")

# ============================================
# GRÁFICOS
# ============================================
st.subheader("📈 Análises Avançadas")

graf1, graf2 = st.columns(2)

with graf1:
    df_status = df_filtrado.groupby(['tipo_operacao', 'status_entrega']).size().reset_index(name='quantidade')
    fig = px.bar(
        df_status, x='tipo_operacao', y='quantidade', color='status_entrega',
        title="Status por Tipo de Operação",
        labels={'tipo_operacao': 'Tipo', 'quantidade': 'Quantidade'},
        barmode='stack'
    )
    st.plotly_chart(fig, use_container_width=True)

with graf2:
    df_estado = df_filtrado.groupby(['estado_exibicao', 'status_entrega']).size().reset_index(name='quantidade')
    df_estado = df_estado.rename(columns={'estado_exibicao': 'estado'})
    fig = px.bar(
        df_estado, x='estado', y='quantidade', color='status_entrega',
        title="Entregas por Estado",
        labels={'estado': 'Estado', 'quantidade': 'Quantidade'},
        barmode='group'
    )
    fig.update_layout(xaxis={'tickangle': 45})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================
# GRÁFICOS DA FROTA PRÓPRIA
# ============================================
if not df_propria.empty:
    st.subheader("🚛 Análise da Frota Própria")
    
    graf3, graf4 = st.columns(2)
    
    with graf3:
        df_motorista = df_propria.groupby('nome_motorista').agg({
            'km_rodados': 'sum',
            'entregas_dia': 'sum'
        }).reset_index()
        fig = px.bar(
            df_motorista, x='nome_motorista', y='km_rodados',
            title="KM Rodados por Motorista",
            labels={'nome_motorista': 'Motorista', 'km_rodados': 'KM Rodados'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with graf4:
        df_veiculo = df_propria.groupby('placa').agg({
            'km_rodados': 'sum',
            'litros_combustivel': 'sum'
        }).reset_index()
        df_veiculo['consumo'] = df_veiculo['km_rodados'] / df_veiculo['litros_combustivel']
        fig = px.bar(
            df_veiculo, x='placa', y='consumo',
            title="Consumo (km/L) por Veículo",
            labels={'placa': 'Veículo', 'consumo': 'km/L'},
            color='consumo',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    graf5, graf6 = st.columns(2)
    
    with graf5:
        df_custo = df_propria.groupby('nome_motorista').agg({
            'km_rodados': 'sum',
            'custo_combustivel': 'sum',
            'custo_manutencao': 'sum'
        }).reset_index()
        df_custo['custo_km'] = (df_custo['custo_combustivel'] + df_custo['custo_manutencao']) / df_custo['km_rodados']
        fig = px.bar(
            df_custo, x='nome_motorista', y='custo_km',
            title="Custo por KM por Motorista",
            labels={'nome_motorista': 'Motorista', 'custo_km': 'R$/km'},
            color='custo_km',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with graf6:
        df_avaria = df_propria.groupby('nome_motorista').agg({
            'qtd_avarias': 'sum',
            'km_rodados': 'sum'
        }).reset_index()
        df_avaria['avaria_por_km'] = df_avaria['qtd_avarias'] / (df_avaria['km_rodados'] / 1000)
        fig = px.bar(
            df_avaria, x='nome_motorista', y='avaria_por_km',
            title="Avarias por 1.000 KM",
            labels={'nome_motorista': 'Motorista', 'avaria_por_km': 'Avarias/1.000 km'},
            color='avaria_por_km',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ============================================
# ANÁLISE DE GARGALOS
# ============================================
if not df_filtrado.empty:
    st.subheader("🔍 Análise de Gargalos")
    
    df_gargalos = df_filtrado[df_filtrado["status_entrega"] != "Entregue No Prazo"]
    
    if not df_gargalos.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            df_garg = df_gargalos.groupby('motivo_gargalo').size().reset_index(name='quantidade')
            df_garg = df_garg.sort_values('quantidade', ascending=False)
            fig = px.pie(
                df_garg, values='quantidade', names='motivo_gargalo',
                title="Distribuição dos Gargalos",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            df_garg_transp = df_gargalos.groupby('nome_transportadora').size().reset_index(name='quantidade')
            df_garg_transp = df_garg_transp.sort_values('quantidade', ascending=False)
            fig = px.bar(
                df_garg_transp, x='nome_transportadora', y='quantidade',
                title="Gargalos por Transportadora",
                labels={'nome_transportadora': 'Transportadora', 'quantidade': 'Quantidade'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("🎉 Nenhum gargalo identificado no período!")
    
    st.markdown("---")

# ============================================
# TABELA COMPLETA
# ============================================
st.subheader("📋 Detalhamento Completo das Entregas")

df_tabela = df_filtrado.copy()
df_tabela['estado'] = df_tabela['estado_exibicao']

colunas_exibicao = [
    "numero_nota_fiscal", "tipo_operacao", "nome_transportadora",
    "nome_motorista", "placa", "nome_cliente", "estado",
    "segmento_operacao", "data_emissao", "status_entrega", "motivo_gargalo",
    "valor_nota_fiscal", "custo_frete_cobrado"
]

if not df_propria.empty:
    colunas_exibicao += ["km_rodados", "litros_combustivel", "custo_combustivel", "custo_manutencao"]

colunas_exibicao += ["qtd_avarias", "valor_avaria", "nota_satisfacao"]

# Formata os valores na tabela
df_tabela_display = df_tabela[colunas_exibicao].copy()
colunas_moeda = ["valor_nota_fiscal", "custo_frete_cobrado", "custo_combustivel", "custo_manutencao", "valor_avaria"]
colunas_numero = ["km_rodados", "litros_combustivel", "qtd_avarias"]

for col in colunas_moeda:
    if col in df_tabela_display.columns:
        df_tabela_display[col] = df_tabela_display[col].apply(lambda x: formatar_moeda(x) if pd.notna(x) else "R$ 0,00")

for col in colunas_numero:
    if col in df_tabela_display.columns:
        if col == "km_rodados":
            df_tabela_display[col] = df_tabela_display[col].apply(lambda x: formatar_km(x) if pd.notna(x) else "0")
        else:
            df_tabela_display[col] = df_tabela_display[col].apply(lambda x: f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notna(x) else "0")

st.dataframe(df_tabela_display, use_container_width=True)

# ============================================
# BOTÃO RECARREGAR
# ============================================
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recarregar Dados", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **📊 Indicadores disponíveis:**
    - ✅ Faturamento e frete
    - ✅ KM rodados e combustível
    - ✅ Manutenção e pedágio
    - ✅ Horas trabalhadas
    - ✅ Avarias e reclamações
    - ✅ Satisfação do cliente
    - ✅ Gargalos operacionais
    - ✅ Produtividade por motorista
    """
)
