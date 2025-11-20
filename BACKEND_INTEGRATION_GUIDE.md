# Backend Integration Guide

## Quick Start for Backend Developer

Este documento serve como guia rápido para desenvolver o backend Django que se conecta com este frontend.

---

## 1. Copie este documento para o repositório do backend

Ao criar o repositório do backend, copie o arquivo `API_SPECIFICATION.md` para lá. Esse arquivo contém:
- ✅ Todos os endpoints necessários
- ✅ Estrutura de dados (models Django)
- ✅ Formato de request/response
- ✅ Regras de validação
- ✅ Exemplos de uso

---

## 2. Estrutura de Pastas Recomendada (Backend)

```
backend/
├── api/
│   ├── models.py          # Player, User, Team, League
│   ├── serializers.py     # DRF Serializers
│   ├── views.py           # API Views
│   ├── urls.py            # URL routing
│   └── permissions.py     # Custom permissions
├── authentication/
│   ├── views.py           # Login, Register, Password reset
│   └── serializers.py     # Auth serializers
├── config/
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL config
│   └── wsgi.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 3. Models Django Necessários

```python
# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    team_name = models.CharField(max_length=50)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def calculate_rank(self):
        # Implementar lógica de ranking
        pass

class Player(models.Model):
    POSITION_CHOICES = [
        ('PG', 'Point Guard'),
        ('SG', 'Shooting Guard'),
        ('SF', 'Small Forward'),
        ('PF', 'Power Forward'),
        ('C', 'Center'),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    position_short = models.CharField(max_length=2, choices=POSITION_CHOICES)
    team = models.CharField(max_length=100)  # NBA Team
    price = models.DecimalField(max_digits=5, decimal_places=1)
    points = models.IntegerField(default=0)
    photo = models.URLField()

    # Stats
    stats_points = models.DecimalField(max_digits=4, decimal_places=1)  # PPG
    stats_rebounds = models.DecimalField(max_digits=4, decimal_places=1)
    stats_assists = models.DecimalField(max_digits=4, decimal_places=1)
    stats_steals = models.DecimalField(max_digits=4, decimal_places=1)
    stats_blocks = models.DecimalField(max_digits=4, decimal_places=1)

class UserTeam(models.Model):
    FORMATION_CHOICES = [
        ('standard', 'Standard'),
        ('small-ball', 'Small Ball'),
        ('twin-towers', 'Twin Towers'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=5, decimal_places=1, default=200)
    formation = models.CharField(max_length=20, choices=FORMATION_CHOICES, default='standard')
    players = models.ManyToManyField(Player, related_name='teams')

    def total_salary(self):
        return sum(p.price for p in self.players.all())

    def can_add_player(self, player):
        if self.players.count() >= 5:
            return False, "Team is full"
        if self.total_salary() + player.price > self.budget:
            return False, "Insufficient budget"
        return True, "OK"

class League(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, through='LeagueMembership')
    created_at = models.DateTimeField(auto_now_add=True)

class LeagueMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
```

---

## 4. Instalação de Dependências

```txt
# requirements.txt
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
django-cors-headers==4.0.0
drf-spectacular==0.26.2
psycopg2-binary==2.9.6
python-decouple==3.8
```

---

## 5. Configuração do Django (settings.py)

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # Local apps
    'api',
    'authentication',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

# Swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'NBA Fantasy API',
    'DESCRIPTION': 'API for NBA Fantasy Basketball Game',
    'VERSION': '1.0.0',
}

# Custom User Model
AUTH_USER_MODEL = 'api.User'
```

---

## 6. URLs Principais

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/', include('api.urls')),
    path('api/auth/', include('authentication.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## 7. Como Fazer o Frontend Conectar ao Backend

### 7.1. Criar arquivo de configuração no frontend

```typescript
// src/lib/config/api.ts

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  // Auth
  login: `${API_BASE_URL}/auth/login`,
  register: `${API_BASE_URL}/auth/register`,
  logout: `${API_BASE_URL}/auth/logout`,
  forgotPassword: `${API_BASE_URL}/auth/forgot-password`,
  resetPassword: `${API_BASE_URL}/auth/reset-password`,
  changePassword: `${API_BASE_URL}/auth/change-password`,

  // Players
  players: `${API_BASE_URL}/players`,
  player: (id: number) => `${API_BASE_URL}/players/${id}`,

  // Team
  team: `${API_BASE_URL}/team`,
  addPlayer: `${API_BASE_URL}/team/players`,
  removePlayer: (id: number) => `${API_BASE_URL}/team/players/${id}`,
  updateFormation: `${API_BASE_URL}/team/formation`,

  // User
  profile: `${API_BASE_URL}/user/profile`,

  // Leaderboard
  leaderboard: `${API_BASE_URL}/leaderboard`,

  // Dashboard
  dashboardStats: `${API_BASE_URL}/dashboard/stats`,
};
```

### 7.2. Criar serviço de API

```typescript
// src/lib/services/api.ts

import { API_ENDPOINTS } from '$lib/config/api';

let authToken: string | null = null;

export function setAuthToken(token: string) {
  authToken = token;
  localStorage.setItem('authToken', token);
}

export function getAuthToken(): string | null {
  if (!authToken) {
    authToken = localStorage.getItem('authToken');
  }
  return authToken;
}

export function clearAuthToken() {
  authToken = null;
  localStorage.removeItem('authToken');
}

async function fetchAPI(url: string, options: RequestInit = {}) {
  const token = getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }

  return response.json();
}

// Auth API
export const authAPI = {
  login: (email: string, password: string, rememberMe: boolean) =>
    fetchAPI(API_ENDPOINTS.login, {
      method: 'POST',
      body: JSON.stringify({ email, password, rememberMe }),
    }),

  register: (data: any) =>
    fetchAPI(API_ENDPOINTS.register, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: () =>
    fetchAPI(API_ENDPOINTS.logout, { method: 'POST' }),
};

// Players API
export const playersAPI = {
  getAll: (params?: any) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return fetchAPI(API_ENDPOINTS.players + query);
  },

  getById: (id: number) =>
    fetchAPI(API_ENDPOINTS.player(id)),
};

// Team API
export const teamAPI = {
  get: () => fetchAPI(API_ENDPOINTS.team),

  addPlayer: (playerId: number) =>
    fetchAPI(API_ENDPOINTS.addPlayer, {
      method: 'POST',
      body: JSON.stringify({ playerId }),
    }),

  removePlayer: (playerId: number) =>
    fetchAPI(API_ENDPOINTS.removePlayer(playerId), {
      method: 'DELETE',
    }),

  updateFormation: (formation: string) =>
    fetchAPI(API_ENDPOINTS.updateFormation, {
      method: 'PUT',
      body: JSON.stringify({ formation }),
    }),
};
```

### 7.3. Atualizar stores para usar API

```typescript
// src/lib/stores/players.ts

import { writable } from 'svelte/store';
import { playersAPI } from '$lib/services/api';
import type { Player } from './types';

export const availablePlayers = writable<Player[]>([]);
export const playersLoading = writable<boolean>(false);
export const playersError = writable<string | null>(null);

export async function loadPlayers(filters?: any) {
  playersLoading.set(true);
  playersError.set(null);

  try {
    const players = await playersAPI.getAll(filters);
    availablePlayers.set(players);
  } catch (error) {
    playersError.set(error.message);
  } finally {
    playersLoading.set(false);
  }
}
```

### 7.4. Criar arquivo .env no frontend

```env
# .env
VITE_API_URL=http://localhost:8000/api
```

---

## 8. Testando a Integração

### Backend
```bash
python manage.py runserver 8000
```

### Frontend
```bash
npm run dev
```

### Teste manual:
1. Acesse http://localhost:5173/register
2. Crie uma conta
3. Faça login em http://localhost:5173/login
4. Navegue para http://localhost:5173/market
5. Adicione jogadores ao time
6. Verifique http://localhost:5173/my-team

---

## 9. Checklist de Implementação Backend

### Básico
- [ ] Models criados (User, Player, UserTeam, League)
- [ ] Serializers DRF
- [ ] Views/ViewSets
- [ ] URLs configuradas
- [ ] CORS habilitado

### Autenticação
- [ ] Registro de usuário
- [ ] Login com JWT
- [ ] Logout
- [ ] Forgot Password
- [ ] Reset Password
- [ ] Change Password

### CRUD Players
- [ ] GET /players (list com filtros)
- [ ] GET /players/:id

### CRUD Team
- [ ] GET /team
- [ ] POST /team/players (add)
- [ ] DELETE /team/players/:id
- [ ] PUT /team/formation

### Extras
- [ ] Leaderboard
- [ ] Dashboard stats
- [ ] Validações (budget, team size)
- [ ] Swagger/OpenAPI docs
- [ ] Testes unitários

---

## 10. Deploy

### Backend (Render/Railway/Heroku)
```bash
# Procfile
web: gunicorn config.wsgi
```

### Frontend (Vercel/Netlify)
Atualizar .env.production:
```env
VITE_API_URL=https://your-backend.herokuapp.com/api
```

---

## Prompt para Claude (Desenvolvimento Backend)

Cole isso quando pedir ao Claude para desenvolver o backend:

```
Desenvolva o backend Django para este projeto NBA Fantasy Game.

Requisitos:
1. Leia o arquivo API_SPECIFICATION.md completamente
2. Implemente todos os models conforme especificado
3. Crie todos os endpoints da API
4. Configure JWT authentication
5. Adicione validações de negócio (budget, team size)
6. Configure CORS para aceitar requisições do frontend
7. Adicione Swagger/OpenAPI documentation
8. Crie fixtures/seed data com pelo menos 18 jogadores da NBA
9. Implemente sistema de ranking
10. Use TypeScript interfaces como referência para os serializers

Estrutura esperada:
- Django REST Framework
- PostgreSQL database
- JWT authentication
- CORS habilitado
- Swagger docs em /swagger/
- Docker configurado

Frontend está em: [link do repositório]
Especificação completa: API_SPECIFICATION.md
```

---

## Dúvidas?

- Frontend TypeScript types: `src/lib/stores/*.ts`
- API Spec completa: `API_SPECIFICATION.md`
- Componentes do frontend: `src/lib/components/`
