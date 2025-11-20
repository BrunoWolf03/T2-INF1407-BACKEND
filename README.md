# NBA Fantasy Game - Backend API

Backend RESTful API desenvolvido em Django para o jogo de Fantasy Basketball NBA.

## 📎 Links

- **Frontend Repository:** [Adicione aqui o link do repositório frontend]
- **API Documentation (Swagger):** http://localhost:8000/swagger/
- **Admin Panel:** http://localhost:8000/admin/

## 📚 Documentação Importante

- [API_SPECIFICATION.md](./API_SPECIFICATION.md) - Especificação completa da API
- [BACKEND_INTEGRATION_GUIDE.md](./BACKEND_INTEGRATION_GUIDE.md) - Guia de integração

## 🛠️ Stack Tecnológica

- **Framework:** Django 4.2+
- **API:** Django REST Framework
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Documentation:** Swagger/OpenAPI (drf-spectacular)
- **CORS:** django-cors-headers

## 🚀 Instalação e Configuração

### Opção 1: Instalação Local

#### Pré-requisitos
- Python 3.11+
- pip
- virtualenv (recomendado)

#### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd T2-INF1407-BACKEND
```

2. **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas configurações (opcional para desenvolvimento)
```

5. **Execute as migrações**
```bash
python manage.py migrate
```

6. **Carregue os dados iniciais (25 jogadores NBA)**
```bash
python manage.py loaddata players
```

7. **Crie um superusuário (opcional)**
```bash
python manage.py createsuperuser
```

8. **Execute o servidor de desenvolvimento**
```bash
python manage.py runserver 8000
```

A API estará disponível em: http://localhost:8000

### Opção 2: Docker

#### Pré-requisitos
- Docker
- Docker Compose

#### Passos

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

## 📄 Documentação da API

### Swagger UI
Acesse: http://localhost:8000/swagger/

A documentação interativa do Swagger permite:
- Visualizar todos os endpoints disponíveis
- Testar requisições diretamente pela interface
- Ver exemplos de request/response
- Entender a estrutura de dados

### Endpoints Principais

#### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login (retorna JWT token)
- `POST /api/auth/logout` - Logout
- `POST /api/auth/forgot-password` - Solicitar reset de senha
- `POST /api/auth/reset-password` - Resetar senha com token
- `POST /api/auth/change-password` - Trocar senha (autenticado)

#### Players (CRUD)
- `GET /api/players` - Listar todos os jogadores
  - Query params: `position`, `team`, `maxPrice`, `search`, `sortBy`
- `GET /api/players/:id` - Detalhes de um jogador

#### Team (CRUD)
- `GET /api/team` - Obter time do usuário autenticado
- `POST /api/team/players` - Adicionar jogador ao time
- `DELETE /api/team/players/:id` - Remover jogador do time
- `PUT /api/team/formation` - Atualizar formação do time

#### User Profile
- `GET /api/user/profile` - Obter perfil do usuário
- `PUT /api/user/profile/update` - Atualizar perfil

#### Leaderboard
- `GET /api/leaderboard` - Ranking global
  - Query params: `league`, `timeframe`, `limit`

#### Dashboard
- `GET /api/dashboard/stats` - Estatísticas do dashboard do usuário

### Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação.

**Como usar:**

1. **Registrar ou fazer login:**
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123",
  "rememberMe": false
}
```

2. **Receber o token na resposta:**
```json
{
  "user": { ... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

3. **Usar o token em requisições protegidas:**
```bash
Authorization: Bearer <token>
```

### Exemplos de Uso

#### Listar jogadores filtrados por posição
```bash
GET /api/players?position=PG&sortBy=points
```

#### Adicionar jogador ao time
```bash
POST /api/team/players
Authorization: Bearer <token>
Content-Type: application/json

{
  "playerId": 1
}
```

#### Visualizar leaderboard
```bash
GET /api/leaderboard?limit=10
```

## 📁 Estrutura do Projeto

```
T2-INF1407-BACKEND/
```
