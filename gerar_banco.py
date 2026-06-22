import sqlite3

conexao = sqlite3.connect("torre_controle_final.db")
cursor = conexao.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS d_transportadoras (
        id_transportadora INTEGER PRIMARY KEY,
        nome_transportadora TEXT NOT NULL,
        cnpj_transportadora TEXT UNIQUE NOT NULL,
        tipo_transporte TEXT,
        segmento_principal TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS d_clientes (
        id_cliente INTEGER PRIMARY KEY,
        nome_cliente TEXT NOT NULL,
        cidade TEXT NOT NULL,
        estado TEXT NOT NULL,
        regiao TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS f_entregas (
        id_entrega INTEGER PRIMARY KEY,
        numero_nota_fiscal INTEGER NOT NULL,
        id_transportadora INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        segmento_operacao TEXT NOT NULL,
        data_emissao TEXT NOT NULL,
        data_previsao_entrega TEXT NOT NULL,
        data_entrega_real TEXT,
        valor_nota_fiscal REAL NOT NULL,
        peso_kg REAL NOT NULL,
        custo_frete_tabela REAL NOT NULL,
        custo_frete_cobrado REAL NOT NULL,
        status_entrega TEXT NOT NULL,
        motivo_gargalo TEXT,
        FOREIGN KEY (id_transportadora) REFERENCES d_transportadoras(id_transportadora),
        FOREIGN KEY (id_cliente) REFERENCES d_clientes(id_cliente)
    );
""")

cursor.execute("DELETE FROM f_entregas;")
cursor.execute("DELETE FROM d_transportadoras;")
cursor.execute("DELETE FROM d_clientes;")

dados_transportadoras = [
    (1, 'Alfa Transportes Express Ltda', '11.111.111/0001-11', 'Fracionado', 'E-commerce'),
    (2, 'Logística Beta Pesados S/A', '22.222.222/0001-22', 'Lotação / TL', 'Carga Geral'),
    (3, 'Expresso Gamma Frio S/A', '33.333.333/0001-33', 'Refrigerado / Controlado', 'Farmacêutico'),
    (4, 'Delta Agro Logística', '44.444.444/0001-44', 'Granel / Caçamba', 'Agronegócio'),
    (5, 'Omega Last Mile Distribuição', '55.555.555/0001-55', 'Urbano / VUC', 'E-commerce')
]
cursor.executemany("INSERT INTO d_transportadoras VALUES (?, ?, ?, ?, ?);", dados_transportadoras)

dados_clientes = [
    (101, 'Varejo São Paulo Hub', 'São Paulo', 'SP', 'Sudeste'),
    (102, 'Distribuidora Rio Centro', 'Rio de Janeiro', 'RJ', 'Sudeste'),
    (103, 'Nordeste Log Commercial', 'Recife', 'PE', 'Nordeste'),
    (104, 'Sul Mercado Atacadista', 'Porto Alegre', 'RS', 'Sul'),
    (105, 'Centro-Oeste Grãos & Cia', 'Goiânia', 'GO', 'Centro-Oeste'),
    (106, 'Pharma Norte Distribuidora', 'Manaus', 'AM', 'Norte'),
    (107, 'Farma Sudeste Medicamentos', 'Campinas', 'SP', 'Sudeste'),
    (108, 'Cerrado Cooperativa Agrícola', 'Sorriso', 'MT', 'Centro-Oeste')
]
cursor.executemany("INSERT INTO d_clientes VALUES (?, ?, ?, ?, ?);", dados_clientes)

dados_entregas = [
    (1, 5001, 1, 101, 'E-commerce', '2026-06-01', '2026-06-04', '2026-06-04', 1500.00, 45.50, 120.00, 120.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (2, 5002, 1, 102, 'E-commerce', '2026-06-01', '2026-06-05', '2026-06-08', 3400.00, 120.00, 250.00, 390.00, 'Atrasado', 'Cobrança Indevida Adicional / Frete Estourado'),
    (3, 5003, 5, 101, 'E-commerce', '2026-06-02', '2026-06-03', '2026-06-03', 450.00, 5.00, 35.00, 35.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (4, 5004, 5, 102, 'E-commerce', '2026-06-02', '2026-06-04', '2026-06-07', 980.00, 15.00, 65.00, 65.00, 'Atrasado', 'Endereço Não Localizado / Ineficiência Last-Mile'),
    (5, 5005, 1, 103, 'E-commerce', '2026-06-03', '2026-06-08', '2026-06-12', 5100.00, 210.00, 410.00, 580.00, 'Atrasado', 'Retenção em Barreira Fiscal / SEFAZ'),
    (6, 5006, 1, 104, 'E-commerce', '2026-06-04', '2026-06-09', '2026-06-09', 2300.00, 80.00, 190.00, 190.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (7, 5007, 5, 101, 'E-commerce', '2026-06-05', '2026-06-06', '2026-06-09', 1100.00, 22.00, 45.00, 45.00, 'Atrasado', 'Destinatário Ausente / Necessidade de Reentrega'),
    (8, 5008, 1, 105, 'E-commerce', '2026-06-05', '2026-06-12', None, 6700.00, 310.00, 550.00, 550.00, 'Em Trânsito', 'Carga em Fluxo Normal'),
    (9, 6001, 2, 101, 'Carga Geral', '2026-06-01', '2026-06-03', '2026-06-03', 45000.00, 12000.00, 1800.00, 1800.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (10, 6002, 2, 102, 'Carga Geral', '2026-06-01', '2026-06-03', '2026-06-06', 32000.00, 8500.00, 1400.00, 1950.00, 'Atrasado', 'Estadia de Veículo / Demora na Descarga do Cliente'),
    (11, 6003, 2, 103, 'Carga Geral', '2026-06-02', '2026-06-08', '2026-06-07', 89000.00, 24000.00, 4200.00, 4200.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (12, 6004, 2, 104, 'Carga Geral', '2026-06-02', '2026-06-08', '2026-06-11', 55000.00, 14500.00, 2900.00, 3600.00, 'Atrasado', 'Quebra Mecânica do Cavalo Mecânico na Rodovia'),
    (13, 6005, 2, 105, 'Carga Geral', '2026-06-03', '2026-06-08', '2026-06-08', 28000.00, 6100.00, 1100.00, 1100.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (14, 6006, 2, 101, 'Carga Geral', '2026-06-10', '2026-06-12', '2026-06-15', 18500.00, 3900.00, 780.00, 1150.00, 'Atrasado', 'Erro Cadastral de Cubagem / Cobrança Divergente'),
    (15, 6007, 2, 103, 'Carga Geral', '2026-06-12', '2026-06-18', None, 95000.00, 26000.00, 4500.00, 4500.00, 'Em Trânsito', 'Carga em Fluxo Normal'),
    (16, 6008, 2, 102, 'Carga Geral', '2026-06-15', '2026-06-17', '2026-06-17', 14000.00, 2100.00, 490.00, 490.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (17, 7001, 3, 107, 'Farmacêutico', '2026-06-01', '2026-06-02', '2026-06-02', 120000.00, 450.00, 950.00, 950.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (18, 7002, 3, 103, 'Farmacêutico', '2026-06-01', '2026-06-05', '2026-06-09', 340000.00, 1100.00, 2800.00, 3400.00, 'Atrasado', 'Perda de Temperatura / Excursão Térmica na Carga'),
    (19, 7003, 3, 106, 'Farmacêutico', '2026-06-02', '2026-06-09', '2026-06-08', 450000.00, 1800.00, 6200.00, 6200.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (20, 7004, 3, 104, 'Farmacêutico', '2026-06-03', '2026-06-07', '2026-06-10', 85000.00, 320.00, 890.00, 890.00, 'Atrasado', 'Sinistro / Tentativa de Roubo de Carga Monitorada'),
    (21, 7005, 3, 107, 'Farmacêutico', '2026-06-05', '2026-06-06', '2026-06-06', 95000.00, 280.00, 610.00, 900.00, 'Entregue No Prazo', 'Taxa Adicional de Agendamento Não Prevista'),
    (22, 7006, 3, 101, 'Farmacêutico', '2026-06-10', '2026-06-11', '2026-06-11', 115000.00, 390.00, 720.00, 720.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (23, 7007, 3, 106, 'Farmacêutico', '2026-06-15', '2026-06-22', None, 210000.00, 920.00, 4800.00, 4800.00, 'Em Trânsito', 'Carga em Fluxo Normal'),
    (24, 7008, 3, 105, 'Farmacêutico', '2026-06-16', '2026-06-20', '2026-06-20', 64000.00, 190.00, 530.00, 530.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (25, 8001, 4, 108, 'Agronegócio', '2026-06-01', '2026-06-06', '2026-06-06', 75000.00, 32000.00, 5400.00, 5400.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (26, 8002, 4, 105, 'Agronegócio', '2026-06-01', '2026-06-05', '2026-06-09', 72000.00, 31500.00, 4800.00, 6100.00, 'Atrasado', 'Excesso de Peso Identificado na Balança Rodoviária'),
    (27, 8003, 4, 108, 'Agronegócio', '2026-06-02', '2026-06-07', '2026-06-07', 78000.00, 33000.00, 5600.00, 5600.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (28, 8004, 4, 103, 'Agronegócio', '2026-06-02', '2026-06-10', '2026-06-14', 81000.00, 32800.00, 7900.00, 7900.00, 'Atrasado', 'Interdição de Pista por Desmoronamento em Serra'),
    (29, 8005, 4, 108, 'Agronegócio', '2026-06-05', '2026-06-10', '2026-06-10', 74000.00, 31900.00, 5300.00, 5300.00, 'Entregue No Prazo', 'Nenhum Operacional'),
    (30, 8006, 4, 104, 'Agronegócio', '2026-06-06', '2026-06-13', '2026-06-13', 83000.00, 34000.00, 8200.00, 9500.00, 'Entregue No Prazo', 'Tarifa Adicional de Pedágio Não Parametrizada'),
    (31, 8007, 4, 108, 'Agronegócio', '2026-06-18', '2026-06-23', None, 76000.00, 32100.00, 5400.00, 5400.00, 'Em Trânsito', 'Carga em Fluxo Normal'),
    (32, 8008, 4, 105, 'Agronegócio', '2026-06-19', '2026-06-23', None, 73000.00, 31200.00, 4700.00, 4700.00, 'Em Trânsito', 'Carga em Fluxo Normal')
]
cursor.executemany("INSERT INTO f_entregas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_entregas)

conexao.commit()
conexao.close()
print("🎯 Banco de dados 'torre_controle_final.db' gerado localmente com sucesso!")