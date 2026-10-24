import os
import json
import ast


def extract_docstrings(root_dir):
    api_docs = []
    for dirpath, _, filenames in os.walk(os.path.join(root_dir, "code")):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        rel_path = os.path.relpath(filepath, root_dir)
                        api_docs.append(f"### `{rel_path}`\n\n{module_doc}\n")

                    for node in tree.body:
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            doc = ast.get_docstring(node)
                            if doc:
                                prefix = "Class" if isinstance(node, ast.ClassDef) else "Function"
                                api_docs.append(f"#### {prefix} `{node.name}`\n\n{doc}\n")
                except Exception:
                    pass
    return "\n".join(api_docs)


def generate_readme():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Load knowledge graph
    graph_path = os.path.join(root_dir, "repo_graph.json")
    graph_data = {}
    if os.path.exists(graph_path):
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

    # Load AI docs
    ai_docs_path = os.path.join(root_dir, "docs", "ai_docs.json")
    ai_docs = {}
    if os.path.exists(ai_docs_path):
        with open(ai_docs_path, "r", encoding="utf-8") as f:
            ai_docs = json.load(f)

    # Load diagrams
    diagrams_path = os.path.join(root_dir, "docs", "diagrams.md")
    diagrams = ""
    if os.path.exists(diagrams_path):
        with open(diagrams_path, "r", encoding="utf-8") as f:
            diagrams = f.read()

    frameworks = (
        ", ".join(graph_data.get("frameworks", []))
        if graph_data.get("frameworks")
        else "Not detected"
    )

    # Load existing README to preserve it
    readme_path = os.path.join(root_dir, "README.md")
    original_readme = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            original_readme = f.read()

    api_docs_content = extract_docstrings(root_dir)

    # Define the automation section
    automation_section = f"""
---

# 🤖 Autonomous Repository System

![CI Status](https://github.com/your-org/your-repo/actions/workflows/autonomous_repo.yml/badge.svg)

*This section is automatically maintained by the AI documentation agent.*

## System Overview
{ai_docs.get("architecture_summary", "AI generated architecture summary not available.")}

## Key Features & Technology Stack
- **Frameworks Detected:** {frameworks}
- Automatically traces internal dependencies across {len(graph_data.get("files", {}))} python files.
- Generates interactive Mermaid architectures and documentation.

{diagrams}

## API Documentation
*Auto-generated from docstrings by AST parser.*
{api_docs_content}

## Automation Onboarding & Contribution
{ai_docs.get("onboarding_guide", "Contributions are welcome! Please run the automation scripts or let GitHub Actions update docs on PRs.")}
"""

    # We insert the automation section at the end of the original README if not already present
    # Or replace it if it is already there. We'll use a marker.
    marker_start = "<!-- AUTONOMOUS_SECTION_START -->"
    marker_end = "<!-- AUTONOMOUS_SECTION_END -->"

    full_automation_content = f"\n{marker_start}\n{automation_section}\n{marker_end}\n"

    if marker_start in original_readme and marker_end in original_readme:
        # Replace existing section
        before = original_readme.split(marker_start)[0]
        after = original_readme.split(marker_end)[1]
        new_readme = before + full_automation_content + after
    else:
        # Append to the end
        new_readme = original_readme + full_automation_content

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print(f"Updated README.md at {readme_path} (preserved original content)")


if __name__ == "__main__":
    generate_readme()
