# Jak uruchomić MitreAI

## Wymagania

| Do czego | Co zainstalować |
|---|---|
| Uruchomienie całości | Docker Desktop (z włączonym silnikiem) |
| Praca nad backendem bez Dockera | [uv](https://docs.astral.sh/uv/) (sam pobierze Pythona 3.13) |
| Praca nad frontendem bez Dockera | Node.js 24 i npm |

## Pierwsze uruchomienie

1. Skopiuj wzór konfiguracji:

   ```bash
   cp .env.example .env
   ```

2. Uzupełnij w `.env`:

   | Zmienna | Co wpisać |
   |---|---|
   | `JWT_SECRET` | losowy ciąg, co najmniej 32 znaki: `openssl rand -hex 32` |
   | `ADMIN_EMAIL` | e-mail pierwszego administratora |
   | `ADMIN_PASSWORD` | hasło pierwszego administratora |
   | `AVAILABLE_MODELS` | opcjonalnie: lista modeli w formacie JSON, pierwszy jest domyślny (domyślnie `["mock-small","mock-large"]`) |

   Plik `.env` jest w `.gitignore` i nie trafia do repozytorium.

3. Zbuduj i uruchom kontenery:

   ```bash
   docker compose up --build -d
   ```

   Kontenery startują po kolei: `mongo`, potem `backend` (gdy baza odpowiada), potem `frontend` (gdy backend odpowiada). Przy pierwszym starcie backend zakłada konto administratora z `.env`.

4. Otwórz aplikację i zaloguj się danymi administratora. Wpisz opis komponentu i naciśnij Enter: rozmowa pojawi się w panelu bocznym, a odpowie atrapa modelu.

## Adresy

| Co | Adres |
|---|---|
| Aplikacja | http://localhost:8080 |
| Swagger (dokumentacja API) | http://localhost:8080/api/docs |
| Stan backendu i bazy | http://localhost:8080/api/health |
| Backend bezpośrednio | http://localhost:8000/api/docs |
| MongoDB (np. dla MongoDB Compass) | `mongodb://localhost:27017` |

Wszystkie porty są wystawione tylko na `127.0.0.1`. Zmienisz je w `.env` (`FRONTEND_PORT`, `BACKEND_PORT`, `MONGO_PORT`).

## Logowanie w Swaggerze

1. Otwórz http://localhost:8080/api/docs i kliknij **Authorize**.
2. W polu `username` wpisz e-mail, w `password` hasło, potem **Authorize**.
3. Od teraz Swagger dołącza token do każdego żądania. Token jest ważny 60 minut (`JWT_EXPIRE_MINUTES`).

## Szybki test API w Swaggerze

1. Zaloguj się jako administrator (**Authorize**, jak wyżej).
2. `POST /api/users`: załóż konto, np. `{"email": "jan@example.com", "password": "haslo-jana-123", "display_name": "Jan"}`.
3. Kliknij **Authorize** → **Logout** i zaloguj się jako `jan@example.com`.
4. `POST /api/conversations` z pustym `{}`: zapamiętaj `id` z odpowiedzi.
5. `POST /api/conversations/{conversation_id}/messages`: wpisz `id`, w `content` dowolny opis komponentu, `model` zostaw pusty albo wpisz `mock-large`.
6. W odpowiedzi `assistant_message.content` to „Odpowiedź z modelu …”, a `conversation.title` to początek Twojego promptu.
7. `GET /api/conversations` pokazuje rozmowę na górze listy.

## Codzienna praca z Dockerem

| Cel | Polecenie |
|---|---|
| Uruchomienie | `docker compose up -d` |
| Przebudowa po zmianach w kodzie | `docker compose up --build -d` |
| Stan kontenerów | `docker compose ps` |
| Logi backendu na żywo | `docker compose logs -f backend` |
| Zatrzymanie (dane zostają) | `docker compose down` |
| Zatrzymanie i usunięcie danych bazy | `docker compose down -v` |

Po `docker compose down -v` baza jest pusta, a backend przy kolejnym starcie znowu zakłada administratora z `.env`.

## Praca z przeładowaniem kodu (bez przebudowy obrazów)

Baza zostaje w Dockerze, a backend i frontend działają lokalnie i same przeładowują się po każdej zmianie w kodzie. Jeśli kontenery `backend` i `frontend` działają, najpierw je zatrzymaj, żeby zwolnić porty:

```bash
docker compose stop backend frontend
```

```bash
docker compose up -d mongo
```

Backend, w katalogu `backend/` (czyta konfigurację z głównego `.env`):

```bash
uv sync
```

```bash
uv run uvicorn app.main:app --reload
```

Frontend, w katalogu `frontend/`:

```bash
npm install
```

```bash
npm run dev
```

Aplikacja jest wtedy pod http://localhost:5173. Vite przekazuje `/api` do backendu na porcie 8000.

## Testy i sprawdzanie kodu

Backend, w katalogu `backend/`. Testy logowania korzystają z prawdziwego MongoDB, więc baza musi działać (`docker compose up -d mongo`). Testy używają osobnej bazy `mitreai_test` i czyszczą ją po każdym teście, więc nie ruszają Twoich danych.

```bash
uv run pytest
```

```bash
uv run ruff check . && uv run ruff format --check .
```

Frontend, w katalogu `frontend/`:

```bash
npm run lint && npm run build
```

## Gdy coś nie działa

| Objaw | Przyczyna i rozwiązanie |
|---|---|
| `failed to connect to the docker API` | Silnik Dockera nie działa. Uruchom Docker Desktop i poczekaj, aż pokaże „Engine running”. |
| `env file .env not found` | Brak pliku `.env`. Zrób krok 1 i 2 z „Pierwszego uruchomienia”. |
| Backend nie wstaje, w `docker compose logs backend` jest błąd o `jwt_secret` | `JWT_SECRET` jest pusty albo krótszy niż 32 znaki. |
| W logach backendu: „Brak konta administratora” | W bazie nie ma admina, a `ADMIN_EMAIL` lub `ADMIN_PASSWORD` jest pusty. Uzupełnij `.env` i zrestartuj backend: `docker compose restart backend`. |
| Hasło administratora z `.env` nie działa | Admin dostaje hasło z `.env` tylko przy pierwszym starcie. Późniejsza zmiana `.env` nie zmienia hasła w bazie. Żeby założyć admina od nowa: `docker compose down -v` (usuwa wszystkie dane), potem `docker compose up -d`. |
| `port is already allocated` | Port jest zajęty przez inny program. Zmień `FRONTEND_PORT`, `BACKEND_PORT` lub `MONGO_PORT` w `.env`. |
| Testy kończą się `ServerSelectionTimeoutError` | MongoDB nie działa. Uruchom `docker compose up -d mongo`. |
| Wysłanie promptu zwraca 422 „Nieznany model” | Nazwa modelu nie jest na liście `AVAILABLE_MODELS`. Sprawdź `GET /api/models`. |
| Frontend pokazuje „Backend niedostępny” | Backend nie działa albo jeszcze startuje. Sprawdź `docker compose ps` i `docker compose logs backend`. |
