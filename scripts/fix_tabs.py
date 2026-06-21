import re
with open("scripts/generate_page.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the whole tabs section
old = '''    tabs_html = ""
    for i, cat_key in enumerate(tab_order):
        active = " active" if i == 0 else ""
        tabs_html += '<button class="tab' + active + '" onclick="filterCategory(this, \\'' + cat_key + '\\')">' + tab_labels[cat_key] + "</button>\\n"
    tabs_html += '<button class="tab" onclick="filterCategory(this, \\'all\\')">All (' + str(total) + ")</button>\\n\""""

# Actually, the file is already partially modified. Let me just fix line 116.
lines = content.split("\\n")
for i, line in enumerate(lines):
    if "tabs_html" in line and "active" in line and "tab" in line:
        # Remove the + active + reference
        lines[i] = line.replace("+ active + ", "").replace("' + active + '", "").replace("' + active + ", "")
        # Fix the resulting string
        lines[i] = lines[i].replace("'<button class=\"tab", "'<button class=\"tab\"")
        break

content = "\\n".join(lines)
with open("scripts/generate_page.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed")
