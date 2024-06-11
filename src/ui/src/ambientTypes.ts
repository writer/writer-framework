import { WriterComponentDefinition } from "./writerTypes";

declare module "marked";
declare module "vue" {
	interface ComponentCustomOptions {
		writer?: WriterComponentDefinition;
	}
}

export {};
