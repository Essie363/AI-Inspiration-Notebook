var fs=require("fs");
var lines=fs.readFileSync("scripts/generate_page.js","utf8").split("\n");
// Find the try block that's missing its catch
for (var i=0; i<lines.length; i++) {
  if (lines[i].trim() === "try {" && i < 200) {
    // Look for the closing of the try block: should be "} catch(e) {"
    for (var j=i+1; j<lines.length && j<i+30; j++) {
      if (lines[j].trim().startsWith("} catch")) {
        console.log("Catch found at line", j+1);
        break;
      }
      if (lines[j].trim() === "}" && j > i+5) {
        // This might be the end of a block that should have a catch
        // Check if next line is not "catch"
        if (!lines[j+1] || !lines[j+1].trim().startsWith("catch")) {
          console.log("Missing catch at line", j+1, "- inserting");
          lines.splice(j, 0, "} catch(e) {", '  oppHtml = "<div class=\"opp-empty\">Unable to load BuilderPulse data: " + esc(String(e)) + "</div>";');
          break;
        }
      }
    }
    break;
  }
}
fs.writeFileSync("scripts/generate_page.js", lines.join("\n"), "utf8");
console.log("Done. Now", lines.length, "lines.");
