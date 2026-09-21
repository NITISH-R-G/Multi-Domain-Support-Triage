import os
import json
import ast
from pathlib import Path

def extract_python_entities(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    entities = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            entities.append({"type": "class", "name": node.name, "file": file_path})
        elif isinstance(node, ast.FunctionDef):
            entities.append({"type": "function", "name": node.name, "file": file_path})
    return entities

def build_knowledge_graph():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    code_dir = os.path.join(root_dir, "code")
    automation_dir = os.path.join(root_dir, "automation")

    graph = {"nodes": [], "edges": []}

    for d in [code_dir, automation_dir]:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    graph["nodes"].append({"id": rel_path, "type": "file"})

                    entities = extract_python_entities(full_path)
                    for entity in entities:
                        node_id = f"{rel_path}:{entity['name']}"
                        graph["nodes"].append({"id": node_id, "type": entity["type"]})
                        graph["edges"].append({"source": rel_path, "target": node_id, "type": "contains"})

    out_path = os.path.join(root_dir, "repo_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph saved to {out_path}")

if __name__ == "__main__":
    build_knowledge_graph()
