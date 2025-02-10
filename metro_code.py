import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import threading

# Chennai Metro stations and connections (Graph Representation)
metro_graph = {
    "Wimco Nagar": ["Tollgate"],
    "Tollgate": ["Wimco Nagar", "Theradi"],
    "Theradi": ["Tollgate", "Mannadi"],
    "Mannadi": ["Theradi", "Central Metro"],
    "Central Metro": ["Mannadi", "Egmore", "Government Estate"],
    "Egmore": ["Central Metro", "Nehru Park"],
    "Nehru Park": ["Egmore", "Kilpauk"],
    "Kilpauk": ["Nehru Park", "Pachaiyappa’s College"],
    "Pachaiyappa’s College": ["Kilpauk", "Shenoy Nagar"],
    "Shenoy Nagar": ["Pachaiyappa’s College", "Anna Nagar East"],
    "Anna Nagar East": ["Shenoy Nagar", "Anna Nagar Tower"],
    "Anna Nagar Tower": ["Anna Nagar East", "Thirumangalam"],
    "Thirumangalam": ["Anna Nagar Tower", "Koyambedu"],
    "Koyambedu": ["Thirumangalam", "CMBT"],
    "CMBT": ["Koyambedu", "Arumbakkam"],
    "Arumbakkam": ["CMBT", "Vadapalani"],
    "Vadapalani": ["Arumbakkam", "Ashok Nagar"],
    "Ashok Nagar": ["Vadapalani", "Ekkatuthangal"],
    "Ekkatuthangal": ["Ashok Nagar", "Guindy"],
    "Guindy": ["Ekkatuthangal", "Alandur"],
    "Alandur": ["Guindy", "Nanganallur Road", "Little Mount"],
    "Nanganallur Road": ["Alandur", "Meenambakkam"],
    "Meenambakkam": ["Nanganallur Road", "Airport"],
    "Airport": ["Meenambakkam"],
    "Little Mount": ["Alandur", "Saidapet"],
    "Saidapet": ["Little Mount", "Teynampet"],
    "Teynampet": ["Saidapet", "AG-DMS"],
    "AG-DMS": ["Teynampet", "Government Estate"],
    "Government Estate": ["AG-DMS", "Central Metro"]
}

# Function to find the shortest path using Dijkstra's algorithm
def find_shortest_path(start, end):
    graph = nx.Graph()
    for station, connections in metro_graph.items():
        for connected_station in connections:
            graph.add_edge(station, connected_station, weight=1)  # Equal weights for simplicity
    try:
        return nx.shortest_path(graph, source=start, target=end, weight="weight")
    except nx.NetworkXNoPath:
        return None

# Function to calculate fare, stops, and travel time
def calculate_fare_and_time(path):
    if not path:
        return None, None, None
    stops = len(path) - 1
    travel_time = stops * 2  # Assuming 2 minutes per stop
    fare = 10 + (stops * 5)  # Base fare ₹10 + ₹5 per stop
    return stops, travel_time, fare

# Function to visualize only the shortest route in a new figure
def visualize_shortest_route(path):
    """Displays a graph with only the shortest route"""
    if not path:
        return

    graph = nx.Graph()
    for i in range(len(path) - 1):
        graph.add_edge(path[i], path[i + 1])

    plt.figure(figsize=(8, 5))
    pos = nx.spring_layout(graph)  # Auto layout positioning
    nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="red", node_size=2000, font_size=10, font_weight="bold")
    plt.title("Shortest Route Visualization")
    plt.show()

# Function to show the clickable metro map for station selection
def show_clickable_map(app, is_start_selection=True):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    graph = nx.Graph()
    for station, connections in metro_graph.items():
        for connected_station in connections:
            graph.add_edge(station, connected_station)

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=1500, font_size=10)

    def on_click(event):
        for station, coords in pos.items():
            x, y = coords
            if abs(event.xdata - x) < 0.05 and abs(event.ydata - y) < 0.05:
                if is_start_selection:
                    app.start_var.set(station)
                else:
                    app.end_var.set(station)
                plt.close()
                break

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.title("Click on a Station to Select")
    plt.show()

# GUI Application
class MetroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chennai Metro Route Finder")
        self.root.geometry("850x600")
        self.root.configure(bg="lightblue")

        ttk.Label(root, text="Chennai Metro Route Finder", font=("Arial", 18, "bold")).pack(pady=10)

        # Metro Map Image in Main UI
        self.map_image = Image.open("metro.png")
        self.map_image = self.map_image.resize((600, 350), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(self.map_image)

        self.canvas = tk.Canvas(root, width=600, height=350)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)

        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        frame = tk.Frame(root, bg="lightblue")
        frame.pack(pady=10)

        ttk.Label(frame, text="Start Station:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.start_menu = ttk.Combobox(frame, textvariable=self.start_var, values=list(metro_graph.keys()), state="readonly", font=("Arial", 12))
        self.start_menu.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Pick on Map", command=lambda: show_clickable_map(self, True)).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Destination Station:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5)
        self.end_menu = ttk.Combobox(frame, textvariable=self.end_var, values=list(metro_graph.keys()), state="readonly", font=("Arial", 12))
        self.end_menu.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Pick on Map", command=lambda: show_clickable_map(self, False)).grid(row=1, column=2, padx=5, pady=5)

        self.find_button = ttk.Button(root, text="Find Shortest Route", command=self.start_thread)
        self.find_button.pack(pady=15, ipadx=20, ipady=10)

    def start_thread(self):
        threading.Thread(target=self.compute_route, daemon=True).start()

    def compute_route(self):
        start = self.start_var.get()
        end = self.end_var.get()

        if not start or not end:
            messagebox.showerror("Error", "Please select both stations.")
            return

        shortest_path = find_shortest_path(start, end)

        if shortest_path:
            stops, travel_time, fare = calculate_fare_and_time(shortest_path)
            messagebox.showinfo("Route Details", f"Route: {' → '.join(shortest_path)}\nStops: {stops}\nTravel Time: {travel_time} mins\nFare: ₹{fare}")
            self.root.after(0, lambda: visualize_shortest_route(shortest_path))

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MetroApp(root)
    root.mainloop()
