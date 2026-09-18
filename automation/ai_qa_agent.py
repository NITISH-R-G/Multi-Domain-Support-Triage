import os
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def read_file(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"


def generate_qa_report(tool_outputs, root_dir):
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        print(
            "OpenAI API key not set or openai package not installed. Skipping AI generation."
        )
        # Fallback basic report
        return "# Enterprise QA Report\n\nAI generation skipped due to missing API key or `openai` package.\n"

    client = OpenAI()

    prompt = f"""
    You are an AI Quality Assurance agent for an enterprise repository.
    The CI/CD pipeline has run multiple code quality, security, and analysis tools.
    Below are the raw outputs from these tools (some may be empty if no issues were found or if the tool failed to run).

    {json.dumps(tool_outputs, indent=2)}

    Based on these outputs, generate a comprehensive Markdown report. The report must include:
    1. A summary of overall repository health.
    2. Estimated scores (out of 100) for: Code Quality, Maintainability, Technical Debt, Security, and Dependency Health.
    3. An explanation of the findings in plain English.
    4. Prioritization of issues by severity.
    5. Actionable recommendations for fixes.
    6. Suggested refactoring opportunities and architectural concerns.
    7. Complexity and dead code trends.

    Format the response directly as Markdown. Do not include markdown block ticks like ```markdown at the beginning or end.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"# Enterprise QA Report\n\nError generating report: {e}\n"


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    reports_dir = os.path.join(root_dir, "reports")

    # Read tool outputs
    tools = {
        "ruff": "ruff_report.json",
        "mypy": "mypy_report.txt",
        "vulture": "vulture_report.txt",
        "pylint": "pylint_report.json",
        "radon_cc": "radon_cc.json",
        "radon_mi": "radon_mi.json",
        "bandit": "bandit_report.json",
        "safety": "safety_report.json",
        "detect_secrets": "secrets_report.json",
    }

    tool_outputs = {}
    for tool, filename in tools.items():
        filepath = os.path.join(reports_dir, filename)
        content = read_file(filepath)
        if content:
            # Try parsing JSON if applicable, otherwise keep as text
            if filepath.endswith(".json"):
                try:
                    tool_outputs[tool] = json.loads(content)
                except json.JSONDecodeError:
                    tool_outputs[tool] = content
            else:
                tool_outputs[tool] = content
        else:
            tool_outputs[tool] = "No report generated or file missing."

    report_content = generate_qa_report(tool_outputs, root_dir)

    os.makedirs(reports_dir, exist_ok=True)
    out_path = os.path.join(reports_dir, "qa_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"QA report saved to {out_path}")


if __name__ == "__main__":
    main()
