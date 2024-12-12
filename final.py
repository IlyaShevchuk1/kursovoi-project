import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import permutations

class GraphModel:
    """Модель для управления графом"""
    def __init__(self):
        self.adjacency_matrix = {}

    def add_edge(self, city1, city2, distance):
        if city1 not in self.adjacency_matrix:
            self.adjacency_matrix[city1] = {}
        if city2 not in self.adjacency_matrix:
            self.adjacency_matrix[city2] = {}

        self.adjacency_matrix[city1][city2] = distance
        self.adjacency_matrix[city2][city1] = distance  # Граф неориентированный

    def reset(self):
        self.adjacency_matrix = {}

    def get_graph(self):
        """Создает NetworkX граф из матрицы смежности"""
        G = nx.Graph()
        for city1, neighbors in self.adjacency_matrix.items():
            for city2, distance in neighbors.items():
                G.add_edge(city1, city2, weight=distance)
        return G


class TSPSolver:
    """Класс для решения задачи коммивояжера"""
    @staticmethod
    def calculate_tsp_route(graph_model, start_city):
        G = graph_model.get_graph()
        nodes = list(G.nodes)
        if start_city not in nodes:
            return None, "Начальный город отсутствует в графе!"

        min_distance = float('inf')
        best_route = None

        for route in permutations([node for node in nodes if node != start_city]):
            route = [start_city] + list(route)
            distance = 0
            for i in range(len(route) - 1):
                distance += G[route[i]][route[i + 1]]['weight']

            distance += G[route[-1]][route[0]]['weight']

            if distance < min_distance:
                min_distance = distance
                best_route = route

        return best_route, min_distance


class GraphView:
    """Класс для отображения графа"""
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_graph(self, graph_model):
        self.ax.clear()
        G = graph_model.get_graph()
        pos = nx.spring_layout(G)
        edges = G.edges(data=True)
        edge_labels = {(u, v): f"{d['weight']} км" for u, v, d in edges}

        nx.draw(G, pos, ax=self.ax, with_labels=True, node_size=2000,
                node_color="lightblue", font_size=12, font_weight="bold")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax, font_size=10)
        self.canvas.draw()

    def clear_graph(self):
        self.ax.clear()
        self.canvas.draw()


class Application:
    """Главное приложение"""
    def __init__(self, root):
        self.graph_model = GraphModel()
        self.graph_view = GraphView(root)

        self.text_output = tk.Text(root, height=15, width=70)
        self.text_output.pack()

        self.create_ui(root)

    def create_ui(self, root):
        tk.Label(root, text="Город 1:").pack()
        self.entry_city1 = tk.Entry(root)
        self.entry_city1.pack()

        tk.Label(root, text="Город 2:").pack()
        self.entry_city2 = tk.Entry(root)
        self.entry_city2.pack()

        tk.Label(root, text="Расстояние (км):").pack()
        self.entry_distance = tk.Entry(root)
        self.entry_distance.pack()

        add_button = tk.Button(root, text="Добавить", command=self.add_edge)
        add_button.pack()

        tk.Label(root, text="Начальный город:").pack()
        self.entry_start_city = tk.Entry(root)
        self.entry_start_city.pack()

        calculate_button = tk.Button(root, text="Рассчитать маршрут", command=self.calculate_tsp_route)
        calculate_button.pack()

        reset_button = tk.Button(root, text="Сброс", command=self.reset)
        reset_button.pack()

    def add_edge(self):
        city1 = self.entry_city1.get()
        city2 = self.entry_city2.get()
        distance = self.entry_distance.get()

        try:
            distance = int(distance)
            if city1 == city2:
                raise ValueError("Города не могут быть одинаковыми!")
            if distance < 0:
                raise ValueError("Расстояние не может быть отрицательным!")

            self.graph_model.add_edge(city1, city2, distance)
            self.update_output()
            self.graph_view.update_graph(self.graph_model)
        except ValueError as e:
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, str(e))

    def update_output(self):
        self.text_output.delete(1.0, tk.END)
        for city, neighbors in self.graph_model.adjacency_matrix.items():
            neighbors_str = ", ".join([f"{neighbor} = {distance}" for neighbor, distance in neighbors.items()])
            self.text_output.insert(tk.END, f"{city}: {neighbors_str}\n")

    def calculate_tsp_route(self):
        start_city = self.entry_start_city.get()
        best_route, result = TSPSolver.calculate_tsp_route(self.graph_model, start_city)
        self.text_output.delete(1.0, tk.END)
        if best_route:
            self.text_output.insert(tk.END, f"Оптимальный маршрут: {' -> '.join(best_route)}\nДлина маршрута: {result} км")
        else:
            self.text_output.insert(tk.END, result)

    def reset(self):
        self.graph_model.reset()
        self.text_output.delete(1.0, tk.END)
        self.graph_view.clear_graph()


# Запуск приложения1
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Расчет оптимального маршрута для коммивояжёра")
    root.geometry("1200x1000")
    app = Application(root)
    root.mainloop()