// /ops/blog_guard.mjs
import fs from "node:fs";

const home = fs.readFileSync("./index.html","utf8");
const postPath = process.argv[2] || "";
if(!postPath) { console.error("Usage: node /ops/blog_guard.mjs ./blog/SLUG/index.html"); process.exit(1); }
const post = fs.readFileSync(postPath,"utf8");

function sliceBetween(s, startRx, endRx) {
  const sIdx = s.search(startRx); if (sIdx < 0) return "";
  const tail = s.slice(sIdx);
  const eRel = tail.search(endRx); if (eRel < 0) return "";
  return tail.slice(0, eRel + tail.match(endRx)[0].length);
}

// Try comment sentinels; else fallback to first <header>/<nav> and last <footer>
const hHeader = sliceBetween(home, /<!--\s*HEADER:START\s*-->|<(header|nav)[^>]*>/i, /<!--\s*HEADER:END\s*-->|<\/\s*(header|nav)\s*>/i);
const hFooter = sliceBetween(home, /<!--\s*FOOTER:START\s*-->|<footer[^>]*>/i, /<!--\s*FOOTER:END\s*-->|<\/\s*footer\s*>/i);
const pHeader = sliceBetween(post, /<!--\s*HEADER:START\s*-->|<(header|nav)[^>]*>/i, /<!--\s*HEADER:END\s*-->|<\/\s*(header|nav)\s*>/i);
const pFooter = sliceBetween(post, /<!--\s*FOOTER:START\s*-->|<footer[^>]*>/i, /<!--\s*FOOTER:END\s*-->|<\/\s*footer\s*>/i);

function normalize(x){return x.replace(/\s+/g," ").trim();}
function die(msg){console.error("❌ "+msg); process.exit(1);}
function ok(msg){console.log("✅ "+msg);}

if (!hHeader || !hFooter) die("Could not detect header/footer in homepage.");
if (!pHeader || !pFooter) die("Post missing header/footer blocks.");
if (normalize(hHeader) !== normalize(pHeader)) die("Header mismatch vs homepage (parity failed).");
if (normalize(hFooter) !== normalize(pFooter)) die("Footer mismatch vs homepage (parity failed).");
ok("Header/Footer parity OK.");

if (!post.includes('reading-progress') && !post.includes('id="rp-bar"')) die("Reading progress bar (reading-progress or #rp-bar) missing.");
if (!/position:\s*fixed;?[^}]*top:\s*(0|72px)/i.test(post)) die("Progress bar must be fixed at top:0 or top:72px.");
if (!/z-index:\s*(2147483647|\d{3,})/.test(post)) die("Progress bar z-index must be reasonably high (999+).");
ok("Progress bar placement OK.");

if (/box-shadow:\s*[^;]+/i.test(pHeader)) die("Navbar must not have box-shadow on blog page.");
if (/backdrop-filter|filter:\s*drop-shadow/i.test(pHeader)) die("Navbar must not add filters/shadows.");
ok("Navbar has no added shadow.");

if (!/class="related-posts"/.test(post)) die("Related Posts section (.related-posts) missing.");
if (!/class="author-box"/.test(post)) die("Author Box (.author-box) missing.");
ok("Required sections present.");

// Ensure H1 contains primary_keyword (if provided in blog_run.yml)
let kw = "";
try {
  const yml = fs.readFileSync("./ops/blog_run.yml","utf8");
  kw = (yml.match(/primary_keyword:\s*"?(.+?)"?\n/i)||[])[1] || "";
} catch {}
if (kw) {
  const h1 = (post.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)||[])[1] || "";
  if (!new RegExp(kw, "i").test(h1)) die(`H1 must include primary_keyword: ${kw}`);
}
ok("Topic/H1 keyword check passed.");