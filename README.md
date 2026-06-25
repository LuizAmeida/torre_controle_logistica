# 🛸 Torre de Performance Logística | Case de Análise de Dados

A Torre de Performance Logística é um projeto interativo desenvolvido de ponta a ponta para centralizar e otimizar a visibilidade sobre indicadores de nível de serviço (SLA) e custos de transporte. Esta aplicação simula uma operação real de distribuição nacional, conectando métricas operacionais com impacto direto no resultado financeiro do negócio.

---

## 👨‍💻 Autor do Projeto

* **Responsável Técnico:** Luiz Almeida
* **Contexto:** Projeto de portfólio para consolidação de competências em Análise de Dados e Business Intelligence (BI).
* **Área de Domínio:** Logística, Cadeia de Suprimentos (Supply Chain) e Auditoria de Fretes.

---

## 📌 Links de Acesso Rápido

* 🚀 **Ambiente de Produção (Acesse o App ao Vivo):** [https://torre-controle-logistica.onrender.com](https://torre-controle-logistica.onrender.com)
* 📁 **Repositório do Código Fonte:** [https://github.com/LuizAlmeida/torre_controle_logistica](https://github.com/LuizAlmeida/torre_controle_logistica)

---

## 🎯 Cenário e Desafios de Negócio

No ambiente logístico de transportes de alta volumetria, gestores enfrentam diariamente problemas causados pela fragmentação da informação. Duas grandes dores foram priorizadas no desenho desta solução:

1. **Vazamento de Receita (Frete Estourado):** Discrepâncias financeiras onde os valores reais faturados pelas transportadoras parceiras superam os custos previamente acordados nas tabelas contratuais.
2. **Rastreabilidade de Gargalos:** Dificuldade em identificar de maneira estatística o motivo predominante gerador de atrasos, impactando a taxa de **OTIF (On-Time In-Full)**.

**Entrega Estratégica:** Este painel consolida os dados operacionais brutos, aplica regras de cálculo automatizadas e gera diagnósticos acionáveis imediatos para controle de custos e negociação com parceiros logísticos.

---

## 🗂️ Estrutura de Pastas e Diretórios do Projeto

Abaixo está descrita a arquitetura de arquivos organizada para o funcionamento da aplicação, seguindo os padrões de boas práticas de versionamento em ambiente Python:

```text
torre_controle_logistica/
│
├── .gitignore               # Instruções de exclusão de arquivos locais para o Git
├── LICENSE                  # Termos de uso e licença pública do projeto (MIT)
├── README.md                # Documentação principal e vitrine do portfólio (Este arquivo)
├── requirements.txt         # Listagem de dependências e bibliotecas do projeto
│
├── torre_controle_final.db  # Banco de dados relacional SQLite3 (Arquivo gerado)
├── gerar_banco.py           # Script Python para criação das tabelas e população dos dados
└── app.py                   # Script principal com as regras analíticas e interface Streamlit
````

## 📄 Detalhamento dos Componentes do Projeto
- requirements.txt: Contém as bibliotecas do projeto e suas respectivas versões de compatibilidade, mapeando de forma fixa o , , e os motores necessários para que o servidor na nuvem () monte o ambiente idêntico ao local.streamlitpandasplotlyRender

- .gitignore: Configurado especificamente para ecossistemas Python, evitando que arquivos temporários de compilação (como diretórios ou ambientes virtuais ) sejam enviados ao GitHub desnecessariamente.__pycache__/.venv/

- LICENSE (Licença MIT): Licença open-source permissiva padrão de mercado, indicando que o código é livre para visualização, estudos e bifurcações comerciais ou privadas, mantendo os créditos do autor original.

- gerar_banco.py: Automação em Python dedicada a estruturar o banco relacional local, limpar dados antigos e aplicar a injeção inicial de registros transacionais de teste.


## 🗄️ Modelagem de Dados Relacional (Star Schema)

Os dados utilizados pelo painel são armazenados em um banco de dados relacional . A arquitetura foi modelada seguindo o padrão de BI chamado Star Schema (Esquema Estrela), separando informações cadastrais em tabelas Dimensão e dados numéricos em tabelas Fato:SQLite3

- d_transportadoras (Tabela Dimensão): Armazena o ID corporativo, nome fantasia da transportadora, CNPJ (estruturado com chaves de unicidade), tipo de transporte operacional (Fracionado, Lotação, Refrigerado, Granel) e segmento mercadológico principal.

- d_clientes (Tabela Dimensão): Armazena os registros cadastrais de destino final, segregados por Nome do Cliente, Cidade, Estado e a Região geográfica correspondente (Norte, Nordeste, Centro-Oeste, Sudeste, Sul).

- f_entregas (Tabela Fato): Concentra a massa de dados transacional e as métricas de desempenho de cada nota fiscal. Armazena chaves estrangeiras vinculadas () às dimensões, valores monetários de NF, peso da carga (kg), custos em contrato, custos cobrados reais, status lógico da entrega e a descrição qualitativa do gargalo verificado.FOREIGN KEY


## 🧠 Lógica de Negócio e Recursos de Business Intelligence

O dashboard interativo processa em tempo real os dados transacionais e extrai três inteligências de monitoramento:

- Indicador OTIF (SLA Operacional): Avalia dinamicamente o cumprimento das metas de prazo. O algoritmo separa as entregas concluídas pontualmente e divide pelo total de movimentações registradas sob as combinações dos filtros aplicados.

- Auditoria Automatizada de Custos: Realiza a varredura financeira linha por linha comparando a tarifa faturada contra o frete de tabela. Casos divergentes com valores inflacionados alimentam imediatamente o card de prejuízo operacional por desvio de custos.

- Análise de Causa Raiz Dinâmica: Utilizando métodos de indexação e agregação estatística do , o sistema rastreia as ocorrências de falhas, calcula o principal fator causador de atrasos (ex: barreira fiscal, reentrega, devolução) e plota uma recomendação operacional fixa para atuação rápida da mesa de controle.pandas


## 🛠️ Tecnologias e Ferramentas Empregadas

- Python (v3.13): Core lógico e processamento de dados.
- Pandas: Motor de engenharia de dados, agregações estatísticas e junção dimensional.
- SQLite3: Armazenamento e execução de consultas via Structured Query Language (SQL).
- Plotly Express: Geração de visualizações dinâmicas interativas (Tendências temporais, distribuição de participação e custos lado a lado).
- Streamlit: Construção do ecossistema de interface web e inputs de filtros cruzados.
- Render Cloud: Infraestrutura em nuvem responsável por ler o repositório e disponibilizar o dashboard globalmente via internet.


## 💻 Instruções para Execução do Projeto em Máquina Local

Para clonar e testar a aplicação em seu ambiente de desenvolvimento local, execute os comandos descritos no terminal passo a passo:
````
# 1. Realizar o clone do repositório remoto
git clone [https://github.com/LuizAlmeida/torre_controle_logistica.git](https://github.com/LuizAlmeida/torre_controle_logistica.git)

# 2. Navegar até o diretório raiz do projeto clonado
cd torre_controle_logistica

# 3. Instalar as dependências de pacotes listadas
pip install -r requirements.txt

# 4. Executar o script Python para reconstrução e carga do banco de dados relacional
python gerar_banco.py

# 5. Inicializar o servidor local do Streamlit para abrir a interface no navegador
streamlit run app.py
````


---

## 📬 Contato e Conexões

Fique à vontade para explorar o código, fazer um fork do repositório ou entrar em contato para trocarmos ideias sobre Análise de Dados e Logística:

* **👨‍💻 Luiz Edglei Marques de Almeida**
* 💼 **LinkedIn:** [Acesse meu perfil profissional](https://www.linkedin.com/in/luiz-edglei-marques-de-almeida)
* 📧 **E-mail:** [luiz_almeida84@outlook.com](mailto:luiz_almeida84@outlook.com)
* 🚀 **Portfólio de Projetos:** [Voltar para a página principal do GitHub](https://github.com/LuizAlmeida)
