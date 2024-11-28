import requests
import json
import re
import os
from typing import Dict, Any


class ConsentModeChecker:
    def __init__(self):
        self.last_results = None
        self.last_url = None
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_consent_mode(self, url: str) -> Dict[str, Any]:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        results = {
            'consent_mode_detected': False,
            'implementation_type': [],
            'default_settings': None,
            'gtm_detected': False,
            'gtag_detected': False,
            'consent_api_calls': [],
            'issues': []
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            content = response.text
            
            gtm_patterns = [
                r'googletagmanager\.com/gtm\.js',
                r'www\.googletagmanager\.com/gtm\.js',
                r'<!-- Google Tag Manager -->',
                r'gtm\.start',
                r'dataLayer\.push\({\'gtm\.'
            ]
            
            for pattern in gtm_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results['gtm_detected'] = True
                    results['implementation_type'].append('GTM')
                    break

            gtag_patterns = [
                r'googletagmanager\.com/gtag/js',
                r'gtag\s*\(\s*[\'"]js[\'"]\s*,\s*[\'"]config[\'"]',
                r'window\.dataLayer\s*=\s*window\.dataLayer',
                r'function gtag\(\)'
            ]
            
            for pattern in gtag_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results['gtag_detected'] = True
                    results['implementation_type'].append('GTAG')
                    break

            consent_patterns = [
                r"gtag\s*\(\s*['\"]consent['\"]",
                r"dataLayer\.push\s*\(\s*\[\s*['\"]consent['\"]",
                r"window\.gtag\s*\(\s*['\"]consent['\"]",
                r"'default',\s*{[^}]*'ad_storage':",
                r"'update',\s*{[^}]*'ad_storage':",
                r"gtag\.consent\s*=",
                r"gtagSet\s*\(\s*['\"]consent['\"]",
                r"OneTrust\.InsertHtml",
                r"CookieConsent",
                r"__tcfapi",
                r"consent_mode_v2",
                r"'functionality_storage':",
                r"'security_storage':",
                r"'personalization_storage':",
                r"'analytics_storage':",
            ]

            for pattern in consent_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results['consent_mode_detected'] = True
                    results['consent_api_calls'].append(pattern)

            default_settings_patterns = [
                r"gtag\s*\(\s*['\"]consent['\"]\s*,\s*['\"]default['\"]\s*,\s*({[^}]+})",
                r"dataLayer\.push\s*\(\s*\[\s*['\"]consent['\"]\s*,\s*['\"]default['\"]\s*,\s*({[^}]+})\s*\]",
                r"'default',\s*({[^}]*'ad_storage':[^}]+})",
            ]

            for pattern in default_settings_patterns:
                match = re.search(pattern, content)
                if match:
                    try:
                        settings_str = match.group(1).replace("'", '"')
                        settings_str = re.sub(r'//.*?\n|/\*.*?\*/', '', settings_str)
                        default_settings = json.loads(settings_str)
                        results['default_settings'] = default_settings
                        break
                    except json.JSONDecodeError:
                        continue

            if not results['consent_mode_detected']:
                results['issues'].append("Nie wykryto konfiguracji Consent Mode")
            if not (results['gtm_detected'] or results['gtag_detected']):
                results['issues'].append("Nie wykryto GTM ani gtag.js")
            if results['default_settings']:
                required_settings = ['ad_storage', 'analytics_storage']
                missing_settings = [setting for setting in required_settings 
                                  if setting not in results['default_settings']]
                if missing_settings:
                    results['issues'].append(
                        f"Brak wymaganych ustawień: {', '.join(missing_settings)}"
                    )

            results['implementation_type'] = list(set(results['implementation_type']))
                
        except requests.RequestException as e:
            results['issues'].append(f"Błąd podczas pobierania strony: {str(e)}")
            
        self.last_results = results
        self.last_url = url
        return results

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
        
        if self.last_results['consent_api_calls']:
            print("\nWykryte wywołania API consent:")
            for call in self.last_results['consent_api_calls']:
                print(f"- {call}")
        
        if self.last_results['default_settings']:
            print("\nDomyślne ustawienia consent:")
            for key, value in self.last_results['default_settings'].items():
                print(f"  {key}: {value}")
        
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
                self.check_consent_mode(url)
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