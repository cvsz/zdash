import { readFile, writeFile, access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const blocked = [".env", ".env.local", ".env.public-demo.local"];
for (const name of blocked) {
  try {
    await access(join(root, name));
    throw new Error(`Public demo build blocked: remove private ${name} from this worktree first.`);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      continue;
    }
    throw error;
  }
}

const expectedKeys = new Set([
  "VITE_PUBLIC_DEMO",
  "VITE_APP_ENV",
  "VITE_AUTH_ENABLED",
  "VITE_ENABLE_MOCK_FALLBACK",
  "VITE_REALTIME_ENABLED",
  "VITE_API_BASE_URL",
  "VITE_WS_BASE_URL",
  "VITE_SHOW_SAFETY_BANNERS",
]);
for (const key of Object.keys(process.env)) {
  if (key.startsWith("VITE_") && !expectedKeys.has(key)) {
    throw new Error(`Public demo build blocked: unexpected ${key} in process environment.`);
  }
}
const template = await readFile(join(root, "public-demo.env.example"), "utf8");
if (!/^VITE_PUBLIC_DEMO=true$/m.test(template) || !/^VITE_AUTH_ENABLED=false$/m.test(template)) {
  throw new Error("Public demo template is missing its mandatory isolation flags.");
}
for (const entry of template.split("\n")) {
  const key = entry.split("=")[0].trim();
  if (key.startsWith("VITE_") && process.env[key] && process.env[key] !== entry.slice(key.length + 1)) {
    throw new Error(`Public demo build blocked: environment overrides ${key}.`);
  }
}
await writeFile(join(root, ".env.public-demo"), template, { encoding: "utf8", mode: 0o600 });
console.log("Prepared isolated public-demo Vite configuration (no secrets).");
