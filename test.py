import requests
import json
import re
import os
from typing import Dict, Any

# Importowanie niezbędnych modułów dla Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ConsentModeChecker:
    def __init__(self):
        self.last_results = None
        self.last_url = None
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_consent_mode_dynamic(self, url: str) -> Dict[str, Any]:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        results = {
            'consent_mode_detected': False,
            'implementation_type': [],
            'gtm_detected': False,
            'gtag_detected': False,
            'issues': [],
            'network_requests': [],
            'consent_given': None,
            'evidence': []
        }
        
        try:
            # Konfiguracja opcji przeglądarki
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            # Włączenie logowania wydajności dla żądań sieciowych
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            
            # Inicjalizacja przeglądarki
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Załaduj stronę
            driver.get(url)
            time.sleep(5)  # Poczekaj na załadowanie strony

            # Funkcja do interakcji z okienkiem zgód
            def handle_consent(consent_action: str):
                try:
                    wait = WebDriverWait(driver, 10)
                    # Jeśli okienko zgód jest w iframe, przełącz się do niego
                    # Przykład:
                    # driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))

                    if consent_action == 'accept':
                        # Zastąp selektor właściwym dla Twojej strony
                        accept_button = wait.until(EC.element_to_be_clickable((By.ID, 'acceptAllButton')))
                        accept_button.click()
                        results['consent_given'] = True
                    elif consent_action == 'reject':
                        # Zastąp selektor właściwym dla Twojej strony
                        reject_button = wait.until(EC.element_to_be_clickable((By.ID, 'rejectAllButton')))
                        reject_button.click()
                        results['consent_given'] = False
                    else:
                        results['issues'].append("Nieprawidłowa akcja zgody.")
                    time.sleep(5)  # Poczekaj na wykonanie skryptów po kliknięciu

                    # Jeśli przełączałeś się do iframe, wróć do głównego kontekstu
                    # driver.switch_to.default_content()
                except (NoSuchElementException, TimeoutException):
                    results['issues'].append(f"Nie znaleziono przycisku zgody dla akcji: {consent_action}")
            
            # Symuluj akceptację wszystkich zgód
            handle_consent('accept')
            
            # Pobierz logi żądań sieciowych
            logs = driver.get_log('performance')
            network_requests_accept = self.parse_network_logs(logs)
            
            # Teraz symuluj odrzucenie wszystkich zgód
            driver.delete_all_cookies()
            driver.refresh()
            time.sleep(5)
            handle_consent('reject')
            logs = driver.get_log('performance')
            network_requests_reject = self.parse_network_logs(logs)
            
            # Analiza żądań sieciowych
            results['network_requests'] = {
                'accept': network_requests_accept,
                'reject': network_requests_reject
            }
            
            # Wykrywanie GTM i gtag.js
            if any('gtm.js' in req for req in network_requests_accept):
                results['gtm_detected'] = True
                results['implementation_type'].append('GTM')
            if any('gtag/js' in req for req in network_requests_accept):
                results['gtag_detected'] = True
                results['implementation_type'].append('GTAG')
            results['implementation_type'] = list(set(results['implementation_type']))
            
            # Sprawdzenie dowodów działania Consent Mode
            consent_mode_evidence = self.check_consent_mode_evidence(network_requests_accept, network_requests_reject)
            results['consent_mode_detected'] = consent_mode_evidence['consent_mode_detected']
            results['evidence'] = consent_mode_evidence['evidence']
            if consent_mode_evidence['issues']:
                results['issues'].extend(consent_mode_evidence['issues'])
            
            # Zamknij przeglądarkę
            driver.quit()
            
        except Exception as e:
            results['issues'].append(f"Błąd podczas analizy dynamicznej: {str(e)}")
            # Upewnij się, że przeglądarka zostanie zamknięta w razie błędu
            try:
                driver.quit()
            except:
                pass
        
        self.last_results = results
        self.last_url = url
        return results

    def parse_network_logs(self, logs):
        network_requests = []
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.requestWillBeSent':
                url = log['params']['request']['url']
                network_requests.append(url)
        return network_requests

    def check_consent_mode_evidence(self, requests_accept, requests_reject):
        from urllib.parse import urlparse, parse_qs

        evidence = []
        issues = []
        consent_mode_detected = False
        
        # Sprawdź żądania do Google Analytics
        ga_requests_accept = [req for req in requests_accept if 'collect' in req and 'google-analytics.com' in req]
        ga_requests_reject = [req for req in requests_reject if 'collect' in req and 'google-analytics.com' in req]
        
        # Sprawdź, czy żądania są wysyłane w obu przypadkach
        if ga_requests_accept:
            evidence.append("Żądania do Google Analytics wysłane po akceptacji zgody.")
        else:
            issues.append("Brak żądań do Google Analytics po akceptacji zgody.")
        
        if ga_requests_reject:
            evidence.append("Żądania do Google Analytics wysłane po odrzuceniu zgody.")
            # Analiza parametrów, aby sprawdzić, czy Consent Mode jest aktywny
            for req in ga_requests_reject:
                parsed_url = urlparse(req)
                query_params = parse_qs(parsed_url.query)
                if 'gcs' in query_params:
                    consent_mode_detected = True
                    evidence.append(f"Parametr 'gcs' Consent Mode znaleziony w żądaniu: {req}")
                else:
                    issues.append(f"Brak parametru 'gcs' w żądaniu GA po odrzuceniu zgody: {req}")
        else:
            issues.append("Brak żądań do Google Analytics po odrzuceniu zgody.")
        
        # Możesz dodać podobne sprawdzenia dla innych usług (np. Google Ads)
        
        return {
            'consent_mode_detected': consent_mode_detected,
            'evidence': evidence,
            'issues': issues
        }

    def print_results(self):
        if not self.last_results:
            print("\nBrak wyników do wyświetlenia. Najpierw wykonaj analizę strony.")
            return

        print(f"\n=== Wyniki analizy Consent Mode dla {self.last_url} ===")
        print(f"Consent Mode wykryty: {'Tak' if self.last_results['consent_mode_detected'] else 'Nie'}")
        
        if self.last_results['implementation_type']:
            print(f"Typ implementacji: {', '.join(self.last_results['implementation_type'])}")
        
        print(f"GTM wykryty: {'Tak' if self.last_results['gtm_detected'] else 'Nie'}")
        print(f"Gtag.js wykryty: {'Tak' if self.last_results['gtag_detected'] else 'Nie'}")
        
        consent_status = 'Akceptacja' if self.last_results['consent_given'] else 'Odrzucenie'
        print(f"\nStatus zgody: {consent_status}")
        
        if self.last_results['evidence']:
            print("\nDowody działania Consent Mode:")
            for ev in self.last_results['evidence']:
                print(f"- {ev}")
        else:
            print("\nNie wykryto konkretnych dowodów działania Consent Mode.")
        
        if self.last_results['issues']:
            print("\nWykryte problemy:")
            for issue in self.last_results['issues']:
                print(f"- {issue}")

    def export_results(self, filename: str):
        if not self.last_results:
            print("\nBrak wyników do eksportu. Najpierw wykonaj analizę strony.")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'url': self.last_url,
                    'results': self.last_results
                }, f, indent=2, ensure_ascii=False)
            print(f"\nWyniki zostały wyeksportowane do pliku: {filename}")
        except Exception as e:
            print(f"\nBłąd podczas eksportu wyników: {str(e)}")

    def display_menu(self):
        while True:
            self.clear_screen()
            print("=== Consent Mode Checker ===")
            print("1. Sprawdź nową stronę")
            print("2. Pokaż ostatnie wyniki")
            print("3. Eksportuj wyniki do pliku")
            print("4. Wyjście")
            
            choice = input("\nWybierz opcję (1-4): ")
            
            if choice == '1':
                url = input("\nPodaj URL strony do sprawdzenia: ")
                self.check_consent_mode_dynamic(url)
                self.print_results()
                input("\nNaciśnij Enter, aby kontynuować...")
            
            elif choice == '2':
                self.clear_screen()
                self.print_results()
                input("\nNaciśnij Enter, aby kontynuować...")
            
            elif choice == '3':
                if self.last_results:
                    filename = input("\nPodaj nazwę pliku do zapisu (np. wyniki.json): ")
                    self.export_results(filename)
                    input("\nNaciśnij Enter, aby kontynuować...")
                else:
                    print("\nBrak wyników do eksportu. Najpierw wykonaj analizę strony.")
                    input("\nNaciśnij Enter, aby kontynuować...")
            
            elif choice == '4':
                print("\nZamykanie...")
                break
            
            else:
                print("\nNieprawidłowy wybór. Spróbuj ponownie.")
                input("\nNaciśnij Enter, aby kontynuować...")

def main():
    checker = ConsentModeChecker()
    checker.display_menu()

if __name__ == "__main__":
    main()
