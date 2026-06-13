import os
import json
import subprocess
import shlex
from datetime import datetime


def run_command(command):
    try:
        result = subprocess.run(shlex.split(command), shell=False, capture_output=True, text=True)
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1


def _run_bandit(code_dir):
    bandit_cmd = f"bandit -r {code_dir} -f json"
    bandit_out, _ = run_command(bandit_cmd)
    bandit_issues = 0
    bandit_high = 0
    try:
        bandit_data = json.loads(bandit_out)
        bandit_issues = len(bandit_data.get("results", []))
        bandit_high = sum(
            1
            for r in bandit_data.get("results", [])
            if r.get("issue_severity") == "HIGH"
        )
    except Exception:
        pass
    return bandit_issues, bandit_high

def _run_safety(code_dir):
    req_file = os.path.join(code_dir, "requirements.txt")
    safety_issues = 0
    if os.path.exists(req_file):
        safety_cmd = f"safety check -r {req_file} --json"
        safety_out, _ = run_command(safety_cmd)
        try:
            safety_data = json.loads(safety_out)
            if isinstance(safety_data, dict) and "vulnerabilities" in safety_data:
                safety_issues = len(safety_data["vulnerabilities"])
            elif isinstance(safety_data, list):
                safety_issues = len(safety_data)
        except Exception:
            pass
    return safety_issues

def _calculate_score(bandit_issues, bandit_high, safety_issues, test_status):
    health_score = 100
    if bandit_high > 0:
        health_score -= 30
    health_score -= (bandit_issues - bandit_high) * 2
    health_score -= safety_issues * 10
    if test_status == "Fail":
        health_score -= 40
    return max(0, min(100, health_score))

def generate_health_dashboard():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    code_dir = os.path.join(root_dir, "code")

    print("Running security and dependency checks...")

    bandit_issues, bandit_high = _run_bandit(code_dir)
    safety_issues = _run_safety(code_dir)

    test_cmd = f"python -m pytest {os.path.join(code_dir, 'tests')} -q"
    _, test_rc = run_command(test_cmd)
    test_status = "Pass" if test_rc == 0 else "Fail"

    health_score = _calculate_score(bandit_issues, bandit_high, safety_issues, test_status)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dashboard_content = f"""# Repository Health Dashboard

*Last updated: {timestamp}*

## Overall Health Score: {health_score}/100

| Metric | Status / Count |
|--------|----------------|
| **Test Suite** | {"✅" if test_status == "Pass" else "❌"} {test_status} |
| **Security Issues (Bandit)** | {bandit_issues} total ({bandit_high} HIGH) |
| **Vulnerable Dependencies (Safety)** | {safety_issues} |

## Details

### Security
{"✅ No security issues found." if bandit_issues == 0 else f"⚠️ Found {bandit_issues} potential security issues. Please review Bandit reports."}

### Dependencies
{"✅ No known vulnerabilities in dependencies." if safety_issues == 0 else f"❌ Found {safety_issues} vulnerable dependencies. Run `safety check` and update them."}

---
*This dashboard is generated automatically by the AI Maintainer system.*
"""

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    out_path = os.path.join(docs_dir, "health_dashboard.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dashboard_content)

    print(f"Health dashboard saved to {out_path}")


if __name__ == "__main__":
    generate_health_dashboard()
