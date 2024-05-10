import path from "path";

import { defineConfig, UserConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import streamsyncPlugin from "./viteStreamsyncPlugin";

export default defineConfig({
	base: "./",
	plugins: [
		vue(),
		streamsyncPlugin(),
	],
	includeStreamsyncComponentPath: false,
	define: {
		STREAMSYNC_LIVE_CCT: JSON.stringify("yes"),
	},
	publicDir: false,
	build: {
		lib: {
			entry: ["./src/custom_components"],
			formats: ["umd"],
			name: "StreamsyncCustomComponentTemplates",
			fileName: (format, entryalias: string): string => {
				/*
				The umd file is generated with a cjs extension since transforming the streamsync package into a module
				(https://github.com/streamsync-cloud/streamsync/issues/405).

				We use the generated file inside a browser, not a nodejs application.
				The cjs extension is not adapted. We implement our own name builder.
				 */
				return "templates.umd.js";
			},
		},
		rollupOptions: {
			external: ["vue", "../injectionKeys"],
			output: {
				globals: {
					vue: "vue",
					[path.resolve("src/injectionKeys")]: "injectionKeys",
				},
			},
		},
		outDir: "custom_components_dist",
		emptyOutDir: true,
	},
	resolve: {
		alias: {
			"@": path.resolve("src"),
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
} as UserConfig);
