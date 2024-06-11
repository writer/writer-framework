import { ResolvedConfig, Plugin } from "vite";

type WriterPluginConfig = ResolvedConfig & {
	includeWriterComponentPath?: boolean;
};

export default (): Plugin => {
	let config: WriterPluginConfig;

	return {
		name: "writer-plugin",
		configResolved(resolvedConfig) {
			config = resolvedConfig as WriterPluginConfig;
		},
		transform(code: string, id: string) {
			if (/vue&type=docs/.test(id)) {
				const docs = code
					.replaceAll(/'/g, "\\'")
					.replaceAll(/\n/g, "\\n")
					.replaceAll(/\r/g, "\\r")
					.trim()
					.replace(/^(\\n|\\t|[ \s])*/, "")
					.replace(/(\\n|\\t|[ \s])*$/, "");
				return `export default Comp => {
					if(!Comp.writer) return;
					Comp.writer.docs = '${docs}';
				}`;
			}
			if (/\.vue$/.test(id)) {
				if (config.includeWriterComponentPath === false) return;
				const fileRef = id.replace(`${__dirname}/`, "");
				return `${code}
					if(_sfc_main.writer) _sfc_main.writer.fileRef = '${fileRef}';
				`;
			}
		},
	};
};
