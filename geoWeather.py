import os
import requests
import logging
from telegram import Location
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

def get_forecast_data(location: Location) -> dict:
    """
    Fetch the weather forecast data for a specific location object.

    Args:
        location: A location object with latitude and longitude attributes.

    Returns:
        A dictionary containing the weather forecast data.
    """
    try:
        if not OPENWEATHERMAP_API_KEY:
            logging.error("OPENWEATHERMAP_API_KEY not found. Please set it in your .env file.")
            raise ValueError("OPENWEATHERMAP_API_KEY not found. Please set it in your .env file.")

        lat, lon = location.latitude, location.longitude
        # Get the hourly forecast using the One Call API
        forecast_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHERMAP_API_KEY}"
        forecast_response = requests.get(forecast_url,timeout=5)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        raise ConnectionError(f"Error fetching weather data: {e}")
    except AttributeError as e:
        logging.error(f"Invalid location object: {e}")
        raise TypeError("Invalid location object provided. Please share a valid location.")
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"Unexpected error in get_forecast_data: {e}")
        raise RuntimeError("An unexpected error occurred while fetching weather data.")

    return forecast_data

def get_forecast_text(location: Location) -> str:
    """
    Get the 24-hour weather forecast for a specific location object.

    Args:
        location: A location object with latitude and longitude attributes.

    Returns:
        A string containing the 24-hour forecast, with warnings highlighted.
    """
    try:
        forecast_data = get_forecast_data(location)
        # Format the forecast for the next 24 hours
        forecast_text = f"48-Hour Forecast for location provided:\n\n"
        warnings = []
        # Add alerts from the API to the warnings
        if 'alerts' in forecast_data:
            for alert in forecast_data['alerts']:
                warnings.append(f"** ALERT from {alert['sender_name']}: {alert['event']} **\n{alert['description']}")
        forecast_text += f"The current temperature is {forecast_data['current']['temp']}°C, feels like {forecast_data['current']['feels_like']}°C with {forecast_data['current']['weather'][0]['description'].capitalize()}.\n\n"
        forecast_text += "Time: Temperature, Weather Description\n"
        for i in range(min(48, len(forecast_data['hourly']))):
            hour_data = forecast_data['hourly'][i]
            temp = hour_data['temp']
            weather_desc = hour_data['weather'][0]['description']
            time_obj = datetime.fromtimestamp(hour_data['dt'])
            time_str = time_obj.strftime('%I:%M %p') # e.g., 03:00 PM
            
            if time_obj.hour == 0:  # Check if it's the last hour of the day
                forecast_text += f"{time_obj.date()} \n"
            forecast_text += f"{time_str}: {temp}°C, {weather_desc.capitalize()}\n"

            # Check for potential warnings
            if "storm" in weather_desc.lower() or "thunder" in weather_desc.lower():
                warnings.append(f"** WARNING: Potential storm around {time_str}! **")
            if temp > 35:
                warnings.append(f"** WARNING: Extreme heat (>35°C) around {time_str}! **")
            if temp < 0:
                warnings.append(f"** WARNING: Freezing temperatures (<0°C) around {time_str}! **")

        if warnings:
            # Using a set to get unique warnings
            unique_warnings = sorted(list(set(warnings)))
            forecast_text = "\n".join(unique_warnings) + "\n\n" + forecast_text

        return forecast_text

    except ConnectionError as e:
        return f"weather service is currently unavailable. Please try again later."
    except TypeError as e:
        return "Invalid location object provided. Please share a valid location."
    except RuntimeError as e:
        return "An unexpected error occurred while fetching weather data."
    except Exception as e:
        logging.error(f"Unexpected error in get_forecast_text: {e}")
        return "An unexpected error occurred while formatting the weather forecast."

if __name__ == '__main__':
    # Example usage:
    class MockLocation:
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude
    
    # You need to have a .env file with your OPENWEATHERMAP_API_KEY
    # OPENWEATHERMAP_API_KEY="your_api_key"
    print("Fetching forecast for London...")
    print(get_forecast_text(MockLocation(51.5074,  -0.144)))