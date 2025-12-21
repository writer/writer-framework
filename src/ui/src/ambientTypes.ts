import { WriterComponentDefinition, WriterAppConfig } from "./writerTypes";

declare module "marked";
declare module "vue" {
	interface ComponentCustomOptions {
		writer?: WriterComponentDefinition;
	}
}

declare global {
	interface Window {
		__WRITER_APP_CONFIG__?: WriterAppConfig | string;
	}
}

export {};
