from requests_html import HTMLSession

def main():
    url = input("Podaj URL strony do monitorowania: ")
    if not url.startswith('http'):
        url = 'http://' + url

    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render(timeout=20)  # renderuje stronę, wykonując JavaScript

        status_code = response.status_code
        headers = response.headers
        cookies = session.cookies.get_dict()

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
            for name, value in cookies.items():
                print(f"{name}: {value}")
        else:
            print("Nie znaleziono ciasteczek.")

        # Sprawdzenie statusu consentu poprzez analizę dataLayer
        data_layer = response.html.find('script', containing='dataLayer')
        consent_status = None
        for script in data_layer:
            if 'dataLayer' in script.text:
                consent_status = script.text
                break

        if consent_status:
            print("Status consentu znaleziony w dataLayer.")
        else:
            print("Status consentu nie został znaleziony w dataLayer.")

        # Sprawdzenie działania tagów poprzez analizę kodu HTML
        if 'googletagmanager.com' in response.html.html:
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
                for name, value in cookies.items():
                    f.write(f"{name}: {value}\n")
            else:
                f.write("Nie znaleziono ciasteczek.\n")

            if consent_status:
                f.write("Status consentu znaleziony w dataLayer.\n")
            else:
                f.write("Status consentu nie został znaleziony w dataLayer.\n")

            if tags_working:
                f.write("Tagi działają poprawnie.\n")
            else:
                f.write("Tagi nie działają.\n")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == '__main__':
    main()
