# Controle de Gastos

Sistema completo para controle de gastos pessoais desenvolvido com Python (Flask), MySQL e Docker.

## Tecnologias

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| Python | 3.11 | Linguagem de programação |
| Flask | 3.0 | Framework web |
| MySQL | 8.0 | Banco de dados relacional |
| Docker | - | Containerização |
| SQLAlchemy | - | ORM para banco de dados |
| Chart.js | - | Gráficos no frontend |

## Funcionalidades

- Cadastro de gastos e receitas
- Categorização de transações
- Relatórios mensais
- Análise por categoria
- Evolução de gastos ao longo do tempo
- Maiores gastos do período
- Análise por forma de pagamento

## Instalação e Execução

### Pré-requisitos

- Docker
- Docker Compose

### Configuração

1. Clone o repositório e entre na pasta:

```bash
cd controle-gastos
```

2. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

O arquivo `.env` contém as seguintes variáveis:

| Variável | Descrição |
|----------|-----------|
| MYSQL_ROOT_PASSWORD | Senha do root do MySQL |
| MYSQL_DATABASE | Nome do banco de dados |
| MYSQL_USER | Usuário do banco |
| MYSQL_PASSWORD | Senha do usuário |
| DATABASE_URL | URL de conexão do SQLAlchemy |
| FLASK_ENV | Ambiente (development/production) |
| FLASK_DEBUG | Modo debug (0 ou 1) |

3. Inicie os containers:

```bash
docker-compose up --build
```

4. Acesse a aplicação: http://localhost:5000

5. Clique em "Criar Categorias" ou execute:

```bash
curl -X POST http://localhost:5000/api/categorias/seed
```

## Endpoints da API

### Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface web |
| GET | `/health` | Status da aplicação |
| GET | `/api` | Informações da API |

### Categorias

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/categorias` | Lista todas as categorias |
| GET | `/api/categorias/:id` | Obtém uma categoria |
| POST | `/api/categorias` | Cria uma categoria |
| PUT | `/api/categorias/:id` | Atualiza uma categoria |
| DELETE | `/api/categorias/:id` | Desativa uma categoria |
| POST | `/api/categorias/seed` | Cria categorias padrão |

### Gastos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/gastos` | Lista gastos (com filtros) |
| GET | `/api/gastos/:id` | Obtém um gasto |
| POST | `/api/gastos` | Cria um gasto |
| PUT | `/api/gastos/:id` | Atualiza um gasto |
| DELETE | `/api/gastos/:id` | Remove um gasto |

Filtros disponíveis para `/api/gastos`:

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| categoria_id | int | Filtrar por categoria |
| tipo | string | "despesa" ou "receita" |
| data_inicio | date | Data inicial (YYYY-MM-DD) |
| data_fim | date | Data final (YYYY-MM-DD) |
| mes | int | Mês (1-12) |
| ano | int | Ano (YYYY) |

### Relatórios

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/relatorios/resumo-mensal` | Resumo do mês |
| GET | `/api/relatorios/por-categoria` | Gastos por categoria |
| GET | `/api/relatorios/evolucao` | Evolução ao longo do tempo |
| GET | `/api/relatorios/maiores-gastos` | Maiores gastos |
| GET | `/api/relatorios/por-forma-pagamento` | Por forma de pagamento |

## Exemplos de Uso

### Criar uma categoria

```bash
curl -X POST http://localhost:5000/api/categorias \
  -H "Content-Type: application/json" \
  -d '{"nome": "Alimentação", "descricao": "Gastos com comida", "cor": "#14b8a6"}'
```

### Registrar um gasto

```bash
curl -X POST http://localhost:5000/api/gastos \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Supermercado",
    "valor": 250.50,
    "data": "2025-11-26",
    "categoria_id": 1,
    "tipo": "despesa",
    "forma_pagamento": "Cartão de Crédito"
  }'
```

### Registrar uma receita

```bash
curl -X POST http://localhost:5000/api/gastos \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Salário",
    "valor": 5000.00,
    "data": "2025-11-05",
    "categoria_id": 9,
    "tipo": "receita"
  }'
```

### Obter resumo mensal

```bash
curl "http://localhost:5000/api/relatorios/resumo-mensal?mes=11&ano=2025"
```

### Obter gastos por categoria

```bash
curl "http://localhost:5000/api/relatorios/por-categoria?mes=11&ano=2025"
```

## Estrutura do Projeto

```
controle-gastos/
├── app/
│   ├── __init__.py          # Factory da aplicação Flask
│   ├── config.py            # Configurações
│   ├── models/
│   │   └── __init__.py      # Modelos do banco de dados
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── gastos.py        # Rotas de gastos
│   │   ├── categorias.py    # Rotas de categorias
│   │   └── relatorios.py    # Rotas de relatórios
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Estilos da aplicação
│   │   └── js/
│   │       └── app.js       # Lógica do frontend
│   └── templates/
│       └── index.html       # Página principal
├── docker-compose.yml       # Configuração Docker Compose
├── Dockerfile               # Dockerfile da aplicação
├── init.sql                 # Script inicial do MySQL
├── requirements.txt         # Dependências Python
├── run.py                   # Ponto de entrada da aplicação
├── .env                     # Variáveis de ambiente (não versionado)
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Este arquivo
```

## Comandos Úteis

```bash
# Iniciar containers em background
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Parar containers
docker-compose down

# Reconstruir imagens
docker-compose up --build

# Acessar container da aplicação
docker exec -it controle_gastos_app bash

# Acessar MySQL
docker exec -it controle_gastos_db mysql -u app_user -p

# Limpar volumes (apaga dados do banco)
docker-compose down -v
```

## Modelo de Dados

### Tabela: categorias

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INT | Chave primária |
| nome | VARCHAR(100) | Nome da categoria |
| descricao | VARCHAR(255) | Descrição |
| cor | VARCHAR(7) | Cor hexadecimal |
| icone | VARCHAR(50) | Indicador visual |
| ativo | BOOLEAN | Se está ativa |
| created_at | DATETIME | Data de criação |
| updated_at | DATETIME | Data de atualização |

### Tabela: gastos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INT | Chave primária |
| descricao | VARCHAR(255) | Descrição do gasto |
| valor | DECIMAL(10,2) | Valor da transação |
| data | DATE | Data do gasto |
| categoria_id | INT | FK para categorias |
| tipo | VARCHAR(20) | "despesa" ou "receita" |
| forma_pagamento | VARCHAR(50) | Forma de pagamento |
| observacao | TEXT | Observações |
| recorrente | BOOLEAN | Se é recorrente |
| created_at | DATETIME | Data de criação |
| updated_at | DATETIME | Data de atualização |

## Licença

Este projeto está sob a licença MIT.
