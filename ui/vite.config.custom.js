import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import monacoEditorPlugin from "vite-plugin-monaco-editor";

/*
injectionKeys is externalised so that it can be linked at runtime.
Otherwise, new, independent instances of Symbol would be created, for which
nothing would be provided.
*/
const injectionKeysPath = fileURLToPath(
	new URL("src/injectionKeys.ts", import.meta.url),
);

export default defineConfig({
	base: "./",
	plugins: [vue(), { ...monacoEditorPlugin({}), apply: "serve" }],
	define: {
		STREAMSYNC_LIVE_CCT: JSON.stringify("yes"),
	},
	publicDir: false,
	build: {
		lib: {
			entry: ["./src/custom_components"],
			formats: ["umd"],
			name: "StreamsyncCustomComponentTemplates",
			fileName: "templates",
		},
		rollupOptions: {
			external: ["vue", injectionKeysPath],
			output: {
				globals: {
					vue: "vue",
					[injectionKeysPath]: "injectionKeys",
				},
			},
		},
		outDir: "custom_components_dist",
		emptyOutDir: true,
	},
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
	},
	server: {
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
});
