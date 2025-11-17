# T2-INF1407-BACKEND

docs/

Aqui ficam:

documentação da API

arquitetura do sistema

diagramas

descrição das entidades

Bom para apresentar no ProgWeb e deixar o repo com cara profissional.

src/main/java/com/brunowolf/nba_fantasy/
✔ controller/

Controladores REST (endpoints).
Ex:

PlayerController

TeamController

AuthController

✔ service/

Regras de negócio.
Ex:

calcular pontuação do fantasy

validar lineup

simular partida

✔ entity/

Mapeamento JPA:

Player

Team

Game

User

✔ repository/

Interfaces do Spring Data JPA.

✔ dto/

Objetos de transporte (entrada/saída da API).

✔ config/

Configurações da aplicação:

segurança / JWT

CORS

beans customizados

✔ exceptions/

Central de tratamento:

GlobalExceptionHandler

erros personalizados

src/main/resources/

Onde ficam:

configs da aplicação

schema/seed

se quiser: swagger estático

scripts/

Scripts pra banco:

criar tabelas

popular jogadores da NBA

.github/workflows/

CI usando GitHub Actions:

rodar testes

fazer build

rodar linter (se tiver)

📦 docker-compose.yml (opcional, mas recomendado!)

Algo como: