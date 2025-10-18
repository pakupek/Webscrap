## Instalacja zależności

1. Skopiuj repozytorium:

```bash
git clone https://github.com/pakupek/Webscrap
```

2. Utwórz kontenery za pomocą podanej komendy. Dla Windows potrzebny będzie terminal WSL
 ```bash
docker compose up --build
```
W tym momencie kontenery zostaną utworzone dla django jak i bazy danych postgresql. W trakcie tworzenia kontenerów domyślnie uruchomi się komenda scrape_articles która przetworzy domyślne adresy url i zapisze dane do bazy. Zostaną również zainstalowane wszystkie potrzebne biblioteki z pliku requirements.txt

3. Uruchomienie scrapera
   Scraper domyślnie się odpala podczas tworzenia kontenerów. Scrapuje 4 domyślne adresy które są zapisane w pliku scrape_articles.py. Jest również opcja uruchomienia scrapera z argumentem -u który umożliwia scrapowanie listy adresów url podanych w konsoli. Na przykład:
```bash
  docker-compose exec django python manage.py scrape_articles -u https://www.autocentrum.pl/publikacje/porady/kaskadowy-pomiar-predkosci-na-czym-polega/?pvclid=01K7W5ZRS9KTH05ZA2EK2CGN1W
```
Powyższy kod jest uruchamiany wewnątrz kontenera django i tyko wtedy on zadziała. Próba uruchomienia bez wspomnianych kontenerów zakończy się niepowodzeniem.

4. Dostepne endpointy API:
Lista wszystkich artykułów w bazie danych
- http://localhost:8000/api/articles/
Szczegóły danego artykułu gdzie <id> id wybranego artykułu
- http://localhost:8000/api/articles/<id>
Filtrowanie poprzez nazwę domeny
- http://localhost:8000/api/articles/?source=domain.com

5. Założenia i ograniczenia
- Scraper działa w kontenerze Docker z Selenium Grid.
- Skrypt zakłada obecność elementów <h1>, <article>, <time>, itp. – jeśli brak, pola zostaną puste.
- Niektóre strony mogą blokować dostęp (403 Forbidden) lub wykrywać automaty.
- Domyślne URL-e do scrapowania są skonfigurowane w komendzie scrape_articles.
- Limit prób pobrania artykułu: 3 próby z rosnącym czasem oczekiwania.
- Parser dat obsługuje język angielski („2 days ago”, „yesterday”, „3 hours ago”).

6. Struktura projektu
webscrap/
├── webscrap/                  # Konfiguracja Django
├── scraper/
│   ├── management/commands/
│   │   └── scrape_articles.py # Komenda scrapera
│   ├── models.py              # Model Article
│   ├── views.py               # API endpointy
│   └── serializers.py         # Serializacja danych
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
