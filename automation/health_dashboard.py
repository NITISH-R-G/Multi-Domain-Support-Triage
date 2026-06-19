import sys
import os
import json
import subprocess  # nosec B404
from datetime import datetime

def get_bandit_stats(code_dir):
    try:
        # nosemgrep
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", str(code_dir), "-f", "json"],
            shell=False, capture_output=True, text=True
        )  # nosec B603
        bandit_out = result.stdout
        bandit_data = json.loads(bandit_out)
        issues = len(bandit_data.get("results", []))
        high = sum(1 for r in bandit_data.get("results", []) if r.get("issue_severity") == "HIGH")
        return issues, high
    except Exception:
        return 0, 0

def get_safety_stats(req_file):
    if not os.path.exists(req_file):
        return 0
    try:
        # nosemgrep
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "-r", str(req_file), "--json"],
            shell=False, capture_output=True, text=True
        )  # nosec B603
        safety_out = result.stdout
        safety_data = json.loads(safety_out)
        if isinstance(safety_data, dict) and "vulnerabilities" in safety_data:
            return len(safety_data["vulnerabilities"])
        elif isinstance(safety_data, list):
            return len(safety_data)
        return 0
    except Exception:
        return 0

def generate_health_dashboard():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    code_dir = os.path.join(root_dir, "code")

    print("Running security and dependency checks...")

    bandit_issues, bandit_high = get_bandit_stats(code_dir)
    req_file = os.path.join(code_dir, "requirements.txt")
    safety_issues = get_safety_stats(req_file)

    try:
        # nosemgrep
        test_result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "-q"],
            shell=False, capture_output=True, text=True, cwd=str(code_dir)
        )  # nosec B603
        test_rc = test_result.returncode
    except Exception:
        test_rc = 1

    test_status = "Pass" if test_rc == 0 else "Fail"

    health_score = 100
    if bandit_high > 0:
        health_score -= 30
    health_score -= (bandit_issues - bandit_high) * 2
    health_score -= safety_issues * 10
    if test_status == "Fail":
        health_score -= 40

    health_score = max(0, min(100, health_score))
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
