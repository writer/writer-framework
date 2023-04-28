import {
	Component,
	Core,
	StreamsyncComponentDefinition,
} from "./streamsyncTypes";

declare module "marked";
declare module "vue" {
	interface ComponentCustomProperties {
		streamsync: Core;
		componentId: Component["id"];
		fields: Record<string, any>;
		formValue: string;
	}

	interface ComponentCustomOptions {
		streamsync?: StreamsyncComponentDefinition;
	}
}

export {};
