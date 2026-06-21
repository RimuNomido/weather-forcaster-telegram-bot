from geopy import Nominatim
import requests

def get_coords(city, ) -> tuple[float, float] | None:
    geolocator = Nominatim(user_agent='rimunomido')
    loc = geolocator.geocode(city)

    if loc is None:
        print('Город не найден. Пользователь ввёл неверное название.')
        return None

    lat = loc.latitude
    lon = loc.longitude

    return (lat, lon)

    # Возвращает словарь из нескольких подсловарей.
def send_request(url, access_key, coords: tuple[float, float]) -> dict | None:
    headers = {'X-Yandex-Weather-Key': access_key}
    query = """
    query GetWeather($lat: Float!, $lon: Float!) {
        weatherByPoint(request: { lat: $lat, lon: $lon }) {
            now {
            cloudiness
            humidity
            precType
            precStrength
            pressure
            temperature
            fahrenheit: temperature(unit: FAHRENHEIT)
            windSpeed
            windDirection
            }
        }
    }
    """
    variables = {
        "lat": coords[0],
        "lon": coords[1]
    }

    try:
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables}, timeout=5)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Ошибка сети: {e}')
        return None
    except ValueError as e:
        print(f'Ошибка парсинга JSON: {e}')
        return None