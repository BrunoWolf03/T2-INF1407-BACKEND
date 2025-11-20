# 🚀 Guia de Início Rápido - NBA Fantasy Backend

## ⚠️ IMPORTANTE: Configuração do Banco de Dados

Se você encontrar o erro: `no such column: position_short`, siga o método recomendado abaixo.

---

## Método 1: Script Automático (RECOMENDADO)

### Passo 1: Instalar dependências
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Passo 2: Configurar banco de dados
```bash
python setup_db.py
```

Este script irá:
- ✅ Criar as tabelas do banco de dados
- ✅ Carregar 25 jogadores NBA
- ✅ Verificar se tudo está correto

### Passo 3: Criar superusuário (opcional)
```bash
python manage.py createsuperuser
```

### Passo 4: Executar servidor
```bash
python manage.py runserver 8000
```

Pronto! Acesse: http://localhost:8000/swagger/

---

## Método 2: Instalação Manual Passo a Passo

### 1. Criar ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Remover banco antigo (se existir)
```bash
# Windows
del db.sqlite3

# Linux/Mac
rm db.sqlite3
```

### 4. Executar migrações
```bash
python manage.py migrate
```

### 5. Carregar jogadores
```bash
python manage.py loaddata players
```

Se o comando acima falhar, tente:
```bash
python manage.py loaddata core/fixtures/players.json
```

### 6. (Opcional) Criar superusuário
```bash
python manage.py createsuperuser
```

### 7. Executar servidor
```bash
python manage.py runserver 8000
```

---

## Método 3: Docker

### Com Docker Compose
```bash
docker-compose down -v
docker-compose up --build
```

### Com Docker apenas
```bash
docker build -t nba-fantasy-backend .
docker run -p 8000:8000 nba-fantasy-backend
```

Acesse: http://localhost:8000/swagger/

---

## 🧪 Testar a API

### 1. Acesse o Swagger
http://localhost:8000/swagger/

### 2. Registrar um usuário
```json
POST /api/auth/register
{
  "username": "player1",
  "email": "player1@example.com",
  "password": "Test123456",
  "confirmPassword": "Test123456",
  "teamName": "Dream Team"
}
```

### 3. Fazer login
```json
POST /api/auth/login
{
  "email": "player1@example.com",
  "password": "Test123456",
  "rememberMe": false
}
```

Copie o **token** da resposta.

### 4. Autenticar no Swagger
1. Clique no botão "Authorize" 🔓
2. Cole: `Bearer SEU_TOKEN_AQUI`
3. Clique em "Authorize"

### 5. Ver jogadores disponíveis
```
GET /api/players
```

### 6. Adicionar jogador ao time
```json
POST /api/team/players
{
  "playerId": 1
}
```

### 7. Ver seu time
```
GET /api/team
```

### 8. Ver leaderboard
```
GET /api/leaderboard
```

---

## 📚 URLs Importantes

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/
- **Admin Panel:** http://localhost:8000/admin/
- **API Base:** http://localhost:8000/api/

---

## 🎯 Dados Pré-carregados

O sistema já vem com **25 jogadores NBA** pré-cadastrados:
- LeBron James (SF - Lakers) - $42.5M
- Stephen Curry (PG - Warriors) - $45.8M
- Giannis Antetokounmpo (PF - Bucks) - $44.2M
- Nikola Jokic (C - Nuggets) - $46.3M
- Joel Embiid (C - 76ers) - $44.5M
- E mais 20 jogadores!

---

## 🐛 Problemas Comuns

### Erro: `no such column: position_short`
**Solução:**
```bash
# 1. Delete o banco de dados
rm db.sqlite3  # ou del db.sqlite3 no Windows

# 2. Execute o script de setup
python setup_db.py
```

### Django não instalado
**Solução:**
```bash
pip install -r requirements.txt
```

### Erro de migração
**Solução:**
```bash
python manage.py migrate --run-syncdb
```

### Porta 8000 em uso
**Solução:**
```bash
python manage.py runserver 8080
```

### Fixtures não carregam
**Solução:**
```bash
python manage.py loaddata core/fixtures/players.json
```

### ModuleNotFoundError
**Solução:** Certifique-se de que o ambiente virtual está ativado:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

---

## 🧪 Verificar se está funcionando

Execute estes comandos para verificar:

```bash
# Verificar se o servidor está rodando
curl http://localhost:8000/api/players/

# Ou abra no navegador
# http://localhost:8000/swagger/
```

Se você ver a lista de jogadores, está tudo funcionando! 🎉

---

## 📊 Estatísticas do Banco

Após o setup, você terá:
- 25 jogadores NBA com stats reais
- 0 usuários (você criará o primeiro)
- 0 times (criado automaticamente ao registrar)

---

## 🚀 Próximos Passos

1. **Teste a API:**
   - Acesse http://localhost:8000/swagger/
   - Registre um usuário
   - Adicione jogadores ao seu time

2. **Explore o Admin:**
   - Acesse http://localhost:8000/admin/
   - Login com o superusuário
   - Veja todos os dados

3. **Integre com o Frontend:**
   - Configure CORS no .env
   - Aponte o frontend para http://localhost:8000/api

---

## 📞 Ajuda

- **README completo:** [README.md](./README.md)
- **Especificação da API:** [API_SPECIFICATION.md](./API_SPECIFICATION.md)
- **Guia de integração:** [BACKEND_INTEGRATION_GUIDE.md](./BACKEND_INTEGRATION_GUIDE.md)

---

**Desenvolvido com ❤️ para INF1407 - Programação para Web**
