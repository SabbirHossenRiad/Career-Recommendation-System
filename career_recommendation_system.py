# -*- coding: utf-8 -*-
"""Career Recommendation System.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mf7_cAMXDKGBeTTb0HwK6c4epNMxhixN
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

from google.colab import drive
drive.mount('/content/drive')

# STEP 1: Setup for Google Colab
from google.colab import output
output.enable_custom_widget_manager()

# STEP 2: Import Required Libraries
import pandas as pd
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import display
import ipywidgets as widgets
from collections import defaultdict

# STEP 3: Load Dataset
file_path = '/content/drive/MyDrive/AI/Data set/career_dataset.csv'
df = pd.read_csv(file_path)

# Build graph from dataset
def build_graph_from_dataset(df):
    G = {}
    for _, row in df.iterrows():
        path = [
            f"Group={row['Group']}",
            f"Math={row['Math_Score']}",
            f"Tech={row['Tech_Interest']}",
            f"Creativity={row['Creativity']}",
            f"Experience={row['Experience']}",
            f"Career={row['Career']}"
        ]
        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            if src not in G:
                G[src] = []
            if dst not in [node for node, _ in G[src]]:
                G[src].append((dst, 1))  # Uniform edge cost
    return G

# Build heuristics
def build_heuristics(G, user_input):
    H = {}
    for node in G:
        if node.startswith("Career="):
            H[node] = 0
        else:
            key, value = node.split('=')
            if key in user_input:
                H[node] = 0 if user_input[key] == value else 2
            else:
                H[node] = 1
    return H

# A* Search Algorithm
def a_star_search(graph, heuristics, start_node, goal_prefix="Career="):
    frontier = []
    heapq.heappush(frontier, (0, start_node, []))
    visited = set()

    while frontier:
        f_score, current, path = heapq.heappop(frontier)
        path = path + [current]

        if current.startswith(goal_prefix):
            return path, f_score

        if current in visited:
            continue
        visited.add(current)

        for neighbor, cost in graph.get(current, []):
            g = len(path)
            h = heuristics.get(neighbor, 1)
            f = g + h
            heapq.heappush(frontier, (f, neighbor, path))

    return None, None

# Filtered graph builder
def build_filtered_graph(df, user_input):
    filtered_df = df.copy()
    for key, value in user_input.items():
        filtered_df = filtered_df[filtered_df[key] == value]
    G = build_graph_from_dataset(filtered_df)
    H = build_heuristics(G, user_input)
    return G, H

# Widgets for input
group_widget = widgets.Dropdown(options=sorted(df['Group'].unique()), description='📘 Group:')
math_widget = widgets.Dropdown(options=sorted(df['Math_Score'].unique()), description='📐 Math:')
tech_widget = widgets.Dropdown(options=sorted(df['Tech_Interest'].unique()), description='💻 Tech:')
creativity_widget = widgets.Dropdown(options=sorted(df['Creativity'].unique()), description='🎨 Creativity:')
experience_widget = widgets.Dropdown(options=sorted(df['Experience'].unique()), description='🧪 Experience:')

# Buttons and output area
submit_button = widgets.Button(description="🔍 Find Career Path", button_style='success')
reset_button = widgets.Button(description="🔁 Reset", button_style='warning')
output_area = widgets.Output()

# Recommendation system
def get_top_recommendations(df, user_input, num_recommendations=3):
    recommendations = defaultdict(int)
    similar_users = df[
        (df['Group'] == user_input['Group']) &
        (df['Math_Score'] == user_input['Math_Score'])
    ]
    if 'Career' in user_input:
        similar_users = similar_users[similar_users['Career'] != user_input.get('Career')]

    for career in similar_users['Career']:
        recommendations[career] += 1

    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return [career for career, _ in sorted_recommendations[:num_recommendations]]

# Submit button functionality
def on_submit_click(b):
    with output_area:
        output_area.clear_output()

        user_input = {
            'Group': group_widget.value,
            'Math_Score': math_widget.value,
            'Tech_Interest': tech_widget.value,
            'Creativity': creativity_widget.value,
            'Experience': experience_widget.value
        }

        G, H = build_filtered_graph(df, user_input)
        start_node = f"Group={user_input['Group']}"
        path, cost = a_star_search(G, H, start_node)

        if path:
            print("\n🎯 Career Recommendation Path:\n")
            for p in path:
                print("→", p)
            print("\n🧮 Total Path Cost:", cost)

            Gviz = nx.DiGraph()
            for i in range(len(path) - 1):
                Gviz.add_edge(path[i], path[i + 1])

            plt.figure(figsize=(12, 6))
            pos = nx.spring_layout(Gviz, seed=42)
            nx.draw(Gviz, pos, with_labels=True, node_color='skyblue', node_size=3000,
                    font_size=10, font_weight='bold', edge_color='gray')
            plt.title("A* Decision Path to Career")
            plt.show()

            recommendations = get_top_recommendations(df, user_input, num_recommendations=3)
            if recommendations:
                print("\n💡 Top 3 Career Recommendations:\n")
                for i, rec in enumerate(recommendations):
                    print(f"{i+1}. {rec}")
        else:
            print("❌ No career path found. Try changing your selections.")

# Reset button functionality
def on_reset_click(b):
    group_widget.value = None
    math_widget.value = None
    tech_widget.value = None
    creativity_widget.value = None
    experience_widget.value = None
    output_area.clear_output()

# Bind functions to buttons
submit_button.on_click(on_submit_click)
reset_button.on_click(on_reset_click)

# Final UI display
display(group_widget, math_widget, tech_widget, creativity_widget, experience_widget,
        widgets.HBox([submit_button, reset_button]), output_area)