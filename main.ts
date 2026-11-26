// Copy the rendered front page into the make.fun output directory.
// Node 22 stdlib only: no dependencies.
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = join(import.meta.dirname, "entry.png");

const buf = readFileSync(src);
if (buf[0] !== 0x89 || buf[1] !== 0x50 || buf[2] !== 0x4e || buf[3] !== 0x47) {
  throw new Error("entry.png is not a PNG file");
}
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
console.log(`copied entry.png (${buf.length} bytes) to ${join(outDir, "entry.png")}`);
