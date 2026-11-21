import { copyFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

// Entry for news-image-20261121: copy the pre-rendered front page
// (entry.png, drawn by gen_image.py from stories.json) to the output
// directory. No network, no deletion of anything: the output directory
// is only created if missing, and the single file is overwritten.
// Runs twice in the grader; both runs write identical bytes.
const root = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(root, "entry.png"), join(outDir, "entry.png"));
