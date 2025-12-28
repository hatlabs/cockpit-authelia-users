import * as esbuild from "esbuild";
import * as fs from "fs";

const production = process.argv.includes("--production");
const watch = process.argv.includes("--watch");

// Ensure dist directory exists
if (!fs.existsSync("dist")) {
  fs.mkdirSync("dist", { recursive: true });
}

// Copy static files
fs.copyFileSync("src/index.html", "dist/index.html");
fs.copyFileSync("src/manifest.json", "dist/manifest.json");

const context = await esbuild.context({
  entryPoints: ["src/authelia-users.tsx"],
  bundle: true,
  outdir: "dist",
  format: "esm",
  target: ["es2020"],
  sourcemap: !production,
  minify: production,
  external: [],
  loader: {
    ".woff": "file",
    ".woff2": "file",
  },
  define: {
    "process.env.NODE_ENV": production ? '"production"' : '"development"',
  },
});

if (watch) {
  await context.watch();
  console.log("Watching for changes...");
} else {
  await context.rebuild();
  await context.dispose();
  console.log("Build complete");
}
