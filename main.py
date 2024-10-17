import requests
from bs4 import BeautifulSoup

def main():
    url = input("Podaj URL strony do monitorowania: ")
    if not url.startswith('http'):
        url = 'http://' + url

    try:
        response = requests.get(url)
        status_code = response.status_code
        headers = response.headers
        cookies = response.cookies

        # Sprawdzenie kodu statusu HTTP
        print(f"Kod statusu: {status_code}")
        if status_code == 200:
            print("HTTP Status Code to 200 OK")
        elif status_code == 400:
            print("HTTP Status Code to 400 Bad Request")
        elif status_code == 500:
            print("HTTP Status Code to 500 Internal Server Error")
        else:
            print(f"HTTP Status Code to {status_code}")

        # Wyświetlenie nagłówków
        print("Nagłówki:")
        for header, value in headers.items():
            print(f"{header}: {value}")

        # Parsowanie ciastek
        print("Ciasteczka:")
        if cookies:
            for cookie in cookies:
                print(f"{cookie.name}: {cookie.value}")
        else:
            print("Nie znaleziono ciasteczek.")

        # Sprawdzenie statusu consentu poprzez analizę ciastek
        consent_status = None
        for cookie in cookies:
            if 'consent' in cookie.name.lower():
                consent_status = cookie.value
                break

        if consent_status:
            print(f"Status consentu: {consent_status}")
        else:
            print("Status consentu nie został znaleziony.")

        # Sprawdzenie działania tagów poprzez analizę kodu HTML
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')

        # Szukanie obecności kodu Google Tag Manager
        if 'googletagmanager.com' in content.decode('utf-8'):
            print("Tagi działają poprawnie.")
            tags_working = True
        else:
            print("Tagi nie działają.")
            tags_working = False

        # Zapis wyników do pliku .txt
        with open('wyniki.txt', 'w', encoding='utf-8') as f:
            f.write(f"Kod statusu: {status_code}\n")
            if status_code == 200:
                f.write("HTTP Status Code to 200 OK\n")
            elif status_code == 400:
                f.write("HTTP Status Code to 400 Bad Request\n")
            elif status_code == 500:
                f.write("HTTP Status Code to 500 Internal Server Error\n")
            else:
                f.write(f"HTTP Status Code to {status_code}\n")

            f.write("Nagłówki:\n")
            for header, value in headers.items():
                f.write(f"{header}: {value}\n")

            f.write("Ciasteczka:\n")
            if cookies:
                for cookie in cookies:
                    f.write(f"{cookie.name}: {cookie.value}\n")
            else:
                f.write("Nie znaleziono ciasteczek.\n")

            if tags_working:
                f.write("Tagi działają poprawnie.\n")
            else:
                f.write("Tagi nie działają.\n")

            if consent_status:
                f.write(f"Status consentu: {consent_status}\n")
            else:
                f.write("Status consentu nie został znaleziony.\n")

    except requests.RequestException as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == '__main__':
    main()
