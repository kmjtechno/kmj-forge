import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, test } from "vitest";

const desktopRoot = fileURLToPath(new URL("../", import.meta.url));

const requiredFiles = [
  "src/App.tsx",
  "src/bridge.ts",
  "src/main.tsx",
  "src/styles.css",
  "index.html",
  "src-tauri/Cargo.toml",
  "src-tauri/tauri.conf.json",
  "src-tauri/src/lib.rs",
  "src-tauri/src/main.rs",
];

describe("Forge Desktop Alpha scaffold", () => {
  test.each(requiredFiles)("provides %s", (relativePath) => {
    expect(existsSync(`${desktopRoot}${relativePath}`)).toBe(true);
  });
});
