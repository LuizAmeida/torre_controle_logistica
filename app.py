import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da página executiva
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

# --- Cabeçalho e Proposta de Valor ---
st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #34495e; font-size: 1.1em;'><b>Solução Gerencial:</b> Auditoria Automática de Fretes, Análise de SLA por Estado e Controle de Metas Logísticas.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Carregamento Automatizado dos Dados Expandidos ---
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
    return df

df_original = carregar_dados()

# --- Barra Lateral de Filtros Avançados ---
st.sidebar.header("🎯 Filtros de Processo")

lista_estados = ["Todos"] + sorted(list(df_original["estado"].unique()))
estado_selecionado = st.sidebar.selectbox("Filtro por Estado de Destino:", lista_estados, key="sb_estado")

lista_transportadoras = ["Todos"] + sorted(list(df_original["nome_transportadora"].unique()))
transportadora_selecionada = st.sidebar.selectbox("Filtro por Transportadora (8 Parceiros):", lista_transportadoras, key="sb_transportadora")

lista_segmentos = ["Todos"] + list(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Filtro por Segmento:", lista_segmentos, key="sb_segmento")

# Executando cruzamento na memória
df_filtrado = df_original.copy()
if estado_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_selecionado]
if transportadora_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nome_transportadora"] == transportadora_selecionada]
if segmento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento_operacao"] == segmento_selecionado]


# --- BLOCO 1: Indicadores Comparativos de Eficiência (Métricas vs Metas) ---
st.subheader("📊 Diagnóstico Macro de Eficiência Logística")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_entregas = len(df_filtrado)
    st.metric(label="Volume Processado", value=f"{total_entregas} NFs")

with col2:
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    
    # Avaliação comparativa contra a meta de mercado (95%)
    desvio_meta = taxa_otif - 95.0
    st.metric(
        label="Nível de Serviço (OTIF Atual)", 
        value=f"{taxa_otif:.1f}%", 
        delta=f"{desvio_meta:.1f}% vs Meta (95%)", 
        delta_color="normal" if desvio_meta >= 0 else "inverse"
    )

with col3:
    faturamento_frete = df_filtrado["custo_frete_cobrado"].sum()
    st.metric(label="Gasto Real de Frete", value=f"R$ {faturamento_frete:,.2f}")

with col4:
    df_filtrado["desvio_frete"] = df_filtrado["custo_frete_cobrado"] - df_filtrado["custo_frete_tabela"]
    prejuizo_frete = df_filtrado[df_filtrado["desvio_frete"] > 0]["desvio_frete"].sum()
    
    # Indicador de eficiência de auditoria financeira
    percentual_perda = (prejuizo_frete / faturamento_frete * 100) if faturamento_frete > 0 else 0.0
    st.metric(
        label="Vazamento Financeiro (Cobrança Indevida)", 
        value=f"R$ {prejuizo_frete:,.2f}", 
        delta=f"{percentual_perda:.1f}% de desperdício", 
        delta_color="inverse"
    )

st.markdown("---")


# --- BLOCO 2: Avaliação Dinâmica de Margens de Nível de Serviço ---
if taxa_otif >= 95.0:
    st.success(f"🏅 **Operação em Zona de Excelência:** O nível de serviço atual está em **{taxa_otif:.1f}%**, cumprindo as metas de atendimento mais rígidas do mercado brasileiro.")
elif taxa_otif >= 85.0:
    st.warning(f"⚠️ **Operação em Zona de Atenção:** O nível de serviço está em **{taxa_otif:.1f}%**. A operação apresenta pequenas quebras de processo que precisam ser estancadas antes de gerar multas contratuais.")
else:
    st.error(f"🚨 **Operação em Zona Crítica / Alerta:** O nível de serviço desabou para **{taxa_otif:.1f}%** (Abaixo do limite tolerável de 85%). Há risco iminente de perda de clientes e penalidades comerciais.")

st.markdown("---")


# --- BLOCO 3: Distribuição por Estados e Desempenho Financeiro ---
st.subheader("🗺️ Onde estão os problemas? Quebra por Estado e Transportadora")
graf1, graf2 = st.columns(2)

with graf1:
    # Agrupando performance de nível de serviço por Estado de Destino
    df_estado = df_filtrado.groupby(['estado', 'status_entrega']).size().reset_index(name='quantidade')
    fig_estado = px.bar(
        df_estado, x='estado', y='quantidade', color='status_entrega',
        title="Qualidade do Processo por Destino: Ocorrências Logísticas por Estado",
        labels={'estado': 'Estado de Destino', 'quantidade': 'Qtd de Notas Fiscais'},
        barmode='group'
    )
    st.plotly_chart(fig_estado, use_container_width=True)

with graf2:
    # Comparando o custo acordado versus o faturado por transportadora
    df_custo_transp = df_filtrado.groupby('nome_transportadora')[['custo_frete_tabela', 'custo_frete_cobrado']].sum().reset_index()
    df_melt = df_custo_transp.melt(id_vars='nome_transportadora', value_vars=['custo_frete_tabela', 'custo_frete_cobrado'],
                                   var_name='Tipo_Custo', value_name='Valor')
    df_melt['Tipo_Custo'] = df_melt['Tipo_Custo'].map({'custo_frete_tabela': 'Custo em Contrato', 'custo_frete_cobrado': 'Valor Real Cobrado'})
    
    fig_auditoria = px.bar(
        df_melt, x='Valor', y='nome_transportadora', color='Tipo_Custo', barmode='group',
        title="Auditoria de Contrato: Quem está faturando acima da tabela corporativa?",
        labels={'nome_transportadora': 'Transportadoras Parceiras', 'Valor': 'Montante em R$'},
        orientation='h'
    )
    st.plotly_chart(fig_auditoria, use_container_width=True)

st.markdown("---")


# --- BLOCO 4: Diagnóstico Automatizado de Gargalo ---
st.subheader("🧠 Inteligência de Processos: Resolução de Causa Raiz")
df_erros = df_filtrado[~df_filtrado["status_entrega"].isin(["Entregue No Prazo"])]

if not df_erros.empty:
    causa_raiz = df_erros["motivo_gargalo"].value_counts().idxmax()
    frequencia_causa = df_erros["motivo_gargalo"].value_counts().max()
    
    st.info(f"""
        **Veredito do Diagnóstico Automático:** A principal falha que está derrubando o seu indicador de OTIF e gerando atrito operacional é **"{causa_raiz}"**, afetando diretamente **{frequencia_causa} processos**.
        
        *💡 **Ação Gerencial Recomendada:** Acionar imediatamente o comitê de operações focado nessa causa raiz para mitigar as perdas logísticas e recuperar o nível de serviço exigido em contrato.*
    """)
else:
    st.success("🎉 **Processo Perfeito:** Nenhuma quebra de SLA ou desvio foi registrado sob as condições dos filtros selecionados.")

st.markdown("---")

# --- BLOCO 5: Evidências Operacionais (Tabela) ---
st.subheader("📋 Auditoria de Evidências: Detalhamento Estatístico das NFs")
colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", "estado",
    "segmento_operacao", "data_emissao", "status_entrega", "custo_frete_cobrado", "motivo_gargalo"
]
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True, key="st_df_final")
