# NBA Fantasy Game - Backend

Backend API desenvolvido em Django para o jogo de Fantasy Basketball NBA.

## Frontend Repository
🔗 **Link do Frontend:** [Adicione aqui o link do repositório frontend]

## Documentação Importante

📋 **LEIA ANTES DE COMEÇAR:**
1. [`API_SPECIFICATION.md`](./API_SPECIFICATION.md) - Especificação completa da API
2. [`BACKEND_INTEGRATION_GUIDE.md`](./BACKEND_INTEGRATION_GUIDE.md) - Guia de integração

> **Nota:** Copie os arquivos `API_SPECIFICATION.md` e `BACKEND_INTEGRATION_GUIDE.md` do repositório do frontend para este repositório antes de começar o desenvolvimento.

## Stack Tecnológica

- **Framework:** Django 4.2+
- **API:** Django REST Framework
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** PostgreSQL
- **Documentation:** Swagger/OpenAPI (drf-spectacular)
- **CORS:** django-cors-headers

## Instalação Rápida

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd nba-fantasy-backend

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Execute migrações
python manage.py migrate

# Carregue dados iniciais
python manage.py loaddata players

# Crie superusuário
python manage.py createsuperuser

# Execute servidor
python manage.py runserver 8000
```

## Endpoints Principais

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/forgot-password` - Esqueci senha
- `POST /api/auth/reset-password` - Resetar senha
- `POST /api/auth/change-password` - Trocar senha

### Players (CRUD)
- `GET /api/players` - Listar jogadores
- `GET /api/players/:id` - Detalhes do jogador

### Team (CRUD)
- `GET /api/team` - Obter time do usuário
- `POST /api/team/players` - Adicionar jogador
- `DELETE /api/team/players/:id` - Remover jogador
- `PUT /api/team/formation` - Atualizar formação

### Leaderboard
- `GET /api/leaderboard` - Ranking global

### Swagger
- `/swagger/` - Documentação interativa da API

## Estrutura do Projeto

```
backend/
├── api/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── authentication/
│   ├── views.py
│   └── serializers.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── fixtures/
│   └── players.json
├── requirements.txt
├── Dockerfile
└── README.md
```

## Variáveis de Ambiente

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@localhost:5432/nba_fantasy

CORS_ALLOWED_ORIGINS=http://localhost:5173

JWT_SECRET_KEY=your-jwt-secret
```

## Docker

```bash
# Build
docker-compose build

# Run
docker-compose up

# Migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Testes

```bash
# Executar todos os testes
python manage.py test

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

## Requisitos Atendidos

### CRUD Completo ✅
- CREATE: Adicionar jogadores ao time
- READ: Listar jogadores, times, leaderboard
- UPDATE: Atualizar formação, perfil do usuário
- DELETE: Remover jogadores do time

### Autenticação ✅
- JWT authentication
- Endpoints protegidos
- Gerenciamento de senha completo

### Usuários ✅
- Cada usuário tem visão própria
- Gerenciamento de time individual
- Sistema de ranking

### Swagger ✅
- Documentação completa em `/swagger/`
- Testável via interface

## Deploy

### Render / Railway / Heroku

```bash
# Procfile
web: gunicorn config.wsgi --log-file -
```

### Variáveis de Ambiente (Produção)
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS=https://your-frontend.com`

## Contato

- **Desenvolvedor:** [Seu Nome]
- **Email:** [seu@email.com]
- **Frontend:** [Link do repositório]

## O que Funciona ✅

- [ ] Registro de usuários
- [ ] Login com JWT
- [ ] CRUD de jogadores
- [ ] CRUD de times
- [ ] Sistema de budget
- [ ] Validação de regras (5 jogadores max, budget)
- [ ] Leaderboard
- [ ] Swagger documentation
- [ ] Reset de senha

## O que Não Funciona / Em Desenvolvimento ⚠️

- [ ] Ligas privadas
- [ ] Sistema de trade
- [ ] Notificações em tempo real
- [ ] Integração com API da NBA (stats reais)

## Licença

Este projeto foi desenvolvido para fins educacionais.
