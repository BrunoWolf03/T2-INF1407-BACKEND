# 🔧 Guia de Solução de Problemas - NBA Fantasy Backend

Este documento contém soluções para os problemas mais comuns.

---

## 🚨 Erro: `no such column: position_short`

### Causa
As migrações antigas não refletem a estrutura atual dos models.

### Solução Rápida
```bash
# 1. Delete o banco de dados
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# 2. Execute o script de setup
python setup_db.py
```

### Solução Manual
```bash
# 1. Delete o banco
rm db.sqlite3

# 2. Execute as migrações
python manage.py migrate

# 3. Carregue os fixtures
python manage.py loaddata players
```

---

## 🚨 Erro: `ModuleNotFoundError: No module named 'django'`

### Causa
Django não está instalado ou o ambiente virtual não está ativado.

### Solução
```bash
# 1. Ative o ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt
```

---

## 🚨 Erro: `django.db.utils.OperationalError: no such table`

### Causa
As migrações não foram executadas.

### Solução
```bash
python manage.py migrate
```

---

## 🚨 Erro ao carregar fixtures: `DoesNotExist`

### Causa
Tentando carregar fixtures antes de executar as migrações.

### Solução
```bash
# 1. Execute as migrações primeiro
python manage.py migrate

# 2. Depois carregue os fixtures
python manage.py loaddata players
```

---

## 🚨 Erro: `Port 8000 is already in use`

### Causa
Outro processo está usando a porta 8000.

### Solução Opção 1: Use outra porta
```bash
python manage.py runserver 8080
```

### Solução Opção 2: Mate o processo
```bash
# Windows (PowerShell):
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 🚨 Erro: `CORS header 'Access-Control-Allow-Origin' missing`

### Causa
Frontend não está na lista de origens permitidas.

### Solução
1. Edite o arquivo `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

2. Reinicie o servidor.

---

## 🚨 Erro: `Invalid token` ou `401 Unauthorized`

### Causa
Token JWT expirado ou inválido.

### Solução
1. Faça login novamente para obter um novo token:
```bash
POST /api/auth/login
{
  "email": "seu@email.com",
  "password": "suaSenha",
  "rememberMe": false
}
```

2. Use o novo token nas requisições.

---

## 🚨 Erro: `Team is full (max 5 players)`

### Causa
Tentando adicionar mais de 5 jogadores ao time.

### Solução
Remova um jogador antes de adicionar outro:
```bash
DELETE /api/team/players/{player_id}
```

---

## 🚨 Erro: `Insufficient budget`

### Causa
A soma dos salários excede o budget de 200M.

### Solução
1. Remova jogadores caros do time
2. Ou escolha jogadores mais baratos

---

## 🚨 Erro: `Player already in team`

### Causa
Tentando adicionar o mesmo jogador duas vezes.

### Solução
Escolha um jogador diferente.

---

## 🚨 Swagger não carrega / 404 Error

### Causa
URLs do Swagger não configuradas ou app não instalado.

### Solução
1. Verifique se `drf-spectacular` está instalado:
```bash
pip install drf-spectacular
```

2. Verifique `nba_fantasy/urls.py`:
```python
from drf_spectacular.views import SpectacularSwaggerView
# ... deve ter a URL do swagger
```

3. Reinicie o servidor.

---

## 🚨 Admin não aceita login

### Causa
Superusuário não foi criado.

### Solução
```bash
python manage.py createsuperuser
```

---

## 🚨 Erro ao executar `python manage.py`

### Causa
Não está no diretório correto ou Python não encontrado.

### Solução
```bash
# 1. Navegue até o diretório do projeto
cd C:\Users\lucal\T2-INF1407-BACKEND

# 2. Verifique se manage.py existe
ls manage.py  # Linux/Mac
dir manage.py # Windows

# 3. Verifique a versão do Python
python --version
```

---

## 🚨 Docker: Container sai imediatamente

### Causa
Erro nas migrações ou comando inválido.

### Solução
```bash
# Ver logs
docker-compose logs web

# Recriar do zero
docker-compose down -v
docker-compose up --build
```

---

## 🚨 Fixtures carregam mas jogadores não aparecem

### Causa
Campo `position_short` pode estar errado no fixture.

### Solução
Verifique se o arquivo `core/fixtures/players.json` existe e está correto:
```bash
cat core/fixtures/players.json
```

---

## 🚨 Erro: `SECRET_KEY` warning

### Causa
SECRET_KEY usando valor padrão.

### Solução
1. Gere uma chave secreta:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. Adicione ao `.env`:
```env
SECRET_KEY=sua-chave-gerada-aqui
```

---

## 🚨 Erro: `TemplateDoesNotExist`

### Causa
Tentando acessar URL que não existe.

### Solução
Use as URLs corretas:
- Swagger: http://localhost:8000/swagger/
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/

---

## 🚨 Erro ao importar `decouple`

### Causa
python-decouple não está instalado.

### Solução
```bash
pip install python-decouple
```

---

## 🚨 Todos os testes falhando

### Causa
Banco de dados de teste corrompido.

### Solução
```bash
# Delete o banco de teste
rm test_db.sqlite3

# Execute os testes novamente
python manage.py test
```

---

## 📋 Checklist de Verificação

Use este checklist para verificar se tudo está funcionando:

- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip list`)
- [ ] Banco de dados migrado (`python manage.py showmigrations`)
- [ ] Fixtures carregados (25 jogadores)
- [ ] Servidor rodando na porta 8000
- [ ] Swagger acessível em /swagger/
- [ ] Consegue registrar usuário
- [ ] Consegue fazer login
- [ ] Consegue adicionar jogador ao time

---

## 🆘 Ainda com problemas?

### Reinstalação Completa

Se nada funcionar, faça uma reinstalação completa:

```bash
# 1. Desative o ambiente virtual
deactivate

# 2. Delete tudo
rm -rf venv/           # ou rmdir /s venv no Windows
rm db.sqlite3
rm -rf core/migrations/*.py  # exceto __init__.py

# 3. Recomeçe do zero
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
python setup_db.py
python manage.py runserver 8000
```

---

## 📞 Obter Ajuda

1. **Verifique a documentação:**
   - [README.md](./README.md)
   - [QUICKSTART.md](./QUICKSTART.md)
   - [API_SPECIFICATION.md](./API_SPECIFICATION.md)

2. **Veja os logs:**
   ```bash
   # Logs do Django
   python manage.py runserver --verbosity 3

   # Logs do Docker
   docker-compose logs -f
   ```

3. **Debug mode:**
   - Verifique `.env`: `DEBUG=True`
   - Acesse a URL com erro e veja o traceback completo

---

**Última atualização:** 2025-11-20
