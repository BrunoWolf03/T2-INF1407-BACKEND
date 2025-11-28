# INF1407 — ProgWeb

Trabalho Final — NBA Fantasy Game Backend

Bruno Wolf - 2212576

Luca Oliveira Lima - 2210831

## Escopo do Projeto
Este projeto foi desenvolvido para a disciplina **INF1407 — Programação Web**, com o objetivo de criar uma API RESTful em **Django** para um jogo de Fantasy Basketball NBA.

O sistema permite o gerenciamento completo de times, jogadores NBA, autenticação de usuários e ranking global.

O foco foi explorar os principais recursos do Django, incluindo:
- Estruturação de **models** e **migrations**
- Criação de **views** com Django REST Framework
- Sistema de autenticação com **JWT**
- Integração com APIs externas (Ball Don't Lie API)
- Documentação automática com **Swagger/OpenAPI**

---

## Funcionalidades Implementadas
- **Sistema de autenticação completo** com JWT (registro, login, logout, recuperação de senha)
- **Gerenciamento de jogadores NBA** com filtros por posição, time e preço
- **Criação e gerenciamento de times** de fantasy com limite de jogadores
- **Sistema de formação tática** (5 titulares + 7 reservas)
- **Ranking global** com pontuação baseada nas estatísticas dos jogadores
- **Dashboard de estatísticas** para visualização de dados do usuário
- **Documentação interativa** via Swagger UI
- **API RESTful** completa seguindo padrões REST

---

## Endpoints Principais

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login (retorna JWT token)
- `POST /api/auth/logout` - Logout
- `POST /api/auth/forgot-password` - Solicitar reset de senha
- `POST /api/auth/reset-password` - Resetar senha com token
- `POST /api/auth/change-password` - Trocar senha (autenticado)

### Players
- `GET /api/players` - Listar todos os jogadores com filtros
- `GET /api/players/:id` - Detalhes de um jogador específico

### Team
- `GET /api/team` - Obter time do usuário autenticado
- `POST /api/team/players` - Adicionar jogador ao time
- `DELETE /api/team/players/:id` - Remover jogador do time
- `PUT /api/team/formation` - Atualizar formação do time

### User Profile
- `GET /api/user/profile` - Obter perfil do usuário
- `PUT /api/user/profile/update` - Atualizar perfil

### Leaderboard
- `GET /api/leaderboard` - Ranking global de usuários

### Dashboard
- `GET /api/dashboard/stats` - Estatísticas do dashboard do usuário

---

## Como rodar localmente

### Pré-requisitos
- Python 3.11+
- pip
- virtualenv

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd T2-INF1407-BACKEND
```

2. **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute as migrações**
```bash
python manage.py migrate
```

5. **Carregue os dados iniciais (jogadores NBA)**
```bash
python manage.py loaddata players
```

6. **Execute o servidor de desenvolvimento**
```bash
python manage.py runserver 8000
```

A API estará disponível em: http://localhost:8000

A documentação Swagger estará em: http://localhost:8000/swagger/

---

## Como rodar com Docker

### Pré-requisitos
- Docker
- Docker Compose

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd T2-INF1407-BACKEND
```

2. **Execute com Docker Compose**
```bash
docker-compose up --build
```

A API estará disponível em: http://localhost:8000

Para parar os containers:
```bash
docker-compose down
```

Para parar e remover volumes:
```bash
docker-compose down -v
```

---

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação.

**Fluxo de uso:**

1. Registrar ou fazer login:
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123",
  "rememberMe": false
}
```

2. Receber o token na resposta:
```json
{
  "user": { ... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

3. Usar o token em requisições protegidas:
```bash
Authorization: Bearer <token>
```

---

## O que funcionou
- Todas as funcionalidades descritas no escopo foram **testadas e aprovadas**
- Sistema de autenticação JWT funcionando corretamente com refresh tokens
- CRUD completo de times e jogadores
- Integração com Ball Don't Lie API para dados dos jogadores NBA
- Sistema de pontuação e ranking global
- Documentação automática via Swagger
- Deploy funcionando corretamente
- Sistema de filtros e busca de jogadores
- Validações de regras de negócio (limite de jogadores, orçamento, etc)

---

## O que não funcionou
- O sistema de notificações por email foi implementado mas **requer configuração de servidor SMTP** em produção
- A atualização automática de estatísticas dos jogadores em tempo real não foi implementada, sendo necessário executar um script manualmente
- Testes automatizados foram parcialmente implementados, mas não cobrem 100% do código

---

## Observações Finais

O projeto foi concluído conforme os requisitos da disciplina.
Todas as funcionalidades principais foram implementadas com sucesso, e a API encontra-se estável e utilizável.

A documentação completa da API pode ser acessada via Swagger UI em `/swagger/` quando o servidor estiver rodando.

Para fins de desenvolvimento, o banco de dados SQLite é utilizado. Para produção, recomenda-se configurar PostgreSQL através das variáveis de ambiente no arquivo `.env`.

A API está preparada para integração com frontend e suporta CORS para desenvolvimento local.
