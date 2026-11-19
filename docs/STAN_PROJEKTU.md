# Stan projektu MitreAI

Ten plik opisuje, co już działa, jak to działa i co zostało do zrobienia. Jest aktualizowany przy każdej zmianie w projekcie.

- Ostatnia aktualizacja: 2026-11-19
- Gałąź robocza backendu: `feature/backend`
- Plan całości: [PLAN_BACKEND.md](PLAN_BACKEND.md), uruchamianie: [URUCHOMIENIE.md](URUCHOMIENIE.md)

## Postęp

| Etap | Stan |
|---|---|
| 1. Szkielet: trzy kontenery, warstwy backendu, pages i components we frontendzie | zrobione |
| 2. Baza: połączenie z MongoDB, modele kolekcji z indeksami | zrobione |
| 3. Logowanie: hasła, JWT, konto admina, formularz i ochrona tras we frontendzie | zrobione |
| 4. Zakładanie i edycja kont przez administratora (API) | zrobione |
| 5. Rozmowy: tworzenie, lista, zmiana tytułu i modelu, archiwizacja, usuwanie (API) | zrobione |
| 6. Wiadomości: wysyłanie promptu, atrapa modelu, lista modeli (API) | zrobione |
| 7. Dokumenty: pliki dołączane do promptu (GridFS) | do zrobienia (czeka na decyzję o typach plików i limicie) |
| 8. Frontend czatu: lista rozmów, czat, wybór modelu, menu na telefon | zrobione |
| 9. Frontend: panel administratora (zakładanie i edycja kont) | do zrobienia |
| Później: prawdziwe modele LLM i RAG nad MITRE ATT&CK | do ustalenia |

## Dostępne endpointy

| Metoda | Ścieżka | Dostęp | Co robi |
|---|---|---|---|
| GET | `/api/health` | publiczny | Stan aplikacji i bazy: 200 albo 503, gdy baza nie odpowiada |
| POST | `/api/auth/login` | publiczny | Logowanie (formularz: `username` = e-mail, `password`), zwraca token JWT |
| GET | `/api/auth/me` | zalogowany | Dane zalogowanego użytkownika |
| POST | `/api/users` | admin | Załóż konto (e-mail, hasło min. 8 znaków, nazwa, rola) |
| GET | `/api/users` | admin | Lista kont, od najstarszego |
| GET | `/api/users/{id}` | admin | Szczegóły konta |
| PATCH | `/api/users/{id}` | admin | Zmień nazwę, rolę, aktywność lub hasło |
| GET | `/api/models` | zalogowany | Dostępne modele z oznaczeniem domyślnego |
| GET | `/api/conversations` | zalogowany | Moje rozmowy, od ostatnio aktywnej; `?archived=true` pokazuje archiwum |
| POST | `/api/conversations` | zalogowany | Nowa rozmowa (opcjonalnie `title`, `model`) |
| GET | `/api/conversations/{id}` | właściciel | Szczegóły rozmowy |
| PATCH | `/api/conversations/{id}` | właściciel | Zmień tytuł, model, archiwizuj |
| DELETE | `/api/conversations/{id}` | właściciel | Usuń rozmowę razem z wiadomościami |
| GET | `/api/conversations/{id}/messages` | właściciel | Wiadomości rozmowy, od najstarszej |
| POST | `/api/conversations/{id}/messages` | właściciel | Wyślij prompt (formularz: `content`, opcjonalnie `model`), zwraca obie wiadomości i rozmowę |

Pełna dokumentacja z możliwością wywołania: http://localhost:8080/api/docs

### Kody błędów

Każdy błąd aplikacji ma postać `{"detail": "komunikat po polsku"}`.

| Kod | Kiedy |
|---|---|
| 401 | brak tokenu, token nieważny lub wygasły, złe dane logowania, konto nieaktywne |
| 403 | zwykły użytkownik próbuje operacji administratora |
| 404 | zasób nie istnieje albo należy do innego użytkownika |
| 409 | e-mail jest już zajęty; admin próbuje zablokować siebie albo odebrać sobie rolę |
| 422 | błędne dane wejściowe (np. za krótkie hasło, pusty prompt, nieznany model). Przy błędach walidacji FastAPI `detail` jest listą pól. |

## Jak to działa

### Droga żądania

```
przeglądarka --> nginx (kontener frontend, :8080)
                   |-- /api/...  --> backend FastAPI (:8000) --> MongoDB (:27017)
                   '-- reszta    --> zbudowana aplikacja React (index.html)
```

Frontend i API są pod jednym adresem, więc przeglądarka nie potrzebuje CORS. nginx zwraca `index.html` dla każdego nieznanego adresu, dzięki czemu odświeżenie np. `/login` działa.

### Warstwy backendu

Każde żądanie przechodzi przez warstwy w jednym kierunku:

| Warstwa | Katalog | Odpowiada za | Nie robi |
|---|---|---|---|
| Kontroler | `app/controllers/` | przyjęcie żądania, wywołanie serwisu, kształt odpowiedzi | logiki, zapytań do bazy |
| Serwis | `app/services/` | logika biznesowa, zgłaszanie błędów domenowych | nic nie wie o HTTP |
| Repozytorium | `app/repositories/` | zapytania do MongoDB | logiki |
| Integracja z modelami | `app/llm/` | wywołania modeli językowych (na razie atrapa) | logiki rozmów |
| Model | `app/models/` | kształt dokumentów w kolekcjach i indeksy | |
| Schemat | `app/schemas/` | kształt i walidacja danych wejściowych oraz wyjściowych API | |

Pozostałe elementy:

- `app/dependencies.py` tworzy obiekty i łączy warstwy przez `Depends`, w kolejności: konfiguracja → repozytoria → serwisy → zalogowany użytkownik. W testach dowolną warstwę można podmienić przez `app.dependency_overrides`.
- `app/core/exceptions.py` zawiera błędy domenowe (`AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, `ConflictError`, `InvalidRequestError`). Serwis zgłasza błąd, a `app/core/error_handlers.py` zamienia go na kod HTTP z polem `detail`.
- `app/core/config.py` czyta konfigurację ze zmiennych środowiskowych i pliku `.env`.

### Logowanie

1. Użytkownik wysyła e-mail i hasło z formularza na `/login`. Frontend robi `POST /api/auth/login` jako formularz (`username`, `password`).
2. `AuthService.login`:
   - zamienia e-mail na małe litery i szuka konta,
   - sprawdza hasło przez argon2. Gdy konto nie istnieje, i tak liczy hash na sztucznym haśle, żeby czas odpowiedzi nie zdradzał, czy e-mail jest w bazie,
   - przy złym e-mailu i przy złym haśle zwraca ten sam błąd 401 „Nieprawidłowy e-mail lub hasło”,
   - odrzuca konto nieaktywne,
   - zapisuje `last_login_at` i wystawia token JWT (HS256, `sub` = id użytkownika, ważny `JWT_EXPIRE_MINUTES` minut).
3. Frontend zapisuje token w `localStorage` (klucz `mitreai.accessToken`), pobiera `GET /api/auth/me` i zapamiętuje użytkownika w `AuthProvider`.
4. Każde kolejne żądanie z frontendu ma nagłówek `Authorization: Bearer <token>`, który dokleja `api/client.ts`.
5. Po stronie backendu chroniony endpoint korzysta z `CurrentUserDep`. Ta zależność odczytuje token, sprawdza podpis i datę ważności, ładuje użytkownika z bazy i sprawdza, czy konto jest aktywne. Dzięki temu dezaktywacja konta odcina dostęp od razu, także z wcześniej wydanym tokenem.
6. Endpointy administratora korzystają z `AdminUserDep`, która dodatkowo wymaga roli `admin` (inaczej 403).
7. Po odświeżeniu strony `AuthProvider` odczytuje token z `localStorage` i pyta `/api/auth/me`. Gdy token wygasł, usuwa go i `RequireAuth` przenosi na `/login`.
8. Wylogowanie usuwa token z przeglądarki.

### Konta użytkowników

- Przy każdym starcie backend sprawdza, czy w bazie jest jakikolwiek administrator. Jeśli nie ma, zakłada konto z `ADMIN_EMAIL` i `ADMIN_PASSWORD`. Restart nie tworzy duplikatów.
- Samodzielnej rejestracji nie ma. Konta zakłada administrator przez `POST /api/users`. E-mail jest zapisywany małymi literami i musi być unikalny (409 przy duplikacie).
- `PATCH /api/users/{id}` zmienia tylko przesłane pola. Nowe hasło jest od razu hashowane. Dezaktywacja (`is_active: false`) odcina dostęp natychmiast.
- Administrator nie może zablokować własnego konta ani odebrać sobie roli `admin` (409), żeby system nie został bez administratora.
- Kont nie da się usunąć. Zamiast tego się je dezaktywuje, a historia rozmów zostaje.

### Rozmowy

- Każda rozmowa ma właściciela (`user_id`). `ConversationService.get_conversation` zwraca 404, gdy rozmowa nie istnieje albo należy do kogoś innego. Wszystkie operacje na rozmowie i jej wiadomościach przechodzą przez tę metodę. Administrator też nie widzi cudzych rozmów.
- Lista jest posortowana po `updated_at` malejąco. `updated_at` zmienia się tylko przy nowej wiadomości, więc zmiana tytułu czy archiwizacja nie przestawiają kolejności.
- Archiwizacja (`is_archived: true`) chowa rozmowę z listy. Archiwum pokazuje `?archived=true`.
- Usunięcie kasuje najpierw wiadomości rozmowy, potem samą rozmowę.

### Wysyłanie promptu

`MessageService.send_message`:

1. Sprawdza, czy rozmowa należy do użytkownika.
2. Ustala model: ten z formularza, a jeśli go nie ma, model rozmowy. Model spoza `AVAILABLE_MODELS` daje 422 „Nieznany model”.
3. Zapisuje wiadomość użytkownika (`role: user`).
4. Pobiera całą historię rozmowy i przekazuje ją dostawcy modelu (`LLMProvider.generate`).
5. Zapisuje odpowiedź (`role: assistant`) razem z nazwą modelu, tokenami i polem `analysis` (na razie puste).
6. Aktualizuje rozmowę: `updated_at`, model (wybrany model zostaje modelem rozmowy) i tytuł. Tytuł powstaje tylko wtedy, gdy rozmowa go jeszcze nie ma: z pierwszej linii promptu, maksymalnie 60 znaków.
7. Zwraca obie wiadomości i zaktualizowaną rozmowę, żeby frontend mógł od razu odświeżyć czat i panel boczny.

Prompt jest przesyłany jako formularz, a nie JSON, bo w kroku 7 dojdą do niego pliki. Pusty prompt (same spacje) i prompt dłuższy niż 20 000 znaków dają 422.

### Modele językowe

- Lista modeli pochodzi z `AVAILABLE_MODELS` w `.env` (lista JSON). Pierwszy jest domyślny. Obsługuje ją `ModelService`: buduje listę z oznaczeniem modelu domyślnego (kontroler `/api/models` tylko ją zwraca) i sprawdza, czy wybrany model jest na liście.
- `app/llm/provider.py` definiuje interfejs `LLMProvider` z jedną metodą `generate(model, history)`, która zwraca `ModelReply` (treść, tokeny, `analysis`).
- Teraz działa `MockProvider` (`app/llm/mock_provider.py`), który zawsze odpowiada „Odpowiedź z modelu <nazwa>”.
- Prawdziwy model będzie kolejną klasą z tą samą metodą `generate`. Wystarczy podmienić ją w `get_llm_provider` w `dependencies.py`, bez zmian w serwisach i endpointach.

### Baza danych

| Kolekcja | Zawartość | Indeksy |
|---|---|---|
| `users` | konta: e-mail, hash hasła, nazwa, rola, aktywność | `email` (unikalny) |
| `conversations` | rozmowy: właściciel, tytuł, model, daty, archiwum | `(user_id, updated_at malejąco)` |
| `messages` | wiadomości: rozmowa, rola, treść, model, tokeny, `analysis` | `(conversation_id, created_at)` |
| `documents` | metadane plików dołączonych do wiadomości | `message_id` |

Kolekcje i indeksy zakłada Beanie przy starcie backendu. `documents` czeka na krok 7. Wiadomości są sortowane po `created_at`, a przy tej samej dacie po `_id`, bo Mongo zapisuje czas z dokładnością do milisekundy. Szczegóły pól: [PLAN_BACKEND.md, sekcja 5](PLAN_BACKEND.md#5-model-danych).

### Frontend

| Katalog | Zawartość |
|---|---|
| `src/pages/` | widoki pod adresami: `ChatPage` (`/` nowa rozmowa, `/c/:conversationId` istniejąca), `LoginPage` (`/login`), `NotFoundPage` |
| `src/components/ui/` | ogólne elementy: `Button`, `TextInput`, `StatusBadge`, `Icons` |
| `src/components/layout/` | `AppLayout` (układ, menu na telefon) i `Sidebar` (panel boczny jak w ChatGPT) |
| `src/components/auth/` | `RequireAuth` (przekierowuje niezalogowanych na `/login`), `AccountPanel` (nazwa, e-mail, „Wyloguj”) |
| `src/components/conversations/` | `ConversationList` i `ConversationListItem` (historia, zmiana nazwy, usuwanie) |
| `src/components/chat/` | `ChatComposer` (pole wiadomości), `MessageList` i `MessageBubble` (wiadomości), `ModelSelect` (wybór modelu) |
| `src/components/system/` | `BackendStatusBadge` (kropka stanu backendu i bazy) |
| `src/context/` | `AuthProvider` (zalogowany użytkownik) i `ConversationsProvider` (lista rozmów wspólna dla panelu i czatu) |
| `src/hooks/` | `useAuth`, `useConversations`, `useChat` (rozmowa i wysyłanie), `useModels`, `useBackendHealth` |
| `src/api/` | `client.ts` (fetch z tokenem i obsługą błędów) i po jednym pliku na zasób: `authApi`, `conversationsApi`, `messagesApi`, `modelsApi`, `healthApi` |
| `src/types/` | typy odpowiedzi API: `auth.ts`, `chat.ts`, `health.ts` |

### Czat we frontendzie

1. `AppLayout` opakowuje zalogowaną część w `ConversationsProvider`, który raz pobiera listę rozmów. Panel boczny i czat korzystają z tej samej listy, więc nowa rozmowa, nowy tytuł czy usunięcie od razu widać w obu miejscach.
2. `ChatPage` bierze `conversationId` z adresu i przekazuje go do `useChat`. Hook pobiera rozmowę i jej wiadomości. Nieistniejąca albo cudza rozmowa pokazuje „Nie znaleziono rozmowy”.
3. Wysłanie wiadomości (`useChat.send`):
   - od razu pokazuje wiadomość użytkownika i wskaźnik „pisze”,
   - na stronie `/` najpierw zakłada rozmowę (`POST /api/conversations`) z wybranym modelem,
   - wysyła prompt (`POST .../messages` jako `FormData`, gotowe pod pliki z kroku 7),
   - podmienia tymczasową wiadomość na odpowiedź z serwera i aktualizuje rozmowę na liście (tytuł, kolejność),
   - po nowej rozmowie przechodzi na `/c/<id>` bez ponownego pobierania tego, co już ma.
4. Przy błędzie tymczasowa wiadomość znika, nad polem pojawia się komunikat, a tekst wraca do pola, żeby można było wysłać go jeszcze raz.
5. Wybór modelu: domyślnie model rozmowy (dla nowej rozmowy model domyślny z `/api/models`). Zmieniony model idzie z następną wiadomością, a backend zapisuje go jako model rozmowy.
6. Stan w `useChat` jest przypisany do konkretnej rozmowy, a „ładowanie” i „pusta rozmowa” wynikają z porównania z adresem. Dzięki temu efekt tylko pobiera dane i nie ustawia stanu synchronicznie (zgodnie z regułą `set-state-in-effect`).
7. Gdy serwer odrzuci token (401), `api/client.ts` wysyła zdarzenie `mitreai:unauthorized`, a `AuthProvider` wylogowuje użytkownika i przenosi go na `/login`.
8. Na ekranach węższych niż 768 px panel boczny chowa się za przyciskiem menu i wysuwa nad treść; kliknięcie w tło albo w rozmowę go zamyka.

### Testy

45 testów backendu (`uv run pytest`). Testy z bazą działają na prawdziwym MongoDB w osobnej bazie `mitreai_test`, czyszczonej po każdym teście. Fixture'y `admin_headers`, `user_headers` i `other_user_headers` z `tests/conftest.py` dają gotowe nagłówki z tokenem.

Testy nie korzystają z modelu podpiętego w aplikacji. `tests/conftest.py` podmienia `get_llm_provider` na `FakeLLMProvider` z `tests/fakes.py`, który odpowiada „Testowa odpowiedź modelu <nazwa>” i zapisuje, z jaką historią go wywołano (fixture `llm_provider`). Dzięki temu po podpięciu prawdziwego modelu testy nadal będą szybkie, darmowe i powtarzalne. Sam `MockProvider` ma osobny test w `test_llm.py`.

| Plik | Co sprawdza |
|---|---|
| `test_health.py` | health z podmienionym repozytorium, bez bazy (200, 503, Swagger pod `/api`) |
| `test_llm.py` | odpowiedź `MockProvider` z nazwą modelu |
| `test_security.py` | hashowanie haseł i tokeny (ważny, wygasły, podpisany innym kluczem, uszkodzony) |
| `test_auth.py` | admin przy starcie bez duplikatów, logowanie niezależne od wielkości liter, te same błędy dla złego e-maila i hasła, `/me`, dezaktywacja konta |
| `test_users.py` | zakładanie kont, duplikat, za krótkie hasło, 403 dla zwykłego użytkownika, dezaktywacja, reset hasła, admin nie może zablokować siebie, 404 |
| `test_conversations.py` | model domyślny, nieznany model, lista tylko własnych rozmów, 404 dla cudzej rozmowy, zmiana tytułu i modelu, archiwum, usuwanie z wiadomościami |
| `test_messages.py` | odpowiedź modelu, przekazanie modelowi całej historii rozmowy, tytuł z promptu i jego skracanie, wybór modelu, nieznany model, pusty prompt, kolejność wiadomości, przesuwanie rozmowy na górę listy, cudza rozmowa, lista modeli |

## Znane ograniczenia

- Token jest w `localStorage`. Skrypt wstrzyknięty na stronę (XSS) mógłby go odczytać. Bezpieczniejszy wariant to ciasteczko `httpOnly`.
- Wylogowanie tylko usuwa token z przeglądarki. Sam token działa do końca ważności (domyślnie 60 minut). Nie ma refresh tokenów.
- Brak limitu prób logowania.
- Odpowiedzi są wyświetlane jako zwykły tekst, bez formatowania Markdown. Warto to dodać razem z prawdziwym modelem.
- Archiwum rozmów działa w API, ale nie ma go jeszcze w interfejsie.
- Usuwanie rozmowy potwierdza zwykłe okno przeglądarki (`confirm`), a błędy zmiany nazwy i usuwania pokazuje `alert`.
- Frontend nie ma testów automatycznych; jest sprawdzany ręcznie w przeglądarce.
- Listy rozmów, wiadomości i kont nie mają stronicowania.
- Jeśli wywołanie modelu się nie powiedzie, wiadomość użytkownika zostaje zapisana bez odpowiedzi. Przy atrapie to się nie zdarza; trzeba to obsłużyć przy prawdziwym modelu.
- `npm audit` zgłasza 5 podatności `high` w `picomatch`. To narzędzie używane tylko przy budowaniu, nie trafia do przeglądarki.
- Backend działa na Pythonie 3.13. Instalacja 3.12 przez uv nie działała na komputerze deweloperskim.

## Dziennik zmian

### 2026-11-19: porządki w backendzie

- Oznaczenie modelu domyślnego przeniesione z kontrolera `/api/models` do `ModelService`.
- Testy dostały własną atrapę modelu (`FakeLLMProvider`) podpinaną w `conftest.py`, niezależną od modelu ustawionego w aplikacji.
- Nowe testy: przekazanie modelowi całej historii rozmowy i odpowiedź `MockProvider`.

### 2026-11-17: frontend czatu

- Panel boczny: lista rozmów od ostatnio aktywnej, „Nowa rozmowa”, zmiana nazwy (ołówek, Enter zapisuje, Esc anuluje) i usuwanie (kosz).
- Czat: wiadomości jako dymki, wskaźnik „pisze”, Enter wysyła, Shift+Enter nowa linia, automatyczne przewijanie, wybór modelu.
- Adresy rozmów `/c/<id>`, odświeżenie strony wczytuje rozmowę z serwera.
- Menu na telefon (przycisk w górnym pasku), więc na wąskim ekranie widać historię i „Wyloguj”.
- Automatyczne wylogowanie, gdy serwer odrzuci token.
- Sprawdzone w przeglądarce: pierwsza wiadomość zakłada rozmowę, zmiana modelu, druga rozmowa trafia na górę, przełączanie rozmów, zmiana nazwy przetrwa odświeżenie, usunięcie otwartej rozmowy wraca na `/`, menu na telefonie. Ruch sieciowy bez zbędnych zapytań.

### 2026-11-17: konta, rozmowy, wiadomości (API)

- Konta: `POST/GET /api/users`, `GET/PATCH /api/users/{id}`, tylko dla admina; ochrona przed zablokowaniem własnego konta.
- Rozmowy: pełny CRUD z kontrolą właściciela, archiwum, kaskadowe usuwanie wiadomości.
- Wiadomości: wysyłanie promptu z odpowiedzią atrapy modelu, historia rozmowy, automatyczny tytuł.
- Modele: `GET /api/models`, lista z `AVAILABLE_MODELS`, warstwa `app/llm/` z interfejsem `LLMProvider` i `MockProvider`.
- Nowy błąd domenowy `InvalidRequestError` (422).
- Sprawdzone: 43 testy oraz scenariusz przez nginx (admin zakłada konta, użytkownik rozmawia z atrapą, drugi użytkownik nie widzi cudzej rozmowy, usuwanie).

### 2026-11-17: dokumentacja

- `docs/URUCHOMIENIE.md` i ten plik. README stał się spisem treści.

### 2026-11-17: logowanie

- Backend: hasła argon2 (`pwdlib`), tokeny JWT (`PyJWT`), `/api/auth/login`, `/api/auth/me`, konto admina przy starcie, wspólna obsługa błędów domenowych.
- Frontend: działający formularz logowania, `AuthProvider`, ochrona tras, panel konta z wylogowaniem.
- `.env` jest teraz wymagany (`JWT_SECRET`).
- Sprawdzone: testy, logowanie w przeglądarce (poprawne i błędne hasło), utrzymanie sesji po odświeżeniu, wylogowanie.

### 2026-11-17: szkielet

- Trzy kontenery: frontend (React + Vite, nginx), backend (FastAPI, Python 3.13, uv), MongoDB 8.0.
- Backend w warstwach, `/api/health`, Swagger pod `/api/docs`, modele czterech kolekcji z indeksami.
- Frontend z `pages/` i `components/`, wygląd czatu z panelem bocznym.
