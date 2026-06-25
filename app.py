import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime
import sys

# ============================================
# DIAGNÓSTICO RADICAL - ANTES DE TUDO
# ============================================
print("=" * 60)
print("DIAGNÓSTICO COMPLETO DO BANCO DE DADOS")
print("=" * 60)

db_path = "torre_controle_final.db"

# 1. LISTA TODOS OS ARQUIVOS DO DIRETÓRIO
print(f"\n📁 Arquivos no diretório {os.getcwd()}:")
for arquivo in os.listdir('.'):
    if os.path.isfile(arquivo):
        print(f"  - {arquivo} ({os.path.getsize(arquivo)} bytes)")

# 2. VERIFICA O BANCO
print(f"\n📊 Verificando banco: {db_path}")
if os.path.exists(db_path):
    print(f"  ✅ Banco encontrado - Tamanho: {os.path.getsize(db_path)} bytes")
    
    # Lê diretamente do banco SEM usar pandas
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    print(f"\n  📋 Tabelas encontradas: {[t[0] for t in tabelas]}")
    
    # Verifica cada tabela
    for tabela in tabelas:
        nome = tabela[0]
        cursor.execute(f"SELECT COUNT(*) FROM {nome}")
        count = cursor.fetchone()[0]
        print(f"    - {nome}: {count} registros")
        
        # Mostra os primeiros registros de cada tabela
        if count > 0 and count <= 5:
            cursor.execute(f"SELECT * FROM {nome}")
            amostra = cursor.fetchall()
            print(f"      Amostra: {amostra}")
    
    # VERIFICA ESPECIFICAMENTE A TABELA d_clientes
    print("\n  🔍 VERIFICANDO d_clientes (PROBLEMA):")
    cursor.execute("SELECT id_cliente, nome_cliente, cidade, estado, regiao FROM d_clientes ORDER BY estado;")
    clientes = cursor.fetchall()
    print(f"    Total de clientes: {len(clientes)}")
    for cliente in clientes:
        print(f"    ID: {cliente[0]} | Nome: {cliente[1]} | Cidade: {cliente[2]} | Estado: '{cliente[3]}' | Região: {cliente[4]}")
    
    # VERIFICA SE HÁ ESTADOS ESTRANHOS
    cursor.execute("SELECT DISTINCT estado FROM d_clientes;")
    estados = [row[0] for row in cursor.fetchall()]
    print(f"\n  📍 ESTADOS ENCONTRADOS: {estados}")
    
    estados_validos = ['AM', 'BA', 'CE', 'ES', 'GO', 'MA', 'MG', 'MT', 'PA', 'PE', 'PR', 'RJ', 'RS', 'SC', 'SP']
    for estado in estados:
        if estado not in estados_validos:
            print(f"  🚨 ESTADO INVÁLIDO DETECTADO: '{estado}'")
    
    conn.close()
else:
    print("  ❌ Banco NÃO encontrado!")

print("=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)

# ============================================
# CONTINUAÇÃO DO SEU CÓDIGO ORIGINAL
# ============================================

# Remove as linhas antigas que tentavam recriar o banco
# if os.path.exists("torre_controle_final.db"):  <-- COMENTE OU REMOVA ISSO
#     try:
#         os.remove("torre_controle_final.db")
#     except Exception:
#         pass

# try:  <-- COMENTE OU REMOVA ISSO
#     import gerar_banco
#     gerar_banco.criar_e_povoar_banco()
# except Exception:
#     pass

# Configuração da página executiva profissional
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

# ========== DIAGNÓSTICO INICIAL ==========
print("=== DIAGNÓSTICO INICIAL ===")
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivos no diretório: {os.listdir()}")

# ========== SETUP FORÇADO DO BANCO ==========
db_path = "torre_controle_final.db"

# Remove banco antigo se existir
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✅ Banco antigo removido: {db_path}")
    except Exception as e:
        print(f"⚠️ Erro ao remover banco antigo: {e}")

# Recria o banco do zero
try:
    import gerar_banco
    print("🔄 Executando gerar_banco.criar_e_povoar_banco()...")
    gerar_banco.criar_e_povoar_banco()
    print("✅ Banco recriado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao recriar banco: {e}")
    # Tenta executar via subprocess como fallback
    try:
        print("🔄 Tentando fallback com subprocess...")
        subprocess.run([sys.executable, "gerar_banco.py"], check=True, capture_output=False)
        print("✅ Banco recriado via subprocess!")
    except Exception as e2:
        print(f"❌ Erro no fallback: {e2}")

# Verifica se o banco foi criado
if os.path.exists(db_path):
    tamanho = os.path.getsize(db_path)
    print(f"📊 Banco criado: {tamanho} bytes")
    
    # Verifica os dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [row[0] for row in cursor.fetchall()]
    print(f"📋 Tabelas no banco: {tabelas}")
    
    # Verifica estados (PROBLEMA PRINCIPAL)
    if 'd_clientes' in tabelas:
        cursor.execute("SELECT DISTINCT estado FROM d_clientes ORDER BY estado;")
        estados = [row[0] for row in cursor.fetchall()]
        print(f"📍 Estados cadastrados: {estados}")
        
        cursor.execute("SELECT DISTINCT regiao FROM d_clientes ORDER BY regiao;")
        regioes = [row[0] for row in cursor.fetchall()]
        print(f"📍 Regiões cadastradas: {regioes}")
        
        cursor.execute("SELECT DISTINCT segmento_operacao FROM f_entregas ORDER BY segmento_operacao;")
        segmentos = [row[0] for row in cursor.fetchall()]
        print(f"📍 Segmentos cadastrados: {segmentos}")
    
    conn.close()
else:
    print("❌ Banco NÃO foi criado!")
    st.error("⚠️ Banco de dados não foi criado. Verifique os logs.")
    st.stop()

print("=== FIM DIAGNÓSTICO ===")
# ==========================================

# Configuração da página executiva profissional
st.set_page_config(page_title="Torre de Controle Logística", layout="wide")

st.markdown("<h1 style='text-align: center;'>🛸 Torre de Performance Logística</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Solução Gerencial: Auditoria Automática de Fretes, Análise de SLA e Controle de Metas</p>", unsafe_allow_html=True)
st.markdown("---")

# Carregamento estrito e direto do banco torre_controle_final.db com controle de expiração de cache
@st.cache_data(ttl=0, show_spinner=False)  # ttl=0 força recarregar sempre
def carregar_dados():
    # Verifica se o banco existe antes de carregar
    if not os.path.exists("torre_controle_final.db"):
        st.error("⚠️ Banco de dados não encontrado!")
        return pd.DataFrame()
    
    try:
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
        
        # Converte colunas de data
        df['data_emissao'] = pd.to_datetime(df['data_emissao'])
        
        # VALIDAÇÃO: Verifica se há dados estranhos
        estados_validos = ['AM', 'BA', 'CE', 'ES', 'GO', 'MA', 'MG', 'MT', 'PA', 'PE', 'PR', 'RJ', 'RS', 'SC', 'SP']
        estados_encontrados = df['estado'].unique()
        
        for estado in estados_encontrados:
            if estado not in estados_validos:
                print(f"⚠️ ALERTA: Estado inválido encontrado: '{estado}'")
                # Força a remoção de dados inválidos
                df = df[df['estado'].isin(estados_validos)]
                print(f"🔄 Removidos registros com estado inválido. Total restante: {len(df)}")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_original = carregar_dados()

# Verifica se o DataFrame está vazio
if df_original.empty:
    st.error("⚠️ Nenhum dado disponível para análise. Verifique o banco de dados.")
    st.stop()

# Construção do Painel de Filtros Cruzados com a Linha Temporal Integrada
st.sidebar.header("🎯 Painel de Filtros Cruzados")

data_minima = df_original["data_emissao"].min().date()
data_maxima = df_original["data_emissao"].max().date()

st.sidebar.markdown("📅 **Filtro por Período Temporal:**")
periodo_selecionado = st.sidebar.date_input(
    "Selecione o intervalo de análise:",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima,
    key="sb_datas"
)

st.sidebar.markdown("---")

# Filtros com validação para evitar dados estranhos
lista_segmentos = ["Todos"] + sorted([s for s in df_original["segmento_operacao"].unique() if s and str(s).strip()])
segmento_selecionado = st.sidebar.selectbox("Selecione o Segmento:", lista_segmentos, key="sb_segmento")

lista_regioes = ["Todos"] + sorted([r for r in df_original["regiao"].unique() if r and str(r).strip()])
regiao_selecionada = st.sidebar.selectbox("Selecione a Região Geográfica:", lista_regioes, key="sb_regiao")

lista_estados = ["Todos"] + sorted([e for e in df_original["estado"].unique() if e and str(e).strip() and len(str(e)) <= 2])
estado_selecionado = st.sidebar.selectbox("Selecione o Estado de Destino:", lista_estados, key="sb_estado")

lista_status = ["Todos"] + [s for s in df_original["status_entrega"].unique() if s and str(s).strip()]
status_selecionado = st.sidebar.selectbox("Status da Entrega:", lista_status, key="sb_status")

lista_transportadoras = ["Todos"] + sorted([t for t in df_original["nome_transportadora"].unique() if t and str(t).strip()])
transportadora_selecionada = st.sidebar.selectbox("Transportadora:", lista_transportadoras, key="sb_transportadora")

# Processamento dinâmico dos filtros na memória
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

# Verifica se o DataFrame filtrado está vazio
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# Indicadores de Performance Operacional
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

# Bloco Gráfico 1 e 2
st.subheader("📈 Volumetria e Distribuição de SLAs")
graf1, graf2 = st.columns(2)

with graf1:
    df_estado = df_filtrado.groupby(['estado', 'status_entrega']).size().reset_index(name='quantidade')
    fig_estado = px.bar(
        df_estado, x='estado', y='quantidade', color='status_entrega',
        title="Ocorrências Logísticas por Estado de Destino (15 Estados)",
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

# Bloco Gráfico 3 e 4
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

# Tabela Operacional de Detalhamento
st.subheader("📋 Detalhamento das Notas Fiscais e Ocorrências")
colunas_exibicao = [
    "numero_nota_fiscal", "nome_transportadora", "nome_cliente", "estado",
    "regiao", "segmento_operacao", "data_emissao", "status_entrega", 
    "valor_nota_fiscal", "custo_frete_cobrado", "motivo_gargalo"
]
st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True, key="st_df_final")
