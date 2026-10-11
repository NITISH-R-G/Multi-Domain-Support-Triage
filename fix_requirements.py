with open('automation/requirements.txt', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('networkx'):
        lines[i] = 'networkx>=3.4.2\n' # Using a lower requirement compatible with python 3.11 or not restricted to 3.12. Wait, networkx 3.7 requires python 3.12?
        # Let's check the error: "3.7 Requires-Python >=3.12,!=3.14.1; 3.7rc0 Requires-Python >=3.12,!=3.14.1"
        # So we should downgrade to networkx>=3.0 or similar.
        lines[i] = 'networkx<3.7\n'

with open('automation/requirements.txt', 'w') as f:
    f.writelines(lines)
