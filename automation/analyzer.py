import ast
import json
import os


def get_python_files(root_dir):
    py_files = []
    for root, dirs, files in os.walk(root_dir):
        if ".venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def parse_imports(filepath):
    imports = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return imports


def detect_frameworks(root_dir):
    frameworks = []
    req_file = os.path.join(root_dir, "code", "requirements.txt")
    if os.path.exists(req_file):
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "pytest" in content:
                    frameworks.append("pytest")
                if "openai" in content:
                    frameworks.append("openai")
                if "scikit-learn" in content:
                    frameworks.append("scikit-learn")
        except Exception:
            pass
    return frameworks


def build_knowledge_graph(root_dir):
    graph = {"files": {}, "frameworks": detect_frameworks(root_dir), "structure": {}}

    py_files = get_python_files(root_dir)
    for pf in py_files:
        rel_path = os.path.relpath(pf, root_dir)
        imports = parse_imports(pf)
        graph["files"][rel_path] = {"imports": imports}

    return graph


if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    graph = build_knowledge_graph(root_dir)

    out_path = os.path.join(root_dir, "repo_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph saved to {out_path}")
