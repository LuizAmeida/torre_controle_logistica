import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(page_title="TESTE - DADOS FIXOS", layout="wide")

st.markdown("<h1 style='text-align: center;'>🧪 TESTE - DADOS FIXOS (SEM BANCO)</h1>", unsafe_allow_html=True)
st.markdown("---")

# ============================================
# DADOS FIXOS - APENAS ESTADOS BRASILEIROS
# ============================================
dados = {
    'estado': ['SP', 'RJ', 'MG', 'ES', 'PR', 'SC', 'RS', 'BA', 'CE', 'PE', 'MA', 'GO', 'MT', 'PA', 'AM'],
    'regiao': ['Sudeste', 'Sudeste', 'Sudeste', 'Sudeste', 'Sul', 'Sul', 'Sul', 
               'Nordeste', 'Nordeste', 'Nordeste', 'Nordeste', 
               'Centro-Oeste', 'Centro-Oeste', 'Norte', 'Norte'],
    'status': ['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK'],
    'valor': [1000, 2000, 1500, 3000, 2500, 1800, 2200, 1200, 3500, 2800, 1900, 2100, 1600, 2700, 2300]
}

df = pd.DataFrame(dados)

# ============================================
# MOSTRA OS DADOS
# ============================================
st.write("### 📊 Dados Carregados")
st.dataframe(df)

st.write("---")

# ============================================
# FILTRO DE ESTADOS
# ============================================
st.sidebar.header("🎯 Filtros")

estados = ["Todos"] + sorted(df['estado'].unique())
estado_selecionado = st.sidebar.selectbox("Estado:", estados)

# ============================================
# APLICA FILTRO
# ============================================
df_filtrado = df.copy()

if estado_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

# ============================================
# MÉTRICAS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.metric("Total de Registros", len(df_filtrado))

with col2:
    st.metric("Valor Total", f"R$ {df_filtrado['valor'].sum():,.2f}")

# ============================================
# GRÁFICO
# ============================================
fig = px.bar(
    df_filtrado, 
    x='estado', 
    y='valor',
    title="Valor por Estado"
)
st.plotly_chart(fig, use_container_width=True)

# ============================================
# DEBUG - MOSTRA OS VALORES
# ============================================
st.write("---")
st.write("### 🔍 DEBUG")
st.write(f"**Estados no DataFrame:** {sorted(df['estado'].unique())}")
st.write(f"**Total de estados:** {len(df['estado'].unique())}")
