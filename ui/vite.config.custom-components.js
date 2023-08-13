import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

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
	plugins: [vue()],
	publicDir: false,
	build: {
		lib: {
			entry: ["./src/custom_components/index.js"],
			formats: ["umd"],
			name: "StreamsyncCustomComponentTemplates",
			fileName: "templates",
		},
		rollupOptions: {
			external: ["vue", injectionKeysPath],
			input: {
				a: 'src/custom_components/index.js',
			},	
			output: {
				globals: {
					vue: "vue",
					[injectionKeysPath]: "injectionKeys"
				}
			},
		},
		outDir: "custom_components_dist",
		emptyOutDir: true,
	},
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url))
		},
	}
});
