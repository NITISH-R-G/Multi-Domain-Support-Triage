1. Fix automation Python scripts memory limits/security:
- Updated `automation/health_dashboard.py` to use `shell=False` to pass security scans. Done.
- Updated `automation/ai_maintainer.py` to add `timeout=10` to `requests.post` call to avoid hanging. Done.
2. Automate GitHub Issue formats:
- Converted `bug_report.md` and `feature_request.md` into YAML based GitHub issue templates. Done.
3. Fix automated workflows concurrency issues:
- Added `git pull --rebase origin ${GITHUB_REF#refs/heads/}` before `git push` in `.github/workflows/autonomous_repo.yml` and `.github/workflows/auto_fix.yml`. Done.
4. Auto deploy docs via Pages:
- Created `.github/workflows/pages.yml` to automatically deploy the docs to GitHub Pages. Done.
5. Fix Py3.11 compatibility:
- Verified `types.py` issue and Python 3.12 syntax `type X = Y` isn't anywhere else and removed `types.py`. Done.
- Fixed `code/answer_synthesis.py` hash bug. Done.
6. Verify locally
- `flake8` and `bandit`
- `radon cc`
- `pytest`
7. Pre-commit tasks and final review.
