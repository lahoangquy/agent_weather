import requests
import os

from dotenv import load_dotenv
from flask import session

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()


def get_weather(city: str):
    """Get weather for a given city."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)

    data = response.json()

    temperature_celsius = data['main']['temp']

    return f"Temperature in {city}: {temperature_celsius}°C"


def get_location():
    """Get user's current location."""

    location = session.get("user_location")

    if not location:
        return "Unknown"

    lat = location.get("lat")
    lon = location.get("lon")

    response = requests.get(
        f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json',
        headers={'User-Agent': 'WeatherAssistant/1.0'},
        timeout=5
    )

    data = response.json()

    address = data.get("address", {})

    city = address.get("city") or address.get("town") or "Unknown"

    country = address.get("country", "")

    return f"{city}, {country}"


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
)

system_prompt = """
You are a helpful weather assistant.
"""

agent = create_agent(
    model=llm,
    tools=[get_weather, get_location],
    system_prompt=system_prompt
)
