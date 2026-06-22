# 🛸 Torre de Performance Logística (End-to-End Analytics Case)

[![Streamlit App](https://static.streamlit.io/badge_hosted_button.svg)](https://torre-controle-logistica.onrender.com)

Este repositório contém um case completo de **Data Science & Analytics** voltado à gestão estratégica de transportes, auditoria financeira de fretes e controle de nível de serviço (SLA). A aplicação processa dados transacionais de notas fiscais e fornece diagnósticos automatizados sobre gargalos operacionais e desvios de custos.

---

## 💡 O Problema de Negócio

Em operações logísticas de grande escala, a falta de visibilidade centralizada gera duas grandes dores:
1. **Quebra de SLA (Service Level Agreement):** Dificuldade em rastrear quais transportadoras ou regiões estão penalizando o lead time de entrega, afetando a experiência do cliente.
2. **Falta de Auditoria de Frete:** Ocorrência de distorções onde o valor real de frete cobrado pela transportadora é superior ao valor acordado em contrato (Frete Tabela), gerando vazamento de capital (*frete estourado*).

**A Solução:** Uma Torre de Performance interativa que unifica dados de clientes, parceiros logísticos e notas fiscais para calcular indicadores críticos de performance, auditar custos e gerar insights de causa-raiz de forma automatizada.

---

## 📊 Principais Indicadores (KPIs) Monitorados

* **Total de Entregas (NFs):** Volumetria total de notas fiscais processadas na janela selecionada.
* **Total Frete Cobrado:** Montante financeiro total pago aos parceiros logísticos.
* **Taxa de OTIF (On-Time In-Full):** O indicador mais importante da distribuição. Mede o percentual de entregas concluídas estritamente dentro do prazo regulamentar.
* **Prejuízo (Frete Estourado):** Somatório dos desvios financeiros onde o custo cobrado superou a tabela contratada.

---

## 🏗️ Modelagem de Dados (Arquitetura SQL)

Os dados foram estruturados utilizando o banco de dados **SQLite3**, seguindo o modelo multidimensional **Star Schema** (Fato e Dimensões). Essa arquitetura garante alta performance nas consultas analíticas e integridade referencial via chaves estrangeiras (`FOREIGN KEY`).

* **`d_transportadoras` (Dimensão):** Cadastro de parceiros, CNPJs, tipos de veículo e segmento de atuação principal.
* **`d_clientes` (Dimensão):** Localização geográfica dos clientes mapeando Cidade, Estado e as 5 Regiões do Brasil.
* **`f_entregas` (Fato):** Registro transacional contendo datas (emissão, previsão, real), valores de NF, pesos (kg), cubagem, custos contratuais vs. reais e o status da entrega com o seu respectivo motivo de gargalo.

---

## 🛠️ Tecnologias Empregadas

* **Python 3.13:** Linguagem base de todo o ecossistema.
* **Pandas:** Manipulação, tratamento de dados, junção de tabelas e agregações estatísticas.
* **SQLite3:** Motor de banco de dados relacional para armazenamento seguro dos dados transacionais.
* **Streamlit:** Framework utilizado para a construção e publicação da interface web responsiva.
* **Plotly Express:** Geração de gráficos dinâmicos e interativos (linhas de tendência, gráficos de rosca e barras empilhadas).
* **Render:** Infraestrutura em nuvem utilizada para o deploy e hospedagem contínua da aplicação.

---

## 💻 Como Executar o Projeto Localmente

Caso queira clonar o repositório e rodar a aplicação em sua máquina:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/LuizAlmeida/torre_controle_logistica.git](https://github.com/LuizAlmeida/torre_controle_logistica.git)
   cd torre_controle_logistica
