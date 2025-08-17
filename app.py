# app.py
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in .env file. Please add it before running the app.")

app = Flask(__name__)
CORS(app)

@app.route('/api/geocode', methods=['POST'])
def geocode():
    try:
        data = request.get_json()
        location = data.get("location")
        if not location:
            return jsonify({"error": "No location provided"}), 400

        # This endpoint remains the same
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()

        if not results:
            return jsonify({"error": "Location not found"}), 404

        return jsonify({
            "lat": results[0]["lat"],
            "lng": results[0]["lon"]
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error: " + str(e)}), 500

@app.route('/api/weather', methods=['POST'])
def weather():
    try:
        data = request.get_json()
        lat = data.get("lat")
        lon = data.get("lng")
        if lat is None or lon is None:
            return jsonify({"error": "Latitude or longitude missing"}), 400

        # --- FIX ---
        # Switched from the '/onecall' endpoint to the free '/forecast' endpoint.
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        # This will now correctly report the 401 error if the key is wrong
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Server error: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
