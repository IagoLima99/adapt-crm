import { readFileSync, writeFileSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

/**
 * @param {string} version
 * @param {string} commit
 */
export function createBuildMetadata(version, commit) {
  if (!version.trim() || !commit.trim()) {
    throw new Error("Build version and commit are required.");
  }

  return { version, commit };
}

async function main() {
  const outputPath = process.argv[2];
  if (!outputPath) {
    throw new Error("Output path is required.");
  }

  const packagePath = fileURLToPath(new URL("../../../package.json", import.meta.url));
  const packageJson = JSON.parse(readFileSync(packagePath, "utf8"));
  const commit = process.argv[3] ?? process.env.GITHUB_SHA ?? "";
  const metadata = createBuildMetadata(packageJson.version, commit);
  const resolvedOutputPath = resolve(outputPath);

  await mkdir(dirname(resolvedOutputPath), { recursive: true });
  writeFileSync(resolvedOutputPath, `${JSON.stringify(metadata)}\n`, "utf8");
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : undefined;
if (import.meta.url === invokedPath) {
  await main();
}
