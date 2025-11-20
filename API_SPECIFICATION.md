# NBA Fantasy Game - API Specification for Backend

## Overview
This document describes the API endpoints and data structures required by the frontend application. The backend should be developed in Django and provide RESTful APIs.

## Base URL
```
Development: http://localhost:8000/api
Production: https://your-backend-domain.com/api
```

## Authentication
- Use JWT (JSON Web Tokens) for authentication
- Include token in header: `Authorization: Bearer <token>`
- Protected endpoints require valid token

---

## Data Models & TypeScript Interfaces

### Player
```typescript
interface Player {
  id: number;
  name: string;
  position: string;              // Full name: "Point Guard", "Shooting Guard", etc.
  positionShort: 'PG' | 'SG' | 'SF' | 'PF' | 'C';
  team: string;                  // NBA team name
  price: number;                 // Salary in millions (e.g., 42.5)
  points: number;                // Total fantasy points
  photo: string;                 // URL to player photo
  stats: {
    points: number;              // PPG (points per game)
    rebounds: number;            // RPG
    assists: number;             // APG
    steals: number;              // SPG
    blocks: number;              // BPG
  };
}
```

### User
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  teamName: string;              // User's fantasy team name
  rank: number;                  // Global ranking position
  points: number;                // Total fantasy points
  leagues: League[];
}

interface League {
  id: number;
  name: string;
  rank: number;                  // User's rank in this league
}
```

### UserTeam
```typescript
interface UserTeam {
  id: number;
  userId: number;
  name: string;                  // Team name
  budget: number;                // Total salary cap (200)
  players: Player[];             // Array of 5 players max
  formation: 'standard' | 'small-ball' | 'twin-towers';
}
```

### LeaderboardEntry
```typescript
interface LeaderboardEntry {
  rank: number;
  name: string;                  // Username
  points: number;
  team: string;                  // Team name
}
```

---

## API Endpoints

### 1. Authentication

#### POST `/auth/register`
Register a new user

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "confirmPassword": "string",
  "teamName": "string"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "teamName": "Dream Team"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- 400: Validation errors (passwords don't match, email already exists, etc.)

---

#### POST `/auth/login`
Login user

**Request:**
```json
{
  "email": "string",
  "password": "string",
  "rememberMe": boolean
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "teamName": "Dream Team",
    "rank": 1542,
    "points": 1850
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- 401: Invalid credentials
- 400: Validation errors

---

#### POST `/auth/logout`
Logout user (invalidate token)

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

#### POST `/auth/forgot-password`
Request password reset

**Request:**
```json
{
  "email": "string"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent"
}
```

---

#### POST `/auth/reset-password`
Reset password with token

**Request:**
```json
{
  "token": "string",
  "newPassword": "string",
  "confirmPassword": "string"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

---

#### POST `/auth/change-password`
Change password (authenticated)

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "currentPassword": "string",
  "newPassword": "string",
  "confirmPassword": "string"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 2. Players (CRUD)

#### GET `/players`
Get all available players

**Query Parameters:**
- `position` (optional): Filter by position (PG, SG, SF, PF, C)
- `team` (optional): Filter by NBA team
- `maxPrice` (optional): Filter by max price
- `search` (optional): Search by player name
- `sortBy` (optional): Sort by (points, price-high, price-low, name)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "LeBron James",
    "position": "Small Forward",
    "positionShort": "SF",
    "team": "Los Angeles Lakers",
    "price": 42.5,
    "points": 1850,
    "photo": "https://example.com/lebron.jpg",
    "stats": {
      "points": 25.7,
      "rebounds": 7.3,
      "assists": 7.5,
      "steals": 1.3,
      "blocks": 0.5
    }
  }
]
```

---

#### GET `/players/:id`
Get single player details

**Response (200):**
```json
{
  "id": 1,
  "name": "LeBron James",
  "position": "Small Forward",
  "positionShort": "SF",
  "team": "Los Angeles Lakers",
  "price": 42.5,
  "points": 1850,
  "photo": "https://example.com/lebron.jpg",
  "stats": {
    "points": 25.7,
    "rebounds": 7.3,
    "assists": 7.5,
    "steals": 1.3,
    "blocks": 0.5
  }
}
```

---

### 3. User Team (CRUD)

#### GET `/team`
Get current user's team

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "userId": 1,
  "name": "My Team",
  "budget": 200,
  "formation": "standard",
  "players": [
    {
      "id": 1,
      "name": "LeBron James",
      "positionShort": "SF",
      "team": "Los Angeles Lakers",
      "price": 42.5,
      "points": 1850,
      "photo": "https://example.com/lebron.jpg",
      "stats": { /* ... */ }
    }
  ]
}
```

---

#### POST `/team/players`
Add player to team

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "playerId": 1
}
```

**Response (201):**
```json
{
  "message": "Player added successfully",
  "team": { /* updated team object */ }
}
```

**Errors:**
- 400: Team is full (max 5 players)
- 400: Insufficient budget
- 404: Player not found

---

#### DELETE `/team/players/:playerId`
Remove player from team

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Player removed successfully",
  "team": { /* updated team object */ }
}
```

---

#### PUT `/team/formation`
Update team formation

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "formation": "standard" | "small-ball" | "twin-towers"
}
```

**Response (200):**
```json
{
  "message": "Formation updated successfully",
  "team": { /* updated team object */ }
}
```

---

### 4. User Management

#### GET `/user/profile`
Get current user profile

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "teamName": "Dream Team",
  "rank": 1542,
  "points": 1850,
  "leagues": [
    {
      "id": 1,
      "name": "Friends League",
      "rank": 3
    }
  ]
}
```

---

#### PUT `/user/profile`
Update user profile

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "username": "string",
  "teamName": "string"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": { /* updated user object */ }
}
```

---

### 5. Leaderboard

#### GET `/leaderboard`
Get global leaderboard

**Query Parameters:**
- `league` (optional): Filter by league (global, friends, country)
- `timeframe` (optional): Filter by time (overall, month, week)
- `limit` (optional): Number of entries (default: 100)

**Response (200):**
```json
[
  {
    "rank": 1,
    "name": "Supreme Champion",
    "points": 2450,
    "team": "The Unbeatable"
  },
  {
    "rank": 2,
    "name": "Tactical Master",
    "points": 2380,
    "team": "Hoops Dynasty"
  }
]
```

---

### 6. Dashboard Stats

#### GET `/dashboard/stats`
Get user dashboard statistics

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "totalPoints": 1850,
  "rank": 1542,
  "teamValue": 189.5,
  "playersCount": 5,
  "weeklyChange": 125,
  "recentActivity": [
    {
      "playerId": 1,
      "playerName": "LeBron James",
      "action": "scored",
      "value": 28,
      "points": 28,
      "timestamp": "2024-01-15T20:30:00Z"
    }
  ]
}
```

---

## Important Implementation Notes

### 1. CORS Configuration
Backend must allow requests from frontend domain:

```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Development
    "https://your-frontend-domain.com"  # Production
]

CORS_ALLOW_CREDENTIALS = True
```

### 2. JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### 3. Validation Rules
- **Username**: 3-30 characters, alphanumeric and underscores
- **Email**: Valid email format
- **Password**: Minimum 8 characters
- **Team Name**: 3-50 characters
- **Budget**: Max 200M total
- **Players**: Max 5 per team

### 4. Business Rules
- Users can only manage their own team
- Players cannot be duplicated in a team
- Total team salary cannot exceed budget (200M)
- Formation must be valid: standard (2G-2F-1C), small-ball (3G-2F-0C), twin-towers (2G-1F-2C)

---

## Frontend Integration Example

### Fetch Players
```typescript
const response = await fetch('http://localhost:8000/api/players?position=PG');
const players: Player[] = await response.json();
```

### Add Player to Team
```typescript
const response = await fetch('http://localhost:8000/api/team/players', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ playerId: 1 })
});
```

### Login
```typescript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password, rememberMe: false })
});
const { user, token } = await response.json();
```

---

## Environment Variables (Backend)

Create a `.env` file in the backend:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/nba_fantasy
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.com
```

---

## Testing Checklist

Backend must support:
- ✅ User registration with validation
- ✅ User login with JWT
- ✅ Password reset flow
- ✅ CRUD operations on players
- ✅ CRUD operations on user teams
- ✅ Budget validation
- ✅ Team size limits (max 5 players)
- ✅ Leaderboard calculation
- ✅ User ranking system
- ✅ Different views per user
- ✅ Swagger/OpenAPI documentation
- ✅ CORS properly configured

---

## Additional Features (Optional)

- Real-time updates using WebSockets
- Player statistics auto-update from NBA API
- League management (create/join leagues)
- Trade system between users
- Draft system for new leagues
- Season/gameweek management
- Push notifications for player updates

---

## Swagger Documentation

Backend should expose Swagger UI at:
- Development: `http://localhost:8000/swagger/`
- Production: `https://your-backend-domain.com/swagger/`

Use `drf-spectacular` or `drf-yasg` for Django REST Framework.

---

## Contact

For questions about the API specification, please refer to this document or the frontend repository:
- Frontend Repo: [Link to frontend repository]
- TypeScript interfaces: `src/lib/stores/*.ts`
