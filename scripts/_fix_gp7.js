var fs=require("fs");
var lines=fs.readFileSync("scripts/generate_page.js","utf8").split("\n");

// Find the template area: after "</div>" closing timeline-layout, before opportunities
// Line ~263 (index 262): "    </div>" -- this closes timeline-layout
// We need to add "</div>" for channel-builder BEFORE the opportunities div starts
// AND remove the extra "</div>" after channel-opportunities

// Current:
//    </div>           <- closes timeline-layout (index ~262)
//                      <- MISSING: closes channel-builder
//   <div id="channel-opportunities"...
// ...
//   </div>             <- closes channel-opportunities (index ~267)
//   </div>             <- EXTRA (index ~268)

// Find and fix
for (var i=0; i<lines.length; i++) {
  // Find the line that's "</div>" followed by a blank line then channel-opportunities
  if (lines[i].trim() === '</div>' && 
      i+2 < lines.length && 
      lines[i+2].includes('channel-opportunities')) {
    // This </div> closes timeline-layout. Insert channel-builder closing after it.
    lines.splice(i+1, 0, '  </div>');
    console.log("Inserted channel-builder closing at line", i+2);
    break;
  }
}

// Now find the extra </div> after channel-opportunities closing
// Pattern: "...channel-opportunities...</div>" then a blank then "</div>"
for (var i=0; i<lines.length; i++) {
  if (lines[i].trim() === '</div>' && 
      i > 1 && 
      lines[i-2].includes('channel-opportunities')) {
    // This is the extra closing. Remove it.
    lines.splice(i, 1);
    console.log("Removed extra </div> at line", i+1);
    break;
  }
}

fs.writeFileSync("scripts/generate_page.js", lines.join("\n"), "utf8");
console.log("Fixed. Now", lines.length, "lines.");
