from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def parse_html_and_find_cookies(html):
    """
    Analizuje HTML strony, szukając elementów związanych z consent management (cookiebot, cookie widget, itp.)
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Automatyczne wyszukiwanie elementów z typowymi atrybutami
    possible_elements = []
    keywords = ["cookie", "consent", "bot", "widget"]

    # Szukanie w <script>, <div>, <iframe> itp.
    for tag in ["script", "div", "iframe", "span", "link"]:
        elements = soup.find_all(tag, attrs=True)
        for el in elements:
            if any(keyword in str(el.attrs).lower() or keyword in str(el.text).lower() for keyword in keywords):
                possible_elements.append(el)

    # Filtrujemy tylko unikalne elementy
    detected_elements = list(set(possible_elements))

    if detected_elements:
        print("[DETEKCJA] Znaleziono elementy związane z consent management:")
        for el in detected_elements:
            print(f"[DETEKCJA] Element: {el}")
    else:
        print("[DETEKCJA] Nie znaleziono żadnych elementów związanych z consent management.")
    print("-" * 50)


def wait_for_page_load(driver, timeout=10):
    """
    Czeka na załadowanie strony poprzez sprawdzenie obecności <html>
    """
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        time.sleep(2)  # Dodatkowy czas na pełne załadowanie dynamicznych elementów
    except Exception as e:
        print(f"[BŁĄD] Strona nie załadowała się poprawnie: {e}")


def check_iframes_for_consent(driver):
    """
    Sprawdza iframe'y w poszukiwaniu elementów związanych z consent management
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for index, iframe in enumerate(iframes):
        try:
            print(f"[INFO] Sprawdzanie iframe {index+1}/{len(iframes)}: {iframe.get_attribute('src')}")
            driver.switch_to.frame(iframe)

            # Sprawdzanie obecności elementów związanych z "cookie"
            iframe_html = driver.page_source
            parse_html_and_find_cookies(iframe_html)

            driver.switch_to.default_content()  # Wraca do głównego DOM
        except Exception as e:
            print(f"[INFO] Problem z iframe: {e}")
            driver.switch_to.default_content()  # Wraca do głównego DOM w razie błędu


def check_consent_mode_for_url(url):
    """
    Otwiera stronę, pobiera HTML, analizuje i wykrywa Consent Mode
    """
    # Ustawienia Selenium
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        print(f"Otwieranie strony: {url}")
        driver.get(url)
        wait_for_page_load(driver)

        # Sprawdź iframe'y
        check_iframes_for_consent(driver)

        # Pobierz aktualny HTML strony
        html = driver.page_source

        # Analizuj HTML i szukaj elementów związanych z "cookie consent"
        parse_html_and_find_cookies(html)

    except Exception as e:
        print(f"[BŁĄD] Wystąpił problem: {e}")

    finally:
        driver.quit()


def main():
    """
    Główna funkcja aplikacji
    """
    while True:
        print("Podaj URL strony do analizy (lub wpisz 'exit' aby zakończyć):")
        url = input("URL: ").strip()
        if url.lower() == "exit":
            print("Zakończono działanie aplikacji.")
            break

        # Uruchom analizę dla podanego URL
        check_consent_mode_for_url(url)


if __name__ == "__main__":
    main()
