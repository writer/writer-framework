import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import monacoEditorPlugin from "vite-plugin-monaco-editor";

const streamsyncComponentsDocs = () => {
	let config;

	return {
		name: "vue-docs-ignore",
		configResolved(resolvedConfig) {
			config = resolvedConfig;
		},
		transform(code, id) {
			if (/vue&type=docs/.test(id)) {
				const docs = code
					.replace(/'/g, "\\'")
					.replace(/\n/g, "\\n")
					.trim()
					.replace(/^(\\n|\\t|[ \s])*/g, "")
					.replace(/(\\n|\\t|[ \s])*$/g, "");
				return `export default Comp => {
					if(!Comp.streamsync) return;
					Comp.streamsync.docs = '${docs}';
				}`;
			}
			if (/\.vue$/.test(id)) {
				if (config.includeStreamsyncComponentPath === false) return;
				const fileRef = id.replace(__dirname, "");
				return `${code}
					if(_sfc_main.streamsync) _sfc_main.streamsync.fileRef = '${fileRef}';
				`;
			}
		},
	};
};

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",
	plugins: [vue(), monacoEditorPlugin({}), streamsyncComponentsDocs()],
	includeStreamsyncComponentPath: false,
	define: {
		STREAMSYNC_LIVE_CCT: JSON.stringify("no"),
	},
	build: {
		outDir: "../src/streamsync/static",
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
