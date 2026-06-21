import re
with open("assets/script.js", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Add filter bar
old = """  var html = "";

  for (var d of sortedDates)"""
new = """  var filterHtml = '<div class="fav-filter">';
  filterHtml += '<button class="fav-filter-btn active" data-cat="all" onclick="filterFav(this)">All</button>';
  filterHtml += '<button class="fav-filter-btn" data-cat="extension" onclick="filterFav(this)">Extension</button>';
  filterHtml += '<button class="fav-filter-btn" data-cat="creative" onclick="filterFav(this)">Creative</button>';
  filterHtml += '<button class="fav-filter-btn" data-cat="workflow" onclick="filterFav(this)">Workflow</button>';
  filterHtml += '</div>';
  var html = filterHtml;

  for (var d of sortedDates)"""
c = c.replace(old, new)

# 2. Filter by category + store id
old = "    if (!groups[f.addedAt]) groups[f.addedAt] = [];\n    var card = document.querySelector"
new = "    var card = document.querySelector"
c = c.replace(old, new)

old = "    var card = document.querySelector('.card[data-pid=\"' + f.id + '\"]');\n    if (card) {"
new = "    var card = document.querySelector('.card[data-pid=\"' + f.id + '\"]');\n    if (!card) continue;\n    var cat = card.getAttribute(\"data-category\") || \"\";\n    if (favFilter != \"all\" && cat != favFilter) continue;\n    if (!groups[f.addedAt]) groups[f.addedAt] = [];"
c = c.replace(old, new)

# 3. Add id to item object
c = c.replace("      groups[f.addedAt].push({ title: title, link: link });", "      groups[f.addedAt].push({ id: f.id, title: title, link: link });")

# 4. Remove date from item display
old = "      html += '    <div class=\"fav-item-info\">';\n      html += '      <span class=\"fav-item-title\">' + item.title + '</span>';\n      html += '      <div class=\"fav-item-meta\">';\n      html += '        <span>' + d + '</span>';\n      html += '      </div>';\n      html += '    </div>';"
new = "      html += '    <div class=\"fav-item-info\">';\n      html += '      <span class=\"fav-item-title\">' + item.title + '</span>';\n      html += '    </div>';"
c = c.replace(old, new)

# 5. Fix unfav call
c = c.replace("unfavFromModal('\" + f.id + \"')", "unfavFromModal('\" + item.id + \"')")

with open("assets/script.js", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed")
