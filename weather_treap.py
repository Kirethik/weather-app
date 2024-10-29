import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import json
from dotenv import load_dotenv
from liveflight import getFlightDetails
from iata import getIataCode, airports

# Load environment variables from .env file
load_dotenv()
apiKey = os.getenv('weather_api')

# Main class for the Weather Application
class WeatherApp:
    def __init__(self, root):
        # Initialize the root Tkinter window with settings
        # Time Complexity: O(1)
        # Explanation: Initializes widgets without loops or data structure manipulation, so it takes constant time.
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("600x600")
        self.root.configure(bg="#f0f0f0")  # Set background color

        # Load locations from JSON file
        self.locations = self.loadLocations()

        # Create widgets
        self.createWidgets()

    def loadLocations(self):
        # Load existing locations from a JSON file if available
        # Time Complexity: O(N), where N is the number of locations
        # Explanation: Reads a file and iterates through each location to format and load into a list.
        try:
            if os.path.exists("locations.json"):
                with open("locations.json", "r") as jsonFile:
                    content = jsonFile.read()
                    if content.strip():  # Check if the file is not empty
                        data = json.loads(content)
                        return [f"{loc['arrival']} -> {loc['destination']}" for loc in data.get("locations", [])]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load locations: {e}")
        return []  # Return an empty list if file doesn't exist or is empty

    def createWidgets(self):
        # Create and arrange the Tkinter widgets
        # Time Complexity: O(1)
        # Explanation: This method only initializes widgets without any loops or complex operations.
        self.locationLabel = tk.Label(self.root, text="Select location to get weather:", bg="#f0f0f0")
        self.locationLabel.pack(pady=(20, 10))

        self.comboBox = ttk.Combobox(self.root, values=self.locations, state='readonly')
        self.comboBox.pack(pady=(0, 20))

        self.getWeatherButton = tk.Button(self.root, text="Get Weather", command=self.getWeather, bg="#4CAF50", fg="white")
        self.getWeatherButton.pack(pady=(0, 10))

        self.getFlightsButton = tk.Button(self.root, text="Get Flights", command=self.getFlights, bg="#2196F3", fg="white")
        self.getFlightsButton.pack(pady=(0, 20))

        self.weatherFrame = tk.Frame(self.root, bg="#f0f0f0")
        self.weatherFrame.pack(fill=tk.BOTH, expand=True)

        self.weatherCanvas = tk.Canvas(self.weatherFrame, bg="#f0f0f0")
        self.weatherCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.weatherScrollbar = ttk.Scrollbar(self.weatherFrame, orient=tk.VERTICAL, command=self.weatherCanvas.yview)
        self.weatherScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.weatherCanvas.configure(yscrollcommand=self.weatherScrollbar.set)
        self.weatherCanvas.bind('<Configure>', lambda e: self.weatherCanvas.configure(scrollregion=self.weatherCanvas.bbox("all")))

        self.weatherFrameInner = tk.Frame(self.weatherCanvas, bg="#f0f0f0")
        self.weatherCanvas.create_window((0, 0), window=self.weatherFrameInner, anchor="nw")

    def showLoadingMessage(self):
        # Display a loading message in the frame
        # Time Complexity: O(1)
        # Explanation: Adds a single label to the GUI, requiring constant time.
        self.loadingLabel = tk.Label(self.weatherFrameInner, text="Loading...", justify="center", anchor="center", bg="#f0f0f0")
        self.loadingLabel.pack(pady=10)

    def removeLoadingMessage(self):
        # Remove the loading message from the frame if it exists
        # Time Complexity: O(1)
        # Explanation: Checks and removes a label if it exists, taking constant time.
        if hasattr(self, 'loadingLabel'):
            self.loadingLabel.destroy()

    def fetchAndDisplayWeather(self, locationName):
        # Fetch and display weather information for the specified location
        # Time Complexity: O(1) for showing loading message, O(1) for API call initiation, O(M) for displaying results,
        # where M is the number of elements in weatherData. Network time depends on response delay.
        self.showLoadingMessage()  # Show loading message
        apiEndpoint = 'http://api.openweathermap.org/data/2.5/weather'
        url = f"{apiEndpoint}?appid={apiKey}&q={locationName}&units=metric"

        try:
            # Make API request for weather data
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            weatherData = response.json()

            # Extract weather information
            temperature = weatherData['main']['temp']
            humidity = weatherData['main']['humidity']
            description = weatherData['weather'][0]['description']

            # Display weather info in the GUI
            weatherInfo = f"Weather in {locationName}:\n" \
                          f"Temperature: {temperature:.2f}°C\n" \
                          f"Humidity: {humidity}%\n" \
                          f"Description: {description}"

            weatherLabel = tk.Label(self.weatherFrameInner, text=weatherInfo, justify="center", anchor="center", bg="#f0f0f0")
            weatherLabel.pack(pady=10)

            # Update the canvas with the new weather information
            self.weatherFrameInner.update_idletasks()  # Update the layout
            self.weatherCanvas.config(scrollregion=self.weatherCanvas.bbox("all"))

        except Exception as e:
            self.displayErrorMessage(f"Could not fetch weather for {locationName}: {e}")
        finally:
            self.removeLoadingMessage()  # Remove loading message

    def displayErrorMessage(self, message):
        # Display an error message in the frame
        # Time Complexity: O(1)
        # Explanation: Adds a single label to display an error message.
        errorLabel = tk.Label(self.weatherFrameInner, text=message, justify="center", anchor="center", bg="#f0f0f0")
        errorLabel.pack(pady=10)

    def getWeather(self):
        # Retrieve and display weather information for selected locations
        # Time Complexity: O(M) for widget clearing, where M is the number of child widgets,
        # plus the complexity of fetchAndDisplayWeather for each location.
        selectedLocation = self.comboBox.get()
        if selectedLocation:
            # Split the selected location into departure and arrival
            locations = selectedLocation.split(" -> ")
            departureLocation = locations[0]
            arrivalLocation = locations[1] if len(locations) > 1 else None

            # Clear previous weather information
            for widget in self.weatherFrameInner.winfo_children():
                widget.destroy()

            # Get weather for departure location
            self.fetchAndDisplayWeather(departureLocation)

            # Get weather for arrival location if it exists
            if arrivalLocation:
                self.fetchAndDisplayWeather(arrivalLocation)

    def getFlights(self):
        # Retrieve flight details based on selected departure and arrival locations
        # Time Complexity: O(1) for selection and verification, plus O(F) for IATA code lookup, where F is the complexity of getIataCode.
        # The call to getFlightDetails depends on how it processes IATA codes.
        selectedLocation = self.comboBox.get()
        if selectedLocation:
            # Split the selected location into arrival and destination
            locations = selectedLocation.split(" -> ")
            arrivalCity = locations[1].strip() if len(locations) > 1 else None
            departureCity = locations[0].strip()

            # Get IATA codes for both cities
            departureIata = getIataCode(departureCity, airports)
            arrivalIata = getIataCode(arrivalCity, airports) if arrivalCity else None

            # Check if IATA codes were found
            if departureIata == "No matching airports found.":
                messagebox.showwarning("Warning", f"Departure city '{departureCity}' not found.")
                return
            if arrivalIata == "No matching airports found.":
                messagebox.showwarning("Warning", f"Arrival city '{arrivalCity}' not found.")
                return

            # Call the flight details function with the IATA codes
            self.weatherFrameInner = tk.Frame(self.weatherFrame, bg="#f0f0f0")  # Ensure the result frame is initialized
            self.weatherFrameInner.pack(pady=10)  # Add padding for better spacing
            getFlightDetails(departureIata, arrivalIata, self.weatherFrameInner)
        else:
            messagebox.showwarning("Warning", "Please select a valid arrival and destination.")

# Ensure the script runs only if it is the main program
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
