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

lista_segmentos = ["Todos"] + list(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Selecione o Segmento:", lista_segmentos, key="sb_segmento")

lista_regioes = ["Todos"] + list(df_original["regiao"].unique())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", lista_regioes, key="sb_regiao")

lista_status = ["Todos"] + list(df_original["status_entrega"].unique())
status_selecionado = st.sidebar.selectbox("Status da Entrega:", lista_status, key="sb_status")

lista_transportadoras = ["Todos"] + list(df_original["nome_transportadora"].unique())
transportadora_selecionada = st.sidebar.selectbox("Transportadora:", lista_transportadoras, key="sb_transportadora")

# Aplicando os filtros cruzados
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
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    st.metric(label="Taxa de OTIF (SLA)", value=f"{taxa_otif:.1f}%")

with col4:
    df_filtrado["desvio_frete"] = df_filtrado["custo_frete_cobrado"] - df_filtrado["custo_frete_tabela"]
    prejuizo_frete = df_filtrado[df_filtrado["desvio_frete"] > 0]["desvio_frete"].sum()
    st.metric(label="Prejuízo (Frete Estourado)", value=f"R$ {prejuizo_frete:,.2f}")

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Seção de Destaques Analíticos (Cards em Texto) ---
st.subheader("💡 Destaques Estratégicos da Operação")
col_pos, col_neg = st.columns(2)

with col_pos:
    st.markdown("<h4 style='color: #2ecc71;'>✅ Destaques Positivos</h4>", unsafe_allow_html=True)
    
    if taxa_otif >= 85.0:
        st.write(f"• **Excelente Nível de SLA:** A operação mantém a taxa de OTIF em **{taxa_otif:.1f}%**, cumprindo as janelas de entrega contratuais.")
    else:
        st.write(f"• **Volume Controlado:** Foram processadas **{total_entregas}** entregas sem interrupções críticas de fluxo.")
        
    regiao_top = df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"]["regiao"].value_counts()
    if not regiao_top.empty:
        st.write(f"• **Região Alta Performance:** A região **{regiao_top.index[0]}** registrou a maior volumetria de eficiência e entregas cumpridas dentro do prazo.")

with col_neg:
    st.markdown("<h4 style='color: #e74c3c;'>❌ Destaques Negativos / Alertas</h4>", unsafe_allow_html=True)
    
    if prejuizo_frete > 0:
        st.write(f"• **Distorção de Custo:** Identificado vazamento de margem de **R$ {prejuizo_frete:,.2f}** referente a faturamentos acima da tabela contratada.")
    else:
        st.write("• **Eficiência Financeira:** Nenhuma transportadora cobrou valores acima da tabela contratada.")
        
    qtd_atrasados = len(df_filtrado[df_filtrado["status_entrega"] == "Atrasado"])
    if qtd_atrasados > 0:
        st.write(f"• **Atrasos Identificados:** Há **{qtd_atrasados}** entregas fora do prazo estipulado penalizando o lead time.")
    else:
        st.write("• **Risco Zero de Atraso:** Não constam entregas indevidas em atraso sob o filtro atual.")

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Bloco Gráfico Ajustado ---
st.subheader("📈 Volumetria e Distribuição de SLAs")
graf1, graf2 = st.columns(2)

with graf1:
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
    if status_selecionado != "Todos":
        df_pizza_dados = df_original.copy()
        if segmento_selecionado != "Todos":
            df_pizza_dados = df_pizza_dados[df_pizza_dados["segmento_operacao"] == segmento_selecionado]
        if regiao_selecionada != "Todos":
            df_pizza_dados = df_pizza_dados[df_pizza_dados["regiao"] == regiao_selecionada]
        if transportadora_selecionada != "Todos":
            df_pizza_dados = df_pizza_dados[df_pizza_dados["nome_transportadora"] == transportadora_selecionada]
        title_pizza = "Visão Geral de Status no Contexto Atual"
    else:
        df_pizza_dados = df_filtrado
        title_pizza = "Distribuição Geral por Status de Entrega"

    df_pizza = df_pizza_dados["status_entrega"].value_counts().reset_index()
    df_pizza.columns = ["Status", "Quantidade"]
    
    fig_pizza = px.pie(
        df_pizza, 
        names="Status", 
        values="Quantidade", 
        title=title_pizza,
        hole=0.4
    )
    st.plotly_chart(fig_pizza, use_container_width=True)


# --- CONSTRUÇÃO/MODIFICAÇÃO: Bloco Gráfico Bloco 2 ---
st.subheader("🚛 Performance de Parceiros e Auditoria de Custos")
graf3, graf4 = st.columns(2)

with graf3:
    df_transp = df_filtrado.groupby(['nome_transportadora', 'status_entrega']).size().reset_index(name='entregas')
    fig_barra_transp = px.bar(
        df_transp,
        x='nome_transportadora',
        y='entregas',
        color='status_entrega',
        title="Nível de Serviço (SLA) por Transportadora",
        labels={'nome_transportadora': 'Transportadora', 'entregas': 'Quantidade de Viagens'},
        barmode='stack'
    )
    st.plotly_chart(fig_barra_transp, use_container_width=True)

with graf4:
    df_custos = df_filtrado.groupby('segmento_operacao')[['custo_frete_tabela', 'custo_frete_cobrado']].sum().reset_index()
    df_custos_melt = df_custos.melt(id_vars='segmento_operacao', value_vars=['custo_frete_tabela', 'custo_frete_cobrado'],
                                    var_name='Tipo_Custo', value_name='Valor')
    df_custos_melt['Tipo_Custo'] = df_custos_melt['Tipo_Custo'].map({'custo_frete_tabela': 'Frete Contratado (Tabela)', 'custo_frete_cobrado': 'Frete Real Cobrado'})
    
    fig_comparativo = px.bar(
        df_custos_melt,
        x='segmento_operacao',
        y='Valor',
        color='Tipo_Custo',
        barmode='group',
        title="Auditoria Financeira: Frete Contratado vs Frete Real Cobrado",
        labels={'segmento_operacao': 'Segmento Operacional', 'Valor': 'Montante em R$'}
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Diagnóstico Automatizado (Removida a Chave Conflitante) ---
st.subheader("🧠 Diagnóstico Automatizado de Gargalos Logísticos")

df_erros = df_filtrado[df_filtrado["motivo_gargalo"] != "Nenhum Operacional"]
df_erros = df_erros[df_erros["motivo_gargalo"] != "Carga em Fluxo Normal"]

if not df_erros.empty:
    causa_raiz = df_erros["motivo_gargalo"].value_counts().idxmax()
    frequencia_causa = df_erros["motivo_gargalo"].value_counts().max()
    
    # Removido o parâmetro key daqui para evitar o conflito no SessionState
    st.info(f"""
        **Análise de Causa Raiz:** Identificamos que o principal gargalo operacional sob o filtro selecionado é **"{causa_raiz}"**, ocorrendo em **{frequencia_causa}** incidentes afetando o nível de serviço do período. 
        *Recomendação Operacional: Revisar o processo de agendamento ou acionar a mesa de operações para mitigar novos atrasos desse tipo.*
    """)
else:
    # Removido o parâmetro key daqui para evitar o conflito no SessionState
    st.success("🎉 **Eficiência Total:** Nenhum desvio de fluxo ou gargalo operacional foi registrado sob as condições dos filtros atuais.")

st.markdown("---")


# --- CONSTRUÇÃO/MODIFICAÇÃO: Tabela de Dados Operacionais ---
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")

colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", 
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]

# Mantida uma única chave de controle exclusiva para o elemento da tabela
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True, key="st_df_final")
