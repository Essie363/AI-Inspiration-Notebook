var fs=require("fs");
var lines=fs.readFileSync("scripts/generate_page.js","utf8").split("\n");
// Line 270 (index 269): extra </div> after channel-opportunities close
lines.splice(269, 1);
fs.writeFileSync("scripts/generate_page.js", lines.join("\n"), "utf8");
console.log("Removed extra </div>. Now", lines.length, "lines.");
