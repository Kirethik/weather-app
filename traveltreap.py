from tkinter import *
from tkinter import ttk
import random
import subprocess
import json
import os

# Define the node structure for the Treap data structure
class TreapNode:
    def __init__(self, location):
        # Initialize node with location and random priority for treap balancing
        self.location = location
        self.priority = random.randint(1, 100)
        self.left = None
        self.right = None

# Define the Treap structure for efficient searching and balancing
class Treap:
    def __init__(self):
        self.root = None

    # Right rotation for balancing the treap
    def rotateRight(self, root):
        # Time Complexity: O(1)
        # Explanation: This operation involves a constant number of pointer changes, independent of the Treap size.
        leftChild = root.left
        root.left = leftChild.right
        leftChild.right = root
        return leftChild

    # Left rotation for balancing the treap
    def rotateLeft(self, root):
        # Time Complexity: O(1)
        # Explanation: This operation also involves constant pointer changes, independent of Treap size.
        rightChild = root.right
        root.right = rightChild.left
        rightChild.left = root
        return rightChild

    # Insert a location in the treap with priority-based balancing
    def insert(self, root, location):
        # Time Complexity: Average O(log N), Worst-case O(N)
        # Explanation: On average, the insertion follows a path down the tree, like a binary search tree.
        # Balancing might require rotations, but on average, these operations remain logarithmic.
        if root is None:
            return TreapNode(location)

        if location < root.location:
            root.left = self.insert(root.left, location)
            if root.left.priority > root.priority:
                root = self.rotateRight(root)
        else:
            root.right = self.insert(root.right, location)
            if root.right.priority > root.priority:
                root = self.rotateLeft(root)

        return root

    # Helper to insert a new node in the treap
    def insertNode(self, location):
        # Time Complexity: Average O(log N), Worst-case O(N)
        # Explanation: Same as insert function since it just calls insert at the root.
        self.root = self.insert(self.root, location)

    # Search for nodes with locations matching the prefix in the treap
    def search(self, root, prefix):
        # Time Complexity: O(log N + M), where M is the number of matches found.
        # Explanation: The search follows a path down the tree based on prefix, so it takes O(log N)
        # time on average. Collecting results depends on the number of matches, represented by M.
        if root is None:
            return []

        results = []
        # Check if current location matches the prefix
        if root.location.startswith(prefix):
            results.append(root.location)

        if prefix < root.location:
            results += self.search(root.left, prefix)
        else:
            results += self.search(root.right, prefix)

        return results

    # External method to initiate prefix search in the treap
    def searchPrefix(self, prefix):
        # Time Complexity: O(log N + M)
        # Explanation: This initiates the search from the root, so it shares the time complexity of the search function.
        return self.search(self.root, prefix)

# Define TrieNode structure for autocomplete functionality
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

# Define Trie structure for efficient prefix-based search
class Trie:
    def __init__(self):
        self.root = TrieNode()

    # Insert a word into the Trie structure
    def insert(self, word):
        # Time Complexity: O(L), where L is the length of the word.
        # Explanation: Each character of the word is inserted individually, so the insertion depends linearly on the word length.
        current = self.root
        word = word.lower()
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True

    # Search for all words with the specified prefix
    def search(self, prefix):
        # Time Complexity: O(L + M), where L is the prefix length and M is the number of matched words.
        # Explanation: Searching the prefix takes O(L) time, and collecting results depends on the number of words found.
        current = self.root
        prefix = prefix.lower()
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]
        return self.findWords(current, prefix)

    # Recursively find all words in the Trie starting from a given node
    def findWords(self, node, prefix):
        # Time Complexity: O(M), where M is the number of words found.
        # Explanation: Each word found in this recursive call is appended to the list, so time depends on word count.
        words = []
        if node.is_end_of_word:
            words.append(prefix)

        for char, child in node.children.items():
            words += self.findWords(child, prefix + char)

        return words

# Main class to manage locations and integrate treap and trie
class LocationGraph:
    def __init__(self):
        self.locations = []
        self.treap = Treap()
        self.trie = Trie()

    # Add new locations to both treap and trie
    def addLocations(self, newLocations):
        # Time Complexity: O(L + log N)
        # Explanation: Adding a location to the Trie takes O(L), and inserting it in the Treap takes O(log N) on average.
        combinedLocation = f"{newLocations[0]} -> {newLocations[1]}"
        self.treap.insertNode(combinedLocation)
        self.trie.insert(combinedLocation)
        self.locations.append(combinedLocation)

    # Search for locations using the treap's prefix search
    def searchLocations(self, prefix):
        # Time Complexity: O(log N + M)
        # Explanation: This calls the Treap’s searchPrefix function, which has the same time complexity.
        return self.treap.searchPrefix(prefix)

    # Autocomplete location using trie structure
    def autocomplete(self, prefix):
        # Time Complexity: O(L + M)
        # Explanation: This calls the Trie’s search function, which has the same time complexity.
        return self.trie.search(prefix)

# Main application class for the GUI
class App:
    def __init__(self, root):
        # Configure the main window
        self.window = root
        self.window.title("Location Search")
        self.window.geometry("600x600")
        self.window.configure(bg="#f0f0f0")

        # Initialize the location graph object
        self.location_graph = LocationGraph()

        # Label and input for arrival location
        self.label_arrival = Label(self.window, text="Enter arrival location:", bg="#f0f0f0")
        self.label_arrival.pack(pady=(20, 5))
        self.arrival_entry = Entry(self.window, width=50)
        self.arrival_entry.pack(pady=(0, 10))

        # Label and input for destination location
        self.label_destination = Label(self.window, text="Enter destination location:", bg="#f0f0f0")
        self.label_destination.pack(pady=(10, 5))
        self.destination_entry = Entry(self.window, width=50)
        self.destination_entry.pack(pady=(0, 20))

        # Submit button to add locations
        self.submit_button = Button(self.window, text="Submit Locations", command=self.submitLocations, bg="#4CAF50", fg="white")
        self.submit_button.pack(pady=(10, 20))

        # Label and input for location search
        self.label_search = Label(self.window, text="Search locations:", bg="#f0f0f0")
        self.label_search.pack(pady=(10, 5))
        self.search_entry = Entry(self.window, width=50)
        self.search_entry.pack(pady=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.onSearch)

        # Listbox to display autocomplete suggestions
        self.autocomplete_listbox = Listbox(self.window, width=50)
        self.autocomplete_listbox.pack()

        # Label to display search results
        self.result_label = Label(self.window, text="", bg="#f0f0f0")
        self.result_label.pack(pady=(10, 10))

        # Button to open external weather application
        self.weather_button = Button(self.window, text="Get Weather Info", command=self.openWeatherApp, bg="#2196F3", fg="white")
        self.weather_button.pack(pady=(20, 10))

        # Clear JSON data on window close
        self.window.protocol("WM_DELETE_WINDOW", self.clearJson)

    # Clear JSON data on application close
    def clearJson(self):
        # Time Complexity: O(1)
        # Explanation: It opens and clears a file without looping, making it constant time.
        if os.path.exists("locations.json"):
            open("locations.json", "w").close()
        self.window.destroy()

    # Add locations to graph and JSON file, then reset inputs
    def submitLocations(self):
        # Time Complexity: O(L + log N)
        # Explanation: Adding to the Trie takes O(L) time, and inserting in the Treap takes O(log N) time.
        arrivalLocation = self.arrival_entry.get().strip()
        destinationLocation = self.destination_entry.get().strip()

        if arrivalLocation and destinationLocation:
            newLocations = [arrivalLocation, destinationLocation]
            self.location_graph.addLocations(newLocations)

            # Handle JSON file
            data = {"locations": []}
            if os.path.exists("locations.json"):
                with open("locations.json", "r") as json_file:
                    try:
                        content = json_file.read()
                        if content.strip():
                            data = json.loads(content)
                    except json.JSONDecodeError:
                        print("Error decoding JSON. Initializing with new data.")

            data["locations"].append({"arrival": arrivalLocation, "destination": destinationLocation})

            with open("locations.json", "w") as json_file:
                json.dump(data, json_file)

            # Reset entry fields
            self.arrival_entry.delete(0, END)
            self.destination_entry.delete(0, END)

            # Display confirmation message
            self.result_label.configure(text=f"Locations added: {newLocations}")

    # Handle prefix-based autocomplete suggestions as user types
    def onSearch(self, event):
        # Time Complexity: O(L + M)
        # Explanation: Calls the Trie’s search function for autocomplete suggestions.
        prefix = self.search_entry.get()
        suggestions = self.location_graph.autocomplete(prefix)

        # Update listbox with suggestions
        self.autocomplete_listbox.delete(0, END)
        for suggestion in suggestions:
            self.autocomplete_listbox.insert(END, suggestion)

        # Toggle listbox display based on suggestions
        if suggestions:
            self.autocomplete_listbox.pack()
        else:
            self.autocomplete_listbox.place_forget()

    # Open external weather app
    def openWeatherApp(self):
        # Time Complexity: O(1)
        # Explanation: This simply opens an external application, so it has constant time complexity.
        subprocess.Popen(["python", "weather_treap.py"])

# Create the Tkinter root and start the application
root = Tk()
app = App(root)
root.mainloop()
