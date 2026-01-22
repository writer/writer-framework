import { fileURLToPath, URL } from "url";
import { defineConfig, UserConfig, Plugin } from "vite";
import vue from "@vitejs/plugin-vue";
import writerPlugin from "./viteWriterPlugin";
import postcssAssignLayer from "postcss-assign-layer";

// Plugin to fix monaco-vscode-api internal path resolution
// The package's exports use wildcards: "./vscode/*" -> "./vscode/src/*.js"
// Rollup doesn't respect these, so we manually construct absolute paths
function fixMonacoVSCodePaths(): Plugin {
	return {
		name: "fix-monaco-vscode-paths",
		enforce: "pre", // Run before other plugins
		resolveId(source) {
			// Intercept: @codingame/monaco-vscode-api/vscode/vs/...
			// Transform to absolute path in node_modules
			if (source.startsWith("@codingame/monaco-vscode-api/vscode/vs/")) {
				// Extract the path after /vscode/vs/
				const pathAfterVs = source.slice(
					"@codingame/monaco-vscode-api/vscode/vs/".length,
				);

				// Construct absolute path: ../../node_modules (from src/ui/)
				const absolutePath = fileURLToPath(
					new URL(
						`../../node_modules/@codingame/monaco-vscode-api/vscode/src/vs/${pathAfterVs}.js`,
						import.meta.url,
					),
				);

				return {
					id: absolutePath,
					external: false,
				};
			}
			return null;
		},
	};
}

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",
	plugins: [vue(), writerPlugin(), fixMonacoVSCodePaths()],
	includeWriterComponentPath: false,
	define: {
		WRITER_LIVE_CCT: JSON.stringify("no"),
		WRITER_FRAMEWORK_VERSION: JSON.stringify(
			process.env.WRITER_FRAMEWORK_VERSION || "",
		),
	},
	css: {
		postcss: {
			plugins: [
				// we move all our CSS into Cascade layers to let the user's stylesheets have more priority
				postcssAssignLayer([
					{ include: "**/*/*.css", layerName: "wf" },
				]),
			],
		},
	},
	build: {
		outDir: "../writer/static",
		emptyOutDir: true,
		sourcemap: true,
	},
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
		dedupe: ["monaco-editor"],
	},
	test: {
		environment: "jsdom",
	},
	server: {
		host: "0.0.0.0",
		proxy: {
			"/api": {
				target: "http://127.0.0.1:5000",
				ws: true,
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
			"/static": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
			"/extensions": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
		},
	},
} as UserConfig);
