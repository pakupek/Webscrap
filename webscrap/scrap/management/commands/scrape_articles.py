from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import pytz, re, time, django, os, sys, structlog
from django.core.management.base import BaseCommand
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = structlog.get_logger()


class Command(BaseCommand):
    help = "Begin scraping process of given urls"

    # Konfiguracja parametrów komendy
    def add_arguments(self, parser):
        parser.add_argument('-u', '--url', nargs='*', type=str, help='Pass multiple urls divided by space for scraping')

    def parse_date(self, date_str: str, timezone="Europe/Warsaw") -> str:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        date_str = (date_str or "").strip().lower()

        # Obsługa pustych lub brakujących dat
        if not date_str:
            return now.strftime("%d.%m.%Y %H:%M:%S")

        # Wzorce (np. "2 days ago", "3 hours ago")
        time_units = {
            "day": "days",
            "hour": "hours",
            "minute": "minutes"
        }

        for unit, kwarg in time_units.items():
            if unit in date_str:
                match = re.search(r"(\d+)\s+" + unit, date_str)
                amount = int(match.group(1)) if match else 1
                dt = now - timedelta(**{kwarg: amount})
                break
        else:
            # Przypadek: "yesterday"
            if "yesterday" in date_str:
                dt = now - timedelta(days=1)
            else:
                try:
                    dt = parser.parse(date_str, fuzzy=True)
                except Exception:
                    dt = now

        # Jeśli brak godziny  00:00:00
        if not re.search(r"\d{1,2}:\d{2}", date_str):
            dt = dt.replace(hour=0, minute=0, second=0)

        # Czy data ma strefe czasową
        if dt.tzinfo is None:
            dt = tz.localize(dt)

        return dt.strftime("%d.%m.%Y %H:%M:%S")

    def handle(self, *args, **kwargs):
        # Konfiguracja z django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webscrap.settings")
        project_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(project_path)
        django.setup()
        from scrap.models import Article
        
        SELENIUM_DOCKER_URL = "http://selenium:4444/wd/hub"
        
        # Opcje Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Lista artykułów do scrapowania
        urls_arg = kwargs.get('url')

        # Rozdzielenie adresów
        if isinstance(urls_arg, str):
            urls = [u.strip() for u in urls_arg.split(",") if u.strip()]
        elif isinstance(urls_arg, list):
            urls = urls_arg
        else:
            # Domyślne adresy
            urls = [
                "https://galicjaexpress.pl/ford-c-max-jaki-silnik-benzynowy-wybrac-aby-zaoszczedzic-na-paliwie",
                "https://galicjaexpress.pl/bmw-e9-30-cs-szczegolowe-informacje-o-osiagach-i-historii-modelu",
                "https://take-group.github.io/example-blog-without-ssr/jak-kroic-piers-z-kurczaka-aby-uniknac-suchych-kawalkow-miesa",
                "https://take-group.github.io/example-blog-without-ssr/co-mozna-zrobic-ze-schabu-oprocz-kotletow-5-zaskakujacych-przepisow",
            ]

        
        driver = webdriver.Remote(
            command_executor=SELENIUM_DOCKER_URL,
            options=options
        )
        COUNT = 1
        MAX_SCRAPE_TRIES = 3
        SLEEP_TIME = 3
        CURRENT_TRY = 0

        # Scrapowanie artykułów 
        for url in urls:
            if not url or not isinstance(url, str) or not url.startswith("http"):
                logger.warning(f"Invalid URL: {url}")
                logger.warning("Skipping")
                continue

            # Jesli artykuł jest w bazie to pomijamy proces scrapowania
            elif Article.objects.filter(url = url).exists():
                logger.warning("Scraping article exists in database\nSkipping...")
                COUNT += 1
                continue

            else:
                while CURRENT_TRY < MAX_SCRAPE_TRIES:
                    try:
                        logger.info(f"Scraping article ({COUNT}/{len(urls)})")
                        COUNT += 1
                        driver.get(url)
                        soup = BeautifulSoup(driver.page_source, "html.parser")


                        # Wyciąganie tytułu 
                        title_tag = soup.find("h1") or soup.find("title")
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                            logger.info("Title was found! ")
                        else: 
                            title = "Not Found"
                            logger.warning("Title was not found! ")
                    

                        # Wyciąganie treści
                        content_html_tag = soup.find("article") or soup.find("div", class_="content") or soup.find("div", class_="post")
                        if content_html_tag:
                            content_html = str(content_html_tag) 
                            content_text = content_html_tag.get_text(separator="\n", strip=True)
                            logger.info("Content of the page was found! ")
                        else:
                            content_text, content_html = ""
                            logger.warning("Content of the page was not found! ")


                        # Wyciąganie daty publikacji 
                        date_tag = soup.find("time") or soup.find("span", class_="date") or soup.find("p", class_="date")
                        if date_tag:
                            date_str = date_tag.get_text(strip=True) 
                            published_at = self.parse_date(date_str) 
                            logger.info("Publication date was found! ")
                        else:
                            date_str = ""
                            published_at = self.parse_date("")
                            logger.warning("Publication date was not found! ")

                        # Zapis do bazy artykułów
                        Article.objects.create(title=title,content_html=content_html,content_text=content_text,url=url,published_at=published_at)
                        time.sleep(2) 
                        break
                    
                    # Wyjątek gdy strona nie zostanie załadowana 
                    except (TimeoutException, WebDriverException) as e:
                        CURRENT_TRY += 1
                        logger.warning(f"Page load failed ({CURRENT_TRY}/{MAX_SCRAPE_TRIES}) for {url}: {e}")
                        time.sleep(SLEEP_TIME)

                    except Exception as e:
                        logger.error("Scraping error", error=str(e), url=url, timestamp=time.time())
                        continue
                    break

        logger.info("Scraping finished!")
        driver.quit()