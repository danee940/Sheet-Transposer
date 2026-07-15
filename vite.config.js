import { resolve } from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  root: "src/js",
  build: {
    manifest: "manifest.json",
    outDir: resolve(__dirname, "src/static/js"),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "src/js/main.js"),
        landing: resolve(__dirname, "src/js/landing.js"),
      },
      output: {
        entryFileNames: "[name].[hash].js",
        chunkFileNames: "[name].[hash].js",
        assetFileNames: "[name].[hash][extname]",
      },
    },
  },
  test: {
    root: resolve(__dirname),
    environment: "jsdom",
    include: ["src/js/**/*.test.js"],
  },
});
