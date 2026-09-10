import os
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def load_file_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"


def generate_docs(repo_graph, root_dir):
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        print(
            "OpenAI API key not set or openai package not installed. Using offline fallback."
        )
        return {
            "architecture_summary": "This repository powers the HackerRank Orchestrate terminal-based AI triage agent. It parses support tickets and uses a hybrid retrieval mechanism with TF-IDF and BM25.",
            "onboarding_guide": "To contribute, navigate to the `code/` directory, install `requirements.txt`, and run `pytest tests -q`.",
        }

    client = OpenAI()

    # Load some key files to give context to the LLM
    problem_statement = load_file_content(
        os.path.join(root_dir, "problem_statement.md")
    )
    main_code = load_file_content(os.path.join(root_dir, "code", "main.py"))

    # We truncate main_code to avoid token limits just in case
    main_code = main_code[:3000]

    prompt = f"""
    You are an AI documentation agent for the HackerRank Orchestrate repository.
    Given the following repository knowledge graph:
    {json.dumps(repo_graph, indent=2)}

    And the problem statement overview:
    {problem_statement[:2000]}...

    And parts of the main application code:
    {main_code}

    Write a comprehensive architectural summary that explains what the repository does, how it works, its architecture, and how components communicate.
    Also write a brief onboarding guide explaining how to run it and how to contribute within 5 minutes.

    Format as JSON: {{"architecture_summary": "...", "onboarding_guide": "..."}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "architecture_summary": "Auto-generated summary failed.",
            "onboarding_guide": "Auto-generated onboarding failed.",
        }


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    graph_path = os.path.join(root_dir, "repo_graph.json")

    if not os.path.exists(graph_path):
        print("No repo_graph.json found.")
        return

    with open(graph_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    ai_docs = generate_docs(graph_data, root_dir)

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    out_path = os.path.join(docs_dir, "ai_docs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ai_docs, f, indent=2)

    print(f"AI docs saved to {out_path}")


if __name__ == "__main__":
    main()
