import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

// news-image-20261126: copy the rendered front page to the output dir.
// Node 22 stdlib only. Verifies the PNG magic before writing.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const data = readFileSync(new URL("./entry.png", import.meta.url));
const PNG_MAGIC = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
if (!data.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}
mkdirSync(outDir, { recursive: true });
const out = join(outDir, "entry.png");
writeFileSync(out, data);
console.log(`wrote ${out} (${data.length} bytes)`);
