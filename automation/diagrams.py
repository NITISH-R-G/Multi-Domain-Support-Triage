import json
import os


def generate_mermaid_graph(graph_data):
    lines = ["```mermaid", "graph TD"]

    files = graph_data.get("files", {})

    # Create nodes
    for i, (filepath, data) in enumerate(files.items()):
        node_id = f"node_{i}"
        filename = os.path.basename(filepath)
        lines.append(f'    {node_id}["{filename}"]')
        # Make node clickable to source file
        lines.append(f'    click {node_id} href "../{filepath}"')

    # Create edges
    file_list = list(files.keys())
    for i, (filepath, data) in enumerate(files.items()):
        imports = data.get("imports", [])
        for imp in imports:
            # Simple heuristic: if import matches part of another filename
            for j, other_file in enumerate(file_list):
                if i != j:
                    other_base = os.path.splitext(os.path.basename(other_file))[0]
                    if other_base in imp:
                        lines.append(f"    node_{i} --> node_{j}")

    lines.append("```")
    return "\n".join(lines)


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    graph_path = os.path.join(root_dir, "repo_graph.json")

    if not os.path.exists(graph_path):
        print("No repo_graph.json found.")
        return

    with open(graph_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    mermaid_str = generate_mermaid_graph(graph_data)

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    out_path = os.path.join(docs_dir, "diagrams.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Diagrams\n\n")
        f.write("## Dependency Graph\n\n")
        f.write(mermaid_str)
        f.write("\n")

    print(f"Diagrams saved to {out_path}")


if __name__ == "__main__":
    main()
