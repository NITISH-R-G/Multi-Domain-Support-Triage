with open("code/answer_synthesis.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "h = int(" in line:
        lines[i] = '    h = int(hashlib.sha256(body.encode("utf-8")).hexdigest(), 16)\n'
    if 'body += "\n\n" + _closings[h % len(_closings)]' in line:
        lines[i] = '    body += "\\n\\n" + _closings[h % len(_closings)]\n'
with open("code/answer_synthesis.py", "w") as f:
    f.writelines(lines)
