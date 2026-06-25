import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da página do Streamlit para o usuário final
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

# --- BLOCO 1: Proposta de Valor e Dor do Cliente ---
st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #34495e; font-size: 1.1em;'><b>Solução Gerencial:</b> Auditoria automática de tabelas de frete e monitoramento inteligente de prazos de entrega (SLA).</p>", unsafe_allow_html=True)

# Caixa explicativa da Mágica (O que o sistema resolve)
st.markdown("""
> **Como esta solução protege sua margem de lucro:** Este painel centraliza as notas fiscais da sua operação para resolver dois problemas invisíveis: o pagamento de fretes faturados acima do contrato corporativo (*vazamento de caixa*) e a perda de clientes devido a atrasos sem justificativa aparente.
""")
st.markdown("---")

# --- Carregamento de Dados (A Mágica por trás das cortinas) ---
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

# --- Painel de Filtros Decisórios (Barra Lateral) ---
st.sidebar.header("🎯 Filtros Estratégicos")
st.sidebar.markdown("Use os seletores abaixo para isolar cenários ou avaliar parceiros específicos:")

lista_segmentos = ["Todos"] + list(df_original["segmento_operacao"].unique())
segmento_selecionado = st.sidebar.selectbox("Filtro por Canal/Segmento de Negócio:", lista_segmentos, key="sb_segmento")

lista_regioes = ["Todos"] + list(df_original["regiao"].unique())
regiao_selecionada = st.sidebar.selectbox("Filtro por Região Geográfica:", lista_regioes, key="sb_regiao")

lista_status = ["Todos"] + list(df_original["status_entrega"].unique())
status_selecionado = st.sidebar.selectbox("Filtro por Situação da Entrega:", lista_status, key="sb_status")

lista_transportadoras = ["Todos"] + list(df_original["nome_transportadora"].unique())
transportadora_selecionada = st.sidebar.selectbox("Filtro por Transportadora Parceira:", lista_transportadoras, key="sb_transportadora")

# Processamento dinâmico dos filtros na memória
df_filtrado = df_original.copy()

if segmento_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento_operacao"] == segmento_selecionado]
if regiao_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["regiao"] == regiao_selecionada]
if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status_entrega"] == status_selecionado]
if transportadora_selecionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["nome_transportadora"] == transportadora_selecionada]


# --- BLOCO 2: Separação de KPIs por Indicadores de Negócio ---
st.subheader("📊 Resumo Analítico da Operação")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_entregas = len(df_filtrado)
    st.metric(label="Volume de Pedidos Atendidos", value=f"{total_entregas} NFs")

with col2:
    faturamento_frete = df_filtrado["custo_frete_cobrado"].sum()
    st.metric(label="Gasto Real com Transporte", value=f"R$ {faturamento_frete:,.2f}")

with col3:
    entregas_no_prazo = len(df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"])
    taxa_otif = (entregas_no_prazo / total_entregas * 100) if total_entregas > 0 else 0.0
    st.metric(label="Nível de Serviço Cumprido (SLA / OTIF)", value=f"{taxa_otif:.1f}%")

with col4:
    df_filtrado["desvio_frete"] = df_filtrado["custo_frete_cobrado"] - df_filtrado["custo_frete_tabela"]
    prejuizo_frete = df_filtrado[df_filtrado["desvio_frete"] > 0]["desvio_frete"].sum()
    st.metric(label="Cobranças Indevidas Detectadas", value=f"R$ {prejuizo_frete:,.2f}", delta=f"R$ {prejuizo_frete:,.2f}", delta_color="inverse")

st.markdown("---")


# --- BLOCO 3: Destaques Estratégicos Sem Contradição Lógica ---
st.subheader("💡 Conclusões Rápidas para Tomada de Decisão")
col_pos, col_neg = st.columns(2)
total_fora_prazo = total_entregas - entregas_no_prazo

with col_pos:
    st.markdown("<h4 style='color: #2ecc71;'>✅ Recuperação Financeira e Eficiência</h4>", unsafe_allow_html=True)
    if prejuizo_frete > 0:
        st.write(f"• **Alvo de Auditoria:** Identificamos **R$ {prejuizo_frete:,.2f}** cobrados de forma indevida (acima do contrato). Esse valor está pronto para ser contestado e ressarcido.")
    else:
        st.write("• **Sincronia Financeira:** 100% dos fretes cobrados estão em conformidade com as tabelas acordadas.")
        
    regiao_top = df_filtrado[df_filtrado["status_entrega"] == "Entregue No Prazo"]["regiao"].value_counts()
    if not regiao_top.empty:
        st.write(f"• **Destaque de Entrega:** A região **{regiao_top.index[0]}** lidera o ranking de cumprimento de prazos ao cliente final.")

with col_neg:
    st.markdown("<h4 style='color: #e74c3c;'>❌ Perda de Margem e Gargalos Ativos</h4>", unsafe_allow_html=True)
    if total_fora_prazo > 0:
        st.write(f"• **Atrito de Cliente:** Há **{total_fora_prazo} pedidos** que sofreram desvios de prazo ou estão retidos, impactando o índice de satisfação operacional.")
    else:
        st.write("• **Risco Controlado:** Nenhuma quebra de SLA ou retenção foi identificada sob as condições atuais.")
        
    if prejuizo_frete > 0:
        st.write(f"• **Vazamento Logístico:** Custos operacionais inflacionados devido a erros de cobrança por parte dos parceiros de transporte.")

st.markdown("---")


# --- BLOCO 4: Gráficos com Títulos Explicativos de Negócio ---
st.subheader("📈 Análise de Tendências e Visões de Mercado")
graf1, graf2 = st.columns(2)

with graf1:
    df_linha = df_filtrado.groupby(['data_emissao', 'regiao']).size().reset_index(name='qtd_entregas')
    df_linha = df_linha.sort_values(by='data_emissao')
    fig_linha = px.line(
        df_linha, x='data_emissao', y='qtd_entregas', color='regiao',
        title="Onde estão os pedidos? Volume de Movimentações por Região Comercial",
        labels={'data_emissao': 'Data de Emissão da NF', 'qtd_entregas': 'Quantidade de Notas'},
        markers=True
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with graf2:
    if status_selecionado != "Todos":
        df_pizza_dados = df_original.copy()
        if segmento_selecionado != "Todos": df_pizza_dados = df_pizza_dados[df_pizza_dados["segmento_operacao"] == segmento_selecionado]
        if regiao_selecionada != "Todos": df_pizza_dados = df_pizza_dados[df_pizza_dados["regiao"] == regiao_selecionada]
        if transportadora_selecionada != "Todos": df_pizza_dados = df_pizza_dados[df_pizza_dados["nome_transportadora"] == transportadora_selecionada]
        title_pizza = "Qualidade Real do SLA: Distribuição de Ocorrências no Contexto Atual"
    else:
        df_pizza_dados = df_filtrado
        title_pizza = "Qualidade Real do SLA: Distribuição Geral por Status de Cumprimento de Prazo"

    df_pizza = df_pizza_dados["status_entrega"].value_counts().reset_index()
    df_pizza.columns = ["Status", "Quantidade"]
    fig_pizza = px.pie(df_pizza, names="Status", values="Quantidade", title=title_pizza, hole=0.4)
    st.plotly_chart(fig_pizza, use_container_width=True)

st.markdown("---")


# --- BLOCO 5: Gráficos de Auditoria de Custos e SLA ---
st.subheader("🚛 Avaliação de Performance de Parceiros e Auditoria de Contratos")
graf3, graf4 = st.columns(2)

with graf3:
    df_transp = df_filtrado.groupby(['nome_transportadora', 'status_entrega']).size().reset_index(name='entregas')
    fig_barra_transp = px.bar(
        df_transp, x='nome_transportadora', y='entregas', color='status_entrega',
        title="Quem entrega melhor? Comparativo de Cumprimento de Prazos por Transportadora",
        labels={'nome_transportadora': 'Transportadora Parceira', 'entregas': 'Total de Viagens Financiadas'},
        barmode='stack'
    )
    st.plotly_chart(fig_barra_transp, use_container_width=True)

with graf4:
    df_custos = df_filtrado.groupby('segmento_operacao')[['custo_frete_tabela', 'custo_frete_cobrado']].sum().reset_index()
    df_custos_melt = df_custos.melt(id_vars='segmento_operacao', value_vars=['custo_frete_tabela', 'custo_frete_cobrado'],
                                    var_name='Tipo_Custo', value_name='Valor')
    df_custos_melt['Tipo_Custo'] = df_custos_melt['Tipo_Custo'].map({'custo_frete_tabela': 'Custo Acordado (Tabela Contrato)', 'custo_frete_cobrado': 'Custo Real Cobrado (Faturamento)'})
    fig_comparativo = px.bar(
        df_custos_melt, x='segmento_operacao', y='Valor', color='Tipo_Custo', barmode='group',
        title="Onde está o vazamento de caixa? Custo Contratado vs. Custo Cobrado por Segmento",
        labels={'segmento_operacao': 'Canal de Vendas / Operação', 'Valor': 'Montante Financeiro (R$)'}
    )
    st.plotly_chart(fig_comparativo, use_container_width=True)

st.markdown("---")


# --- BLOCO 6: Diagnóstico de Causa Raiz Automatizado ---
st.subheader("🧠 Inteligência de Negócio: Diagnóstico de Gargalos da Operação")
container_diagnostico = st.container()

with container_diagnostico:
    df_erros = df_filtrado[df_filtrado["motivo_gargalo"] != "Nenhum Operacional"]
    df_erros = df_erros[df_erros["motivo_gargalo"] != "Carga em Fluxo Normal"]

    if not df_erros.empty:
        causa_raiz = df_erros["motivo_gargalo"].value_counts().idxmax()
        frequencia_causa = df_erros["motivo_gargalo"].value_counts().max()
        
        st.info(f"""
            **Mapeamento de Causa Raiz:** O principal gargalo que está gerando a quebra de nível de serviço no cenário atual é **"{causa_raiz}"**, registrando **{frequencia_causa} ocorrências**.
            
            *📌 **Por que utilizar esta inteligência?** Sem esta ferramenta, sua equipe passaria dias abrindo ocorrências de forma manual ou planilhada. O sistema cruza os dados e aponta instantaneamente onde o processo está quebrando, permitindo renegociar metas com as transportadoras e estancar perdas.*
        """)
    else:
        st.success("🎉 **Eficiência Máxima:** Nenhum desvio operacional ou quebra de fluxo foi registrado sob as condições dos filtros aplicados.")

st.markdown("---")


# --- BLOCO 7: Detalhes das Evidências (Tabela Operacional) ---
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")
colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", 
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True, key="st_df_final")
