# MitreAI

Aplikacja czatu, która na podstawie opisu komponentu systemu przemysłowego (urządzenie, protokół, sposób dostępu) wskazuje pasujące techniki MITRE ATT&CK wraz z uzasadnieniem, mitygacjami i sposobami wykrywania. Docelowo odpowiedzi generuje LLM z RAG nad bazą ATT&CK.

## Dokumentacja

| Plik | Co zawiera |
|---|---|
| [docs/URUCHOMIENIE.md](docs/URUCHOMIENIE.md) | Jak uruchomić aplikację, testy i co zrobić, gdy coś nie działa |
| [docs/STAN_PROJEKTU.md](docs/STAN_PROJEKTU.md) | Co już działa, jak działa, znane ograniczenia, dziennik zmian |
| [docs/PLAN_BACKEND.md](docs/PLAN_BACKEND.md) | Plan backendu: model danych, endpointy, kolejność prac |

## Szybki start

```bash
cp .env.example .env
```

Uzupełnij w `.env` pola `JWT_SECRET` (`openssl rand -hex 32`), `ADMIN_EMAIL` i `ADMIN_PASSWORD`, potem:

```bash
docker compose up --build -d
```

Aplikacja: http://localhost:8080, Swagger: http://localhost:8080/api/docs. Szczegóły w [docs/URUCHOMIENIE.md](docs/URUCHOMIENIE.md).

## Architektura

| Kontener | Technologia | Port |
|---|---|---|
| `frontend` | React + Vite, serwowany przez nginx, który przekazuje `/api` do backendu | 8080 |
| `backend` | FastAPI, Python 3.13, uv, Beanie | 8000 |
| `mongo` | MongoDB 8.0 | 27017 |

## Struktura repozytorium

```
MitreAI/
├── docker-compose.yml
├── .env.example               # wzór konfiguracji, bez sekretów
├── docs/                      # dokumentacja projektu
├── backend/
│   ├── app/
│   │   ├── main.py            # tworzenie aplikacji, start i zamknięcie połączenia z bazą
│   │   ├── dependencies.py    # łączenie warstw przez Depends, bieżący użytkownik
│   │   ├── core/              # konfiguracja, baza, hasła i JWT, błędy aplikacji
│   │   ├── controllers/       # endpointy HTTP
│   │   ├── services/          # logika biznesowa
│   │   ├── repositories/      # dostęp do bazy danych
│   │   ├── llm/               # wywołania modeli językowych (na razie atrapa)
│   │   ├── models/            # kolekcje MongoDB
│   │   └── schemas/           # kształt żądań i odpowiedzi API
│   └── tests/
└── frontend/
    └── src/
        ├── pages/             # widoki podpięte pod adresy
        ├── components/        # komponenty wielokrotnego użytku (ui, layout, auth, chat, conversations, system)
        ├── context/           # stan wspólny: zalogowany użytkownik, lista rozmów
        ├── hooks/             # useAuth, useConversations, useChat, useModels, useBackendHealth
        ├── api/               # komunikacja z backendem
        ├── types/             # typy odpowiedzi API
        └── styles/            # style globalne
```

Jak działają warstwy i logowanie: [docs/STAN_PROJEKTU.md](docs/STAN_PROJEKTU.md#jak-to-działa).
