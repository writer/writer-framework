import { generateCore } from "./core";
import { generateBuilderManager } from "./builder/builderManager";

/**
 * Basic building block of applications.
 * Multiple instances of a single component can exists. For example, via Repeater.
 */

export type Component = {
	id: string;
	parentId: string;
	type: string;
	position: number;
	content: Record<string, string>;
	handlers?: Record<string, string>;
	visible?: boolean | string;
	binding?: {
		eventType: string;
		stateRef: string;
	};
};

/**
 * Identifies a unique instance of a Component.
 */

export type InstancePathItem = {
	componentId: Component["id"];
	instanceNumber: number;
};

/**
 * Details the full path, including all ancestors, of a unique instance of a Component.
 */

export type InstancePath = InstancePathItem[];

/**
 * Defines component structure and behaviour. Included in Component templates.
 */

export type StreamsyncComponentDefinition = {
	name: string;
	description: string;
	docs?: string;
	category?: string;
	allowedChildrenTypes?: (string | "*" | "inherit")[];
	allowedParentTypes?: string[];
	fields?: Record<
		string,
		{
			name: string;
			init?: string;
			desc?: string;
			default?: string;
			control?: string;
			options?: Record<string, string>;
			type: FieldType;
			category?: FieldCategory;
			applyStyleVariable?: boolean;
		}
	>;
	events?: Record<
		string,
		{
			desc?: string;
			stub?: string;
			bindable?: boolean;
		}
	>;
	previewField?: string;
	positionless?: boolean;
};

export type Core = ReturnType<typeof generateCore>;
export type BuilderManager = ReturnType<typeof generateBuilderManager>;

export const enum ClipboardOperation {
	Cut = "cut",
	Copy = "copy",
}

export const enum FieldType {
	Text = "Text",
	KeyValue = "Key-Value",
	Color = "Color",
	Shadow = "Shadow",
	Number = "Number",
	Object = "Object",
	IdKey = "Identifying Key",
}

export const enum FieldCategory {
	General = "General",
	Style = "Style",
}

export type ComponentMap = Record<Component["id"], Component>;

/**
 * Unit of data for non-state-mutation communications between frontend and backend.
 */

export type MailItem = { type: string; payload: Record<string, string> };
