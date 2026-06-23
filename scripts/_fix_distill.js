var fs=require("fs");
var lines=fs.readFileSync("scripts/generate_page.js","utf8").split("\n");

// Change the BP_DIR reference and add distilled fallback logic
// Find: "const fp = BP_DIR + ..." line
for (var i=0; i<lines.length; i++) {
  if (lines[i].includes("const fp = BP_DIR +") && lines[i].includes(".md")) {
    // Replace the file-reading section
    // Find the block: for (const f of bpDates) { ... }
    var blockStart = i - 4; // "if (bpDates.length > 0) {"
    for (var j=blockStart; j<lines.length; j++) {
      if (lines[j].includes("oppHtml += '</div>';") && lines[j+1] && lines[j+1].trim() === "}") {
        var blockEnd = j+1;
        // Replace block
        var newBlock = [
          '  if (bpDates.length > 0) {',
          '    const OPP_DIR = ROOT + "/data/opportunities";',
          '    oppHtml = "";',
          '    for (const f of bpDates) {',
          '      // Prefer distilled version, fallback to raw BuilderPulse',
          '      const distilledPath = OPP_DIR + "/" + f.date + "-distilled.md";',
          '      const rawPath = f.path;',
          '      const readPath = fs.existsSync(distilledPath) ? distilledPath : rawPath;',
          '      const raw = fs.readFileSync(readPath, "utf-8");',
          '      const parsed = parseMdToHtml(raw);',
          '      oppHtml += \'<div class="opp-day">\';',
          '      oppHtml += \'<div class="opp-day-header">\' + f.date + \'</div>\';',
          '      oppHtml += \'<div class="opp-day-content">\' + parsed + \'</div>\';',
          '      oppHtml += \'</div>\';',
          '    }',
          '  }'
        ];
        lines.splice(blockStart, blockEnd - blockStart + 1, ...newBlock);
        console.log("Replaced BP file reading block at lines", blockStart+1, "-", blockEnd+1);
        break;
      }
    }
    break;
  }
}

fs.writeFileSync("scripts/generate_page.js", lines.join("\n"), "utf8");
console.log("Done. Now", lines.length, "lines.");
