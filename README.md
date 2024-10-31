# Consent Mode Checker

**Narzędzie w Pythonie** do analizy i weryfikacji implementacji Google Consent Mode na stronach internetowych. To narzędzie pomaga wykryć różne warianty implementacji Consent Mode, GTM oraz konfiguracji gtag.js.

## 🚀 Funkcjonalności

* Wykrywanie implementacji *Google Tag Manager* (GTM)
* Wykrywanie implementacji *Global Site Tag* (gtag.js)
* Analiza konfiguracji Consent Mode i ustawień
* Identyfikacja potencjalnych problemów z implementacją
* Obsługa domyślnych i niestandardowych konfiguracji zgód
* Eksport wyników do formatu JSON
* Przyjazny interfejs wiersza poleceń

## 💻 Wymagania

```plaintext
python >= 3.6
requests
```

## 🔧 Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/twojanazwa/consent-mode-checker.git
cd consent-mode-checker
```

2. Zainstaluj wymagane pakiety:
```bash
pip install requests
```

## 📖 Użytkowanie

Uruchom skrypt za pomocą Pythona:

```bash
python consent_mode_checker.py
```

### Menu główne:

1️⃣ Sprawdź nową stronę  
2️⃣ Pokaż ostatnie wyniki  
3️⃣ Eksportuj wyniki do pliku  
4️⃣ Wyjście  

___

### ✅ Sprawdzanie Strony

1. Wybierz opcję 1 z głównego menu
2. Wprowadź URL strony (z lub bez http/https)
3. Przeanalizuj otrzymane wyniki

### 📊 Wyniki Analizy Zawierają:

* Status wykrycia Consent Mode
* Typ implementacji (GTM/gtag.js)
* Wykryte wywołania API consent
* Domyślne ustawienia zgód
* Potencjalne problemy z implementacją

### 💾 Eksport Wyników

Wyniki można wyeksportować do pliku JSON:

1. Wybierz opcję 3 z głównego menu
2. Podaj nazwę pliku (np. `wyniki.json`)
3. Narzędzie zapisze wyniki w formacie JSON

## 📋 Przykładowy Output

```json
{
  "url": "przyklad.pl",
  "results": {
    "consent_mode_detected": true,
    "implementation_type": ["GTM"],
    "default_settings": {
      "ad_storage": "denied",
      "analytics_storage": "denied"
    },
    "gtm_detected": true,
    "gtag_detected": false,
    "consent_api_calls": [
      "gtag('consent', 'default'",
      "dataLayer.push(['consent'"
    ],
    "issues": []
  }
}
```

## 🔍 Wzorce Detekcji

Narzędzie sprawdza różne wzorce implementacji:

* Standardowe implementacje GTM
* Implementacje gtag.js
* Wywołania API Consent Mode
* Integracje CMP
* Konfiguracje Consent Mode v2