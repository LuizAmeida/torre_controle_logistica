import sqlite3
import random
from datetime import datetime, timedelta
import os

def criar_e_povoar_banco():
    """Cria banco de dados com todas as métricas operacionais completas"""
    
    db_path = "torre_controle_final.db"
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ Banco antigo removido")
        except Exception as e:
            print(f"⚠️ Erro ao remover: {e}")
    
    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()

    # ========== LIMPEZA ==========
    cursor.execute("DROP TABLE IF EXISTS f_entregas;")
    cursor.execute("DROP TABLE IF EXISTS d_transportadoras;")
    cursor.execute("DROP TABLE IF EXISTS d_clientes;")
    cursor.execute("DROP TABLE IF EXISTS d_motoristas;")
    cursor.execute("DROP TABLE IF EXISTS d_veiculos;")
    cursor.execute("DROP TABLE IF EXISTS d_fornecedores;")

    # ========== TABELAS DIMENSÃO ==========
    
    cursor.execute("""
        CREATE TABLE d_transportadoras (
            id_transportadora INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_transportadora TEXT NOT NULL,
            tipo_transporte TEXT,
            modalidade TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE d_fornecedores (
            id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_fornecedor TEXT NOT NULL,
            cidade TEXT,
            estado TEXT,
            segmento TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE d_motoristas (
            id_motorista INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_motorista TEXT NOT NULL,
            codigo_motorista TEXT,
            cnh TEXT,
            data_admissao TEXT,
            categoria_cnh TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE d_veiculos (
            id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            modelo TEXT,
            fabricante TEXT,
            tipo_veiculo TEXT,
            capacidade_kg REAL,
            ano_fabricacao INTEGER,
            km_inicial REAL,
            data_aquisicao TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE d_clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL,
            cidade TEXT,
            estado TEXT,
            regiao TEXT,
            tipo_destino TEXT
        );
    """)

    # ========== TABELA FATO COMPLETA ==========
    cursor.execute("""
        CREATE TABLE f_entregas (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_nota_fiscal TEXT NOT NULL,
            data_emissao TEXT,
            data_entrega_real TEXT,
            data_prevista_entrega TEXT,
            id_transportadora INTEGER,
            id_motorista INTEGER,
            id_veiculo INTEGER,
            id_cliente INTEGER,
            id_fornecedor INTEGER,
            tipo_operacao TEXT,
            segmento_operacao TEXT,
            
            -- Métricas financeiras
            valor_nota_fiscal REAL,
            peso_kg REAL,
            volume_m3 REAL,
            custo_frete_tabela REAL,
            custo_frete_cobrado REAL,
            custo_frete_real REAL,
            valor_mercadoria REAL,
            
            -- Métricas de frota própria
            km_rodados REAL,
            km_inicial_viagem REAL,
            km_final_viagem REAL,
            litros_combustivel REAL,
            custo_combustivel REAL,
            custo_manutencao REAL,
            custo_pedagio REAL,
            custo_horas_trabalhadas REAL,
            horas_trabalhadas REAL,
            
            -- Métricas de produtividade
            entregas_dia INTEGER,
            tempo_viagem_horas REAL,
            tempo_carregamento_horas REAL,
            tempo_descarga_horas REAL,
            numero_paradas INTEGER,
            tempo_paradas_minutos REAL,
            
            -- Métricas de qualidade
            status_entrega TEXT,
            motivo_gargalo TEXT,
            avarias BOOLEAN,
            valor_avaria REAL,
            qtd_avarias INTEGER,
            nota_satisfacao INTEGER,
            reclamacao_cliente BOOLEAN,
            
            FOREIGN KEY (id_transportadora) REFERENCES d_transportadoras(id_transportadora),
            FOREIGN KEY (id_motorista) REFERENCES d_motoristas(id_motorista),
            FOREIGN KEY (id_veiculo) REFERENCES d_veiculos(id_veiculo),
            FOREIGN KEY (id_cliente) REFERENCES d_clientes(id_cliente),
            FOREIGN KEY (id_fornecedor) REFERENCES d_fornecedores(id_fornecedor)
        );
    """)

    # ========== POPULA FORNECEDORES ==========
    print("🔄 Cadastrando fornecedores...")
    fornecedores = [
        ("Móveis Brasil LTDA", "São Paulo", "SP", "Móveis"),
        ("Eletro Norte Indústria", "Manaus", "AM", "Eletrodomésticos"),
        ("Tech Eletrônicos", "São Paulo", "SP", "Eletrônicos"),
        ("Deco Casa", "Curitiba", "PR", "Decoração"),
        ("Móveis Sul", "Porto Alegre", "RS", "Móveis"),
        ("Eletro Brasil", "Rio de Janeiro", "RJ", "Eletrodomésticos"),
        ("Iluminação BR", "São Paulo", "SP", "Iluminação"),
        ("Utilidades Domésticas", "Belo Horizonte", "MG", "Utensílios")
    ]
    cursor.executemany("INSERT INTO d_fornecedores (nome_fornecedor, cidade, estado, segmento) VALUES (?, ?, ?, ?);", fornecedores)

    # ========== POPULA TRANSPORTADORAS ==========
    print("🔄 Cadastrando transportadoras...")
    transportadoras = [
        ("Alfa Transportes", "Lotação", "externa"),
        ("Beta Logística", "Fracionado", "externa"),
        ("Gama Express", "Fracionado", "externa"),
        ("Delta Cargas", "Lotação", "externa"),
        ("Frota Própria - SP", "Domicílio", "propria"),
        ("Frota Própria - RJ", "Domicílio", "propria"),
        ("Frota Própria - MG", "Domicílio", "propria"),
        ("Frota Própria - PR", "Domicílio", "propria")
    ]
    cursor.executemany("INSERT INTO d_transportadoras (nome_transportadora, tipo_transporte, modalidade) VALUES (?, ?, ?);", transportadoras)

    # ========== POPULA MOTORISTAS ==========
    print("🔄 Cadastrando motoristas...")
    motoristas = [
        ("João Silva", "MOT-001", "12345678901", "2020-01-15", "E"),
        ("Carlos Santos", "MOT-002", "23456789012", "2021-03-10", "D"),
        ("Maria Oliveira", "MOT-003", "34567890123", "2019-06-20", "E"),
        ("José Pereira", "MOT-004", "45678901234", "2022-02-01", "D"),
        ("Antônio Costa", "MOT-005", "56789012345", "2020-08-15", "E"),
        ("Francisco Lima", "MOT-006", "67890123456", "2021-11-01", "D"),
        ("Paulo Almeida", "MOT-007", "78901234567", "2023-01-10", "E"),
        ("Roberto Ferreira", "MOT-008", "89012345678", "2022-06-20", "D")
    ]
    cursor.executemany("INSERT INTO d_motoristas (nome_motorista, codigo_motorista, cnh, data_admissao, categoria_cnh) VALUES (?, ?, ?, ?, ?);", motoristas)

    # ========== POPULA VEÍCULOS ==========
    print("🔄 Cadastrando veículos...")
    veiculos = [
        ("ABC-1234", "Actros", "Mercedes-Benz", "Caminhão", 15000, 2020, 25000, "2020-03-15"),
        ("DEF-5678", "FH", "Volvo", "Caminhão", 18000, 2021, 18000, "2021-05-20"),
        ("GHI-9012", "R440", "Scania", "Caminhão", 16000, 2019, 32000, "2019-08-10"),
        ("JKL-3456", "Stralis", "Iveco", "Caminhão", 14000, 2022, 5000, "2022-02-01"),
        ("MNO-7890", "Delivery", "VW", "VUC", 5000, 2021, 15000, "2021-07-15"),
        ("PQR-1234", "Cargo", "Ford", "Caminhão", 12000, 2020, 28000, "2020-10-20"),
        ("STU-5678", "Atego", "Mercedes-Benz", "VUC", 6000, 2023, 2000, "2023-01-10"),
        ("VWX-9012", "P360", "Scania", "Caminhão", 17000, 2022, 8000, "2022-06-01")
    ]
    cursor.executemany("""
        INSERT INTO d_veiculos (placa, modelo, fabricante, tipo_veiculo, capacidade_kg, ano_fabricacao, km_inicial, data_aquisicao) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, veiculos)

    # ========== POPULA CLIENTES ==========
    print("🔄 Cadastrando clientes...")
    clientes = [
        ("Móveis Elegância", "São Paulo", "SP", "Sudeste", "cliente_final"),
        ("Eletro Center", "Rio de Janeiro", "RJ", "Sudeste", "loja"),
        ("Casa & Conforto", "Belo Horizonte", "MG", "Sudeste", "cliente_final"),
        ("Multi Eletros", "Vitória", "ES", "Sudeste", "loja"),
        ("Móveis Planejados", "Curitiba", "PR", "Sul", "cliente_final"),
        ("Eletro Sul", "Porto Alegre", "RS", "Sul", "loja"),
        ("Casa Moderna", "Salvador", "BA", "Nordeste", "cliente_final"),
        ("Eletro Nordeste", "Fortaleza", "CE", "Nordeste", "loja"),
        ("Móveis Brasil", "Recife", "PE", "Nordeste", "cliente_final"),
        ("CD Goiânia", "Goiânia", "GO", "Centro-Oeste", "cd"),
        ("Distribuidora MT", "Cuiabá", "MT", "Centro-Oeste", "cd"),
        ("Móveis Rústicos", "Belém", "PA", "Norte", "cliente_final"),
        ("Eletro Manaus", "Manaus", "AM", "Norte", "loja"),
        ("CD São Paulo", "São Paulo", "SP", "Sudeste", "cd"),
        ("CD Rio", "Rio de Janeiro", "RJ", "Sudeste", "cd")
    ]
    cursor.executemany("INSERT INTO d_clientes (nome_cliente, cidade, estado, regiao, tipo_destino) VALUES (?, ?, ?, ?, ?);", clientes)

    conexao.commit()

    # ========== GERA DADOS DE ENTREGAS ==========
    print("🔄 Gerando 200 entregas com métricas completas...")
    segmentos = ["Móveis", "Eletrodomésticos", "Eletrônicos", "Utensílios", "Decoração", "Iluminação"]
    status_opcoes = ["Entregue No Prazo", "Atrasado", "Retido na Barreira Fiscal", "Extraviado", "Avariado"]
    gargalos_opcoes = {
        "Entregue No Prazo": "Nenhum",
        "Atrasado": "Atraso no Carregamento / Trânsito",
        "Retido na Barreira Fiscal": "Fiscalização / SEFAZ",
        "Extraviado": "Sinistro / Roubo de Carga",
        "Avariado": "Manuseio Incorreto / Acidente"
    }
    tipos_operacao = ["externa", "propria", "propria", "externa"]

    random.seed(42)
    data_base = datetime(2026, 6, 1)

    for i in range(1, 201):
        nf = f"NF-2026-{i:04d}"
        
        tipo_op = random.choice(tipos_operacao)
        
        if tipo_op == "externa":
            id_transp = random.randint(1, 4)
            id_motorista = None
            id_veiculo = None
            km_rodados = 0
            litros_combustivel = 0
            custo_manutencao = 0
            custo_pedagio = 0
            horas_trabalhadas = 0
            km_inicial_viagem = 0
            km_final_viagem = 0
            custo_combustivel = 0
            custo_horas_trabalhadas = 0
            tempo_viagem_horas = 0
            tempo_carregamento_horas = 0
            tempo_descarga_horas = 0
            numero_paradas = 0
            tempo_paradas_minutos = 0
            entregas_dia = 1
        else:
            id_transp = random.randint(5, 8)
            id_motorista = random.randint(1, 8)
            id_veiculo = random.randint(1, 8)
            
            km_rodados = round(random.uniform(50, 1200), 1)
            km_inicial_viagem = round(random.uniform(0, 50000), 1)
            km_final_viagem = km_inicial_viagem + km_rodados
            
            litros_combustivel = round(km_rodados / random.uniform(3.5, 6.5), 1)
            custo_combustivel = round(litros_combustivel * random.uniform(5.5, 6.5), 2)
            custo_manutencao = round(random.uniform(50, 500), 2)
            custo_pedagio = round(random.uniform(0, 300), 2)
            
            horas_trabalhadas = round(random.uniform(4, 12), 1)
            custo_horas_trabalhadas = round(horas_trabalhadas * random.uniform(25, 45), 2)
            
            tempo_viagem_horas = round(random.uniform(2, 10), 1)
            tempo_carregamento_horas = round(random.uniform(0.5, 3), 1)
            tempo_descarga_horas = round(random.uniform(0.5, 2), 1)
            numero_paradas = random.randint(0, 5)
            tempo_paradas_minutos = numero_paradas * random.randint(5, 30)
            entregas_dia = random.randint(1, 5)
        
        id_clie = random.randint(1, 15)
        id_fornecedor = random.randint(1, 8)
        seg = random.choice(segmentos)
        
        d_emissao = data_base + timedelta(days=random.randint(0, 20))
        d_previsao = d_emissao + timedelta(days=random.randint(2, 7))
        
        sorteio_status = random.choices(status_opcoes, weights=[0.55, 0.15, 0.10, 0.05, 0.15], k=1)[0]
        gargalo = gargalos_opcoes[sorteio_status]
        
        if sorteio_status == "Entregue No Prazo":
            d_entrega = d_previsao - timedelta(days=random.randint(0, 2))
            data_entrega_str = d_entrega.strftime('%Y-%m-%d')
        elif sorteio_status == "Extraviado":
            data_entrega_str = "Não Entregue"
        else:
            d_entrega = d_previsao + timedelta(days=random.randint(2, 10))
            data_entrega_str = d_entrega.strftime('%Y-%m-%d')

        valor_nf = round(random.uniform(500, 50000), 2)
        valor_mercadoria = round(valor_nf * random.uniform(0.7, 0.9), 2)
        peso = round(random.uniform(10, 2000), 2)
        volume = round(random.uniform(0.5, 15), 2)
        
        frete_tabela = round(valor_nf * random.uniform(0.02, 0.05), 2)
        if random.random() > 0.70:
            frete_cobrado = round(frete_tabela + random.uniform(100, 800), 2)
        else:
            frete_cobrado = frete_tabela
        frete_real = frete_cobrado if random.random() > 0.3 else round(frete_cobrado * random.uniform(0.9, 1.1), 2)
        
        avarias = random.random() < 0.12
        if avarias:
            qtd_avarias = random.randint(1, 3)
            valor_avaria = round(random.uniform(50, 5000), 2)
        else:
            qtd_avarias = 0
            valor_avaria = 0
        
        nota_satisfacao = random.randint(1, 5) if sorteio_status == "Entregue No Prazo" else random.randint(1, 4)
        reclamacao_cliente = random.random() < 0.08 if sorteio_status != "Entregue No Prazo" else False

        cursor.execute("""
            INSERT INTO f_entregas (
                numero_nota_fiscal, data_emissao, data_entrega_real, data_prevista_entrega,
                id_transportadora, id_motorista, id_veiculo, id_cliente, id_fornecedor,
                tipo_operacao, segmento_operacao,
                valor_nota_fiscal, peso_kg, volume_m3,
                custo_frete_tabela, custo_frete_cobrado, custo_frete_real, valor_mercadoria,
                km_rodados, km_inicial_viagem, km_final_viagem,
                litros_combustivel, custo_combustivel,
                custo_manutencao, custo_pedagio,
                custo_horas_trabalhadas, horas_trabalhadas,
                tempo_viagem_horas, tempo_carregamento_horas, tempo_descarga_horas,
                numero_paradas, tempo_paradas_minutos, entregas_dia,
                status_entrega, motivo_gargalo,
                avarias, valor_avaria, qtd_avarias,
                nota_satisfacao, reclamacao_cliente
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (nf, d_emissao.strftime('%Y-%m-%d'), data_entrega_str, d_previsao.strftime('%Y-%m-%d'),
              id_transp, id_motorista, id_veiculo, id_clie, id_fornecedor,
              tipo_op, seg,
              valor_nf, peso, volume,
              frete_tabela, frete_cobrado, frete_real, valor_mercadoria,
              km_rodados, km_inicial_viagem, km_final_viagem,
              litros_combustivel, custo_combustivel,
              custo_manutencao, custo_pedagio,
              custo_horas_trabalhadas, horas_trabalhadas,
              tempo_viagem_horas, tempo_carregamento_horas, tempo_descarga_horas,
              numero_paradas, tempo_paradas_minutos, entregas_dia,
              sorteio_status, gargalo,
              avarias, valor_avaria, qtd_avarias,
              nota_satisfacao, reclamacao_cliente))

    conexao.commit()
    conexao.close()
    print(f"✅ Banco criado com sucesso! {db_path}")

if __name__ == "__main__":
    criar_e_povoar_banco()
