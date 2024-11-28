import requests
import csv
import io
import datetime
import hashlib
import hmac
import base64

# API key
API_KEY = "85768b1960c7aa6ae7a2d7a08168541b"

# OBS Connection and Data Fetching
def fetch_data_from_obs():
    access_key = 'FHVV7UVUMRCHAUCWUX1R'  # Access Key ID
    secret_key = 'suqbDXVYpfqIP3rFKe1tkIfjdzMBLfoqIRDkwBcm'  # Secret Access Key
    bucket_name = 'enes'  # OBS Bucket name
    object_name = 'turkiye_sehirleri_hava_durumu.csv'  # File name
    endpoint = 'https://obs.tr-west-1.myhuaweicloud.com'  # OBS endpoint

    # OBS URL
    url = f"{endpoint}/{bucket_name}/{object_name}"

    # Request time
    now = datetime.datetime.utcnow()
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Signing process (to create Authorization header)
    string_to_sign = f"GET\n\n\n{date_str}\n/{bucket_name}/{object_name}"
    h = hmac.new(secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(h.digest()).decode('utf-8')
    authorization_header = f"AWS {access_key}:{signature}"

    # HTTP GET request
    headers = {
        'Date': date_str,
        'Authorization': authorization_header
    }

    response = requests.get(url, headers=headers)

    # If the request is successful, process the CSV data
    if response.status_code == 200:
        print("Data fetched from OBS!")
        csv_data = response.text

        # Process the data (convert CSV format to Python list)
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.reader(csv_file)
        return list(csv_reader)
    else:
        print(f"Failed to fetch data from OBS. Error: {response.status_code}, {response.text}")
        return None

# Recommendations based on weather conditions
def get_weather_recommendations(temp, humidity, description, wind_speed):
    recommendations = []

    # Temperature recommendations
    if temp >= 30:
        recommendations.append("It's a hot day! Stay in the shade and drink plenty of water.")
        recommendations.append("Wear summer clothes and use sunscreen.")
        recommendations.append("If you are staying outside, don't forget to wear a hat.")
    elif temp >= 20:
        recommendations.append("Nice weather! You can take a walk outside.")
        recommendations.append("Wear light clothes to stay cool.")
    elif temp >= 10:
        recommendations.append("It's a bit cold, but you can still spend time outside.")
        recommendations.append("Wearing a jacket or sweater is a good idea.")
    elif temp < 10:
        recommendations.append("It's cold! Wear thick clothes and be careful.")

    # Humidity recommendations
    if humidity > 80:
        recommendations.append("It's very humid, wear light clothes to avoid sweating.")
    elif humidity < 30:
        recommendations.append("The air is dry, consider using a moisturizer to prevent dry skin.")

    # Precipitation recommendations
    if "rain" in description:
        recommendations.append("It's raining, don't forget to take your umbrella!")
    elif "snow" in description:
        recommendations.append("It's snowing, wear warm clothes and be careful.")

    # Wind recommendations
    if wind_speed > 15:
        recommendations.append("The wind is very strong, take it into consideration before going outside.")
    
    return recommendations

# Ask user if they want to use location or manually enter a city name
choice = input("Would you like to get weather information based on your location or manually enter a city? (l/m): ").strip().lower()

if choice == "m":
    city = input("Which city's weather information would you like to get?: ").strip()
else:
    # Get city information based on user's IP address
    ip_url = "http://ip-api.com/json/"
    ip_response = requests.get(ip_url)
    ip_data = ip_response.json()
    city = ip_data.get("city", "Istanbul")  # Default to Istanbul if city information is not available

# Ask user if they want daily weather, last 5 days, or next 7 days forecast
forecast_choice = input("Would you like the daily weather, last 5 days, or next 7 days forecast? (daily/5/7): ").strip().lower()

if forecast_choice == "daily":
    # API URL
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    # Fetch weather data
    weather_response = requests.get(weather_url)
    if weather_response.status_code == 200:
        weather_data = weather_response.json()

        # Extract weather data
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        weather_description = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']

        # Print output
        print(f"Today's weather in {city}: {weather_description.capitalize()}")
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s\n")

        # Get and print recommendations
        recommendations = get_weather_recommendations(temperature, humidity, weather_description, wind_speed)
        print("Recommendations:")
        for recommendation in recommendations:
            print(f"- {recommendation}")
    else:
        print("An error occurred while fetching weather data. Please try again later.")

elif forecast_choice == "5" or forecast_choice == "7":
    # Fetch data from OBS
    obs_data = fetch_data_from_obs()
    if obs_data:
        header = obs_data[0]
        data = obs_data[1:]
        city_data = [row for row in data if row[0].lower() == city.lower()]

        if city_data:
            print("Weather data fetched from OBS.")
            if forecast_choice == "5":
                print(f"\nLast 5 days weather forecast for {city}:")
                # Ensure we have at least 5 records
                for row in city_data[-5:] if len(city_data) >= 5 else city_data:
                    date, temp, description, humidity, wind_speed = row[1], row[2], row[3], row[4], row[5]
                    print(f"Date: {date}, Temperature: {temp}°C, Weather: {description}, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s")
            elif forecast_choice == "7":
                print(f"\nNext 7 days weather forecast for {city}:")
                # Ensure we have at least 7 records
                for row in city_data[:7] if len(city_data) >= 7 else city_data:
                    date, temp, description, humidity, wind_speed = row[1], row[2], row[3], row[4], row[5]
                    print(f"Date: {date}, Temperature: {temp}°C, Weather: {description}, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s")

            # Check for significant changes throughout the day
            print("\nChecking for significant weather changes during the day:")
            change_detected = False
            for i in range(1, len(city_data)):
                prev_description = city_data[i - 1][3].lower()
                current_description = city_data[i][3].lower()
                if current_description != prev_description:
                    change_detected = True
                    print(f"- On {city_data[i][1]}, weather changed to {current_description}.")
            if not change_detected:
                print("- No significant weather changes detected today.")
        else:
            print(f"No weather forecast data found for {city}.")
