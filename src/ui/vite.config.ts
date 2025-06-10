import { fileURLToPath, URL } from "url";
import { defineConfig, UserConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import writerPlugin from "./viteWriterPlugin";
import postcssAssignLayer from "postcss-assign-layer";

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",
	plugins: [vue(), writerPlugin()],
	includeWriterComponentPath: false,
	define: {
		WRITER_LIVE_CCT: JSON.stringify("no"),
		WRITER_FRAMEWORK_VERSION: JSON.stringify(process.env.WRITER_FRAMEWORK_VERSION || ""),
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
	},
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
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
