import sqlite3
import random
from datetime import datetime, timedelta
import os

def criar_e_povoar_banco():
    """
    Cria e popula o banco de dados com dados oficiais.
    """
    
    db_path = "torre_controle_final.db"
    
    # Remove o banco se existir
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"🗑️ Banco removido: {db_path}")
        except Exception as e:
            print(f"⚠️ Erro ao remover banco: {e}")
    
    # Conexão
    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()

    # ========== LIMPEZA ==========
    print("🔄 Limpando tabelas existentes...")
    cursor.execute("DROP TABLE IF EXISTS f_entregas;")
    cursor.execute("DROP TABLE IF EXISTS d_transportadoras;")
    cursor.execute("DROP TABLE IF EXISTS d_clientes;")
    print("✅ Tabelas removidas")

    # ========== CRIAÇÃO ==========
    print("🔄 Criando estrutura das tabelas...")
    
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
            faturamento_status TEXT,
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
    print("✅ Estrutura criada")

    # ========== TRANSPORTADORAS ==========
    print("🔄 Cadastrando transportadoras...")
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
    print(f"✅ {len(transportadoras)} transportadoras cadastradas")

    # ========== CLIENTES ==========
    print("🔄 Cadastrando clientes...")
    
    clientes = [
        # SUDESTE (4)
        ("CD São Paulo", "São Paulo", "SP", "Sudeste"),
        ("Filial Rio de Janeiro", "Rio de Janeiro", "RJ", "Sudeste"),
        ("Atacado Belo Horizonte", "Belo Horizonte", "MG", "Sudeste"),
        ("Operador Vitória", "Vitória", "ES", "Sudeste"),
        # SUL (3)
        ("Cooperativa Curitiba", "Curitiba", "PR", "Sul"),
        ("Logística Joinville", "Joinville", "SC", "Sul"),
        ("Terminal Porto Alegre", "Porto Alegre", "RS", "Sul"),
        # NORDESTE (4)
        ("Distribuidora Salvador", "Salvador", "BA", "Nordeste"),
        ("Hub Fortaleza", "Fortaleza", "CE", "Nordeste"),
        ("Polo Recife", "Recife", "PE", "Nordeste"),
        ("Logística São Luís", "São Luís", "MA", "Nordeste"),
        # CENTRO-OESTE (2)
        ("Agro Goiânia", "Goiânia", "GO", "Centro-Oeste"),
        ("Plataforma Cuiabá", "Cuiabá", "MT", "Centro-Oeste"),
        # NORTE (2)
        ("Norte Belém", "Belém", "PA", "Norte"),
        ("Polo Manaus", "Manaus", "AM", "Norte")
    ]
    cursor.executemany("INSERT INTO d_clientes (nome_cliente, cidade, estado, regiao) VALUES (?, ?, ?, ?);", clientes)
    print(f"✅ {len(clientes)} clientes cadastrados")

    # ========== VERIFICAÇÃO DOS ESTADOS ==========
    cursor.execute("SELECT DISTINCT estado FROM d_clientes ORDER BY estado;")
    estados_cadastrados = [row[0] for row in cursor.fetchall()]
    print(f"📍 Estados cadastrados: {estados_cadastrados}")
    
    estados_validos = ['AM', 'BA', 'CE', 'ES', 'GO', 'MA', 'MG', 'MT', 'PA', 'PE', 'PR', 'RJ', 'RS', 'SC', 'SP']
    
    # VERIFICA SE TEM ALGO ERRADO
    for estado in estados_cadastrados:
        if estado not in estados_validos:
            print(f"🚨 ERRO: Estado inválido encontrado: '{estado}'")
            cursor.execute(f"DELETE FROM d_clientes WHERE estado = '{estado}';")
            print(f"✅ Estado '{estado}' removido")
    
    conexao.commit()

    # ========== DADOS DAS ENTREGAS ==========
    print("🔄 Gerando 100 notas fiscais...")
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

    print("✅ 100 notas fiscais geradas")

    # ========== VALIDAÇÃO FINAL ==========
    print("\n🔍 VALIDAÇÃO FINAL...")
    
    # Verifica estados
    cursor.execute("SELECT DISTINCT estado FROM d_clientes ORDER BY estado;")
    estados_finais = [row[0] for row in cursor.fetchall()]
    print(f"📍 Estados finais no banco: {estados_finais}")
    
    # Verifica se todos os estados são válidos
    estados_validos = ['AM', 'BA', 'CE', 'ES', 'GO', 'MA', 'MG', 'MT', 'PA', 'PE', 'PR', 'RJ', 'RS', 'SC', 'SP']
    for estado in estados_finais:
        if estado not in estados_validos:
            print(f"🚨 ERRO CRÍTICO: Estado inválido encontrado: '{estado}'")
            cursor.execute(f"DELETE FROM d_clientes WHERE estado = '{estado}';")
    
    # Verifica novamente
    cursor.execute("SELECT DISTINCT estado FROM d_clientes ORDER BY estado;")
    estados_finais = [row[0] for row in cursor.fetchall()]
    print(f"✅ Estados FINAIS após validação: {estados_finais}")
    
    # Verifica se são exatamente 15 estados
    if len(estados_finais) == 15:
        print("✅ Todos os 15 estados estão corretos!")
    else:
        print(f"⚠️ ATENÇÃO: Tem {len(estados_finais)} estados, esperado 15")
        print(f"   Estados: {estados_finais}")

    # Verifica se as tabelas existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [row[0] for row in cursor.fetchall()]
    print(f"📋 Tabelas no banco: {tabelas}")
    
    if 'f_entregas' not in tabelas:
        print("🚨 ERRO CRÍTICO: Tabela f_entregas não foi criada!")
    else:
        cursor.execute("SELECT COUNT(*) FROM f_entregas;")
        total = cursor.fetchone()[0]
        print(f"✅ Total de entregas: {total}")

    conexao.commit()
    conexao.close()
    print("✅ Banco de dados gerado com sucesso!")

if __name__ == "__main__":
    criar_e_povoar_banco()
