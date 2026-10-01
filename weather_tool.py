from langchain.tools import tool
import requests


@tool
def get_weather(city: str, days: int = 3) -> str:
    """
    Get weather forecast for a city.
    """

    # -----------------------------------------
    # Step 1: Find latitude and longitude
    # -----------------------------------------
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(
        geocoding_url,
        params=geocoding_params,
        timeout=10
    )

    geo_response.raise_for_status()

    geo_data = geo_response.json()

    if "results" not in geo_data or not geo_data["results"]:
        return f"Could not find the city: {city}"

    latitude = geo_data["results"][0]["latitude"]
    longitude = geo_data["results"][0]["longitude"]

    # -----------------------------------------
    # Step 2: Get weather forecast
    # -----------------------------------------
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_probability_max",
            "weather_code"
        ],
        "forecast_days": days,
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=10
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    daily = weather_data["daily"]

    # -----------------------------------------
    # Step 3: Convert weather code to text
    # -----------------------------------------
    def weather_description(code):

        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        return descriptions.get(
            code,
            "Unknown weather"
        )

    # -----------------------------------------
    # Step 4: Build final weather report
    # -----------------------------------------
    results = []

    for i in range(len(daily["time"])):

        date = daily["time"][i]

        minimum_temperature = daily[
            "temperature_2m_min"
        ][i]

        maximum_temperature = daily[
            "temperature_2m_max"
        ][i]

        rain_probability = daily[
            "precipitation_probability_max"
        ][i]

        weather_code = daily[
            "weather_code"
        ][i]

        description = weather_description(
            weather_code
        )

        result = (
            f"Date: {date}\n"
            f"Minimum temperature: "
            f"{minimum_temperature}°C\n"
            f"Maximum temperature: "
            f"{maximum_temperature}°C\n"
            f"Rain probability: "
            f"{rain_probability}%\n"
            f"Weather: {description}"
        )

        results.append(result)

    return "\n\n".join(results)