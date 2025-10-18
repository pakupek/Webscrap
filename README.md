## Skopiuj repozytorium:

```bash
git clone https://github.com/pakupek/Webscrap
```

## Utwórz kontenery za pomocą podanej komendy. Dla Windows potrzebny będzie terminal WSL
 ```bash
docker compose up --build
```
W tym momencie kontenery zostaną utworzone dla django jak i bazy danych postgresql. W trakcie tworzenia kontenerów domyślnie uruchomi się komenda scrape_articles która przetworzy domyślne adresy url i zapisze dane do bazy. Zostaną również zainstalowane wszystkie potrzebne biblioteki z pliku requirements.txt

## Tworzenie pliku env
W pobranym archiwum git należy utworzyć plik o nazwie .env który zawiera ustawienia bazy danych postgresql. Zawartość jaką musi mieć to:

    POSTGRES_DB=postgres

    POSTGRES_USER=postgres
    
    POSTGRES_PASSWORD=  < - tutaj ustaw swoje hasło
    
    POSTGRES_HOST=db
    
    POSTGRES_PORT=5432

## Uruchomienie scrapera
   Scraper domyślnie się odpala podczas tworzenia kontenerów. Scrapuje 4 domyślne adresy które są zapisane w pliku scrape_articles.py. Jest również opcja uruchomienia scrapera z argumentem -u który umożliwia scrapowanie listy adresów url podanych w konsoli. Na przykład:
```bash
  docker-compose exec django python manage.py scrape_articles -u https://www.autocentrum.pl/publikacje/porady/kaskadowy-pomiar-predkosci-na-czym-polega/?pvclid=01K7W5ZRS9KTH05ZA2EK2CGN1W
```
Powyższy kod jest uruchamiany wewnątrz kontenera django i tyko wtedy on zadziała. Próba uruchomienia bez wspomnianych kontenerów zakończy się niepowodzeniem.

## Dostepne endpointy API:

- http://localhost:8000/api/articles/   ->  Lista wszystkich artykułów w bazie danych
- http://localhost:8000/api/articles/id  -> Szczegóły danego artykułu gdzie id wybranego artykułu
- http://localhost:8000/api/articles/?source=domain.com   ->  Filtrowanie poprzez nazwę domeny

## Założenia i ograniczenia
- Scraper działa w kontenerze Docker z Selenium Grid.
- Skrypt zakłada obecność elementów h1, article, time, itp. – jeśli brak, pola zostaną puste.
- Niektóre strony mogą blokować dostęp (403 Forbidden) lub wykrywać automaty.
- Domyślne URL-e do scrapowania są skonfigurowane w komendzie scrape_articles.
- Limit prób pobrania artykułu: 3 próby z rosnącym czasem oczekiwania.
- Parser dat obsługuje język angielski („2 days ago”, „yesterday”, „3 hours ago”).

## Struktura katalogów projektu Webscrap
```
webscrap/
├── webscrap/                        # Konfiguracja Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── scrap/                            # Aplikacja Django do scrapowania
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                     # Model Article
│   ├── views.py                      # API endpointy
│   ├── serializers.py                # Serializacja danych
│   ├── urls.py
│   ├── migrations/
│   │   └── __init__.py
│   └── management/
│       └── commands/
│           └── scrape_articles.py    # Komenda scrapera
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
