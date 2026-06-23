import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  ".."
);
const source = path.join(frontendRoot, ".env.example");
const destination = path.join(frontendRoot, ".env.local");

if (!fs.existsSync(source)) {
  console.error("Missing frontend/.env.example.");
  process.exit(1);
}

if (fs.existsSync(destination)) {
  console.log("frontend/.env.local already exists; no changes made.");
} else {
  fs.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
  console.log("Created frontend/.env.local from .env.example.");
}
