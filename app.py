# ==============================================================================
# PROJETO: TORRE DE CONTROLE DE PERFORMANCE LOGÍSTICA - BIG DATA SIMULATION
# ETAPA: PAINEL EXECUTIVO STREAMLIT - VERSÃO V10 (PRODUÇÃO RENDER)
# AUTOR: Luiz Edglei (Expert em Logística & Data Science)
# ==============================================================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Configuração da página e layout do dashboard
st.set_page_config(page_title="Torre de Controle Executiva", layout="wide")
st.title("📊 Torre de Controle & Performance Logística Avançada")
st.markdown("---")

# Definição do caminho do banco de dados (Caminho relativo para ambiente de produção)
caminho_banco = "torre_controle_final.db"

# Validação de segurança para conferir se o banco de dados foi carregado pelo Git
if not os.path.exists(caminho_banco):
    st.error(f"❌ Erro Crítico: O banco de dados '{caminho_banco}' não foi localizado na raiz do projeto.")
    st.stop()

# Estabelece conexão com o banco SQLite
conexao = sqlite3.connect(caminho_banco)

# Carrega os segmentos únicos para popular o filtro dinâmico lateral
df_sidebar = pd.read_sql_query("SELECT DISTINCT segmento_operacao FROM f_entregas", conexao)
lista_segmentos = ["Todos"] + list(df_sidebar['segmento_operacao'].unique())

st.sidebar.header("🕹️ Filtros Operacionais")
segmento_selecionado = st.sidebar.selectbox("Escolha o Segmento de Negócio:", lista_segmentos)

# Bloco condicional para construção das queries SQL baseado no filtro escolhido
if segmento_selecionado != "Todos":
    query_kpi = "SELECT COUNT(*) AS total, SUM(CASE WHEN status_entrega = 'Atrasado' THEN 1 ELSE 0 END) AS atrasos, SUM(CASE WHEN custo_frete_cobrado > custo_frete_tabela THEN (custo_frete_cobrado - custo_frete_tabela) ELSE 0 END) AS desvio FROM f_entregas WHERE segmento_operacao = ?"
    query_auditoria = "SELECT numero_nota_fiscal AS [Nota Fiscal], (custo_frete_cobrado - custo_frete_tabela) AS [Prejuizo (R$)] FROM f_entregas WHERE segmento_operacao = ? AND custo_frete_cobrado > custo_frete_tabela"
    query_perf = "SELECT c.regiao AS [Regiao], AVG(JULIANDAY(f.data_entrega_real) - JULIANDAY(f.data_emissao)) AS [Dias] FROM f_entregas f INNER JOIN d_clientes c ON f.id_cliente = c.id_cliente WHERE f.data_entrega_real IS NOT NULL AND f.segmento_operacao = ? GROUP BY c.regiao"
    query_tabela = "SELECT id_entrega AS [ID], numero_nota_fiscal AS [NF], segmento_operacao AS [Segmento], status_entrega AS [Status], motivo_gargalo AS [Diagnóstico Operacional], (custo_frete_cobrado - custo_frete_tabela) AS [Divergência Frete (R$)] FROM f_entregas WHERE segmento_operacao = ?"
    params = [segmento_selecionado]
else:
    query_kpi = "SELECT COUNT(*) AS total, SUM(CASE WHEN status_entrega = 'Atrasado' THEN 1 ELSE 0 END) AS atrasos, SUM(CASE WHEN custo_frete_cobrado > custo_frete_tabela THEN (custo_frete_cobrado - custo_frete_tabela) ELSE 0 END) AS desvio FROM f_entregas"
    query_auditoria = "SELECT numero_nota_fiscal AS [Nota Fiscal], (custo_frete_cobrado - custo_frete_tabela) AS [Prejuizo (R$)] FROM f_entregas WHERE custo_frete_cobrado > custo_frete_tabela"
    query_perf = "SELECT c.regiao AS [Regiao], AVG(JULIANDAY(f.data_entrega_real) - JULIANDAY(f.data_emissao)) AS [Dias] FROM f_entregas f INNER JOIN d_clientes c ON f.id_cliente = c.id_cliente WHERE f.data_entrega_real IS NOT NULL GROUP BY c.regiao"
    query_tabela = "SELECT id_entrega AS [ID], numero_nota_fiscal AS [NF], segmento_operacao AS [Segmento], status_entrega AS [Status], motivo_gargalo AS [Diagnóstico Operacional], (custo_frete_cobrado - custo_frete_tabela) AS [Divergência Frete (R$)] FROM f_entregas"
    params = []

# Processamento e renderização dos KPIs Principais
df_kpi = pd.read_sql_query(query_kpi, conexao, params=params)

if not df_kpi.empty and pd.notna(df_kpi['total'].iloc[0]) and df_kpi['total'].iloc[0] > 0:
    total_envios = df_kpi['total'].iloc[0]
    total_atrasos = df_kpi['atrasos'].iloc[0] if pd.notna(df_kpi['atrasos'].iloc[0]) else 0
    prejuizo_frete = df_kpi['desvio'].iloc[0] if pd.notna(df_kpi['desvio'].iloc[0]) else 0.0
else:
    total_envios = 0
    total_atrasos = 0
    prejuizo_frete = 0.0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"📦 **Volumetria Total:** {total_envios} NFs")
with col2:
    st.markdown(f"⚠️ **Ocorrências de Atraso:** {total_atrasos}")
with col3:
    st.markdown(f"💸 **Vazamento de Lucro (Auditoria):** R$ {prejuizo_frete:.2f}")

st.markdown("---")
col_graf1, col_graf2 = st.columns(2)

# Gráfico 1: Auditoria Financeira de Frete
with col_graf1:
    st.subheader("🔍 Estouro de Custo de Frete por Nota Fiscal")
    df_aud = pd.read_sql_query(query_auditoria, conexao, params=params)
    if not df_aud.empty:
        fig_aud = px.bar(df_aud, x="Nota Fiscal", y="Prejuizo (R$)", title="Desvios Contratuais por Emissão", color="Prejuizo (R$)", color_continuous_scale="Reds")
        st.plotly_chart(fig_aud, use_container_width=True)
    else:
        st.info("Nenhum desvio financeiro identificado para este segmento.")

# Gráfico 2: Análise de Performance de Lead Time operacional
with col_graf2:
    st.subheader("🗺️ Lead Time Médio por Região Destino")
    df_perf = pd.read_sql_query(query_perf, conexao, params=params)
    if not df_perf.empty:
        fig_perf = px.line(df_perf, x="Regiao", y="Dias", title="Ciclo de Pedido em Dias Úteis", markers=True)
        st.plotly_chart(fig_perf, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar a curva de Lead Time.")

st.markdown("---")
st.subheader("📋 Diagnóstico de Gargalos Ocorrido na Operação (Massa Fato)")

# Exibição analítica da tabela de dados tratada
df_completo = pd.read_sql_query(query_tabela, conexao, params=params)
st.table(df_completo)

conexao.close()