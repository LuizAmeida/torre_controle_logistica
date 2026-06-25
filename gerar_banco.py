import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def criar_e_povoar_banco():
    conexao = sqlite3.connect("torre_controle_final.db")
    cursor = conexao.cursor()

    # 1. Criando as Tabelas
    cursor.execute("DROP TABLE IF EXISTS f_entregas;")
    cursor.execute("DROP TABLE IF EXISTS d_transportadoras;")
    cursor.execute("DROP TABLE IF EXISTS d_clientes;")

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

    # 2. Inserindo 8 Transportadoras Parceiras
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

    # 3. Inserindo Clientes distribuídos por Estados e Regiões
    clientes = [
        ("Magazine Luiza SP", "São Paulo", "SP", "Sudeste"),
        ("Via Varejo RJ", "Rio de Janeiro", "RJ", "Sudeste"),
        ("Mercado Livre MG", "Belo Horizonte", "MG", "Sudeste"),
        ("Ambev BA", "Salvador", "BA", "Nordeste"),
        ("Grendene CE", "Fortaleza", "CE", "Nordeste"),
        ("Mundial RS", "Porto Alegre", "RS", "Sul"),
        ("Terminal PR", "Curitiba", "PR", "Sul"),
        ("Agro GO", "Goiânia", "GO", "Centro-Oeste")
    ]
    cursor.executemany("INSERT INTO d_clientes (nome_cliente, cidade, estado, regiao) VALUES (?, ?, ?, ?);", clientes)
    conexao.commit()

    # 4. Gerando 100 Notas Fiscais Estruturadas com Lógica de Negócio
    segmentos = ["E-Commerce", "Varejo", "Indústria", "Agronegócio"]
    status_opcoes = ["Entregue No Prazo", "Atrasado", "Retido na Barreira Fiscal", "Extraviado"]
    gargalos_opcoes = {
        "Entregue No Prazo": "Nenhum Operacional",
        "Atrasado": "Atraso no Carregamento",
        "Retido na Barreira Fiscal": "Fiscalização / SEFAZ",
        "Extraviado": "Sinistro / Roubo de Carga"
    }

    random.seed(42) # Mantém os dados fixos e consistentes
    data_base = datetime(2026, 6, 1)

    for i in range(1, 101):
        nf = f"NF-2026-{i:03d}"
        id_transp = random.randint(1, 8)
        id_clie = random.randint(1, 8)
        seg = random.choice(segmentos)
        
        # Datas lógicas
        d_emissao = data_base + timedelta(days=random.randint(0, 15))
        d_previsao = d_emissao + timedelta(days=random.randint(3, 7))
        
        # Sorteando o status baseado em probabilidade real (65% no prazo, 35% com problemas)
        sorteio_status = random.choices(status_opcoes, weights=[0.65, 0.20, 0.10, 0.05], k=1)[0]
        gargalo = gargalos_opcoes[sorteio_status]
        
        if sorteio_status == "Entregue No Prazo":
            d_entrega = d_previsao - timedelta(days=random.randint(0, 2))
        else:
            d_entrega = d_previsao + timedelta(days=random.randint(2, 6)) if sorteio_status != "Extraviado" else "Não Entregue"

        valor_nf = round(random.uniform(5000, 120000), 2)
        peso = round(random.uniform(50, 4000), 2)
        
        # Lógica de Auditoria de Frete (Algumas transportadoras cobram a mais de propósito)
        frete_tabela = round(valor_nf * random.uniform(0.02, 0.05), 2)
        if random.random() > 0.75: # 25% de chance de erro de faturamento (frete estourado)
            frete_cobrado = round(frete_tabela + random.uniform(150, 1200), 2)
        else:
            frete_cobrado = frete_tabela

        cursor.execute("""
            INSERT INTO f_entregas (
                numero_nota_fiscal, id_transportadora, id_cliente, segmento_operacao,
                data_emissao, data_previsao_entrega, data_entrega_real, valor_nota_fiscal,
                peso_kg, custo_frete_tabela, custo_frete_cobrado, status_entrega, motivo_gargalo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (nf, id_transp, id_clie, seg, d_emissao.strftime('%Y-%m-%d'), d_previsao.strftime('%Y-%m-%d'), 
              d_entrega if isinstance(d_entrega, str) else d_entrega.strftime('%Y-%m-%d'), 
              valor_nf, peso, frete_tabela, frete_cobrado, sorteio_status, gargalo))

    conexao.commit()
    conexao.close()
    print("Banco de dados expandido com 100 NFs, 8 transportadoras e estados cadastrado com sucesso!")

if __name__ == "__main__":
    criar_e_povoar_banco()
