import type { Component as VueComponent } from "vue";
import { generateCore } from "./core";
import { generateBuilderManager } from "./builder/builderManager";
import type { SchemaObject } from "ajv";
import type { useNotesManager } from "./core/useNotesManager";

export type Core = ReturnType<typeof generateCore>;

type ComponentId = string;

/**
 * Basic building block of applications.
 * Multiple instances of a single component can exists. For example, via Repeater.
 */

type VisibleField = {
	expression: boolean | string; // True | False | 'custom'
	binding: string; // variable binding when expression is custom
	reversed: boolean;
};

export type Component = {
	id: ComponentId;
	parentId: string;
	type: string;
	position: number;
	content: Record<string, string>;
	isCodeManaged?: boolean;
	handlers?: Record<string, string>;
	visible?: VisibleField;
	binding?: {
		eventType: string;
		stateRef: string;
	};
	x?: number;
	y?: number;
	outs?: {
		outId: string;
		toNodeId: string;
	}[];
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
export type WriterComponentDefinitionField = {
	/** Display name */
	name: string;
	/** Initial value */
	init?: string;
	/** Description */
	desc?: string;
	/** Value used if the field is empty, e.g. "(No text)" */
	default?: string;
	/** Which control (text, textarea, etc) to use if not the default for the type */
	control?: FieldControl;
	options?:
	| Record<string, string>
	| string // For predefined functions
	| ((wf?: Core, componentId?: ComponentId) => Record<string, string>); // List of values to be provided as autocomplete options
	/** Data type for the field */
	type: FieldType;
	/** Category (Layout, Content, etc) */
	category?: FieldCategory;
	/** Use the value of this field as a CSS variable */
	applyStyleVariable?: boolean;
	validator?: SchemaObject;
};

export type WriterComponentDefinitionEvent = {
	/** Description */
	desc?: string;
	/** Stub method for the event */
	stub?: string;
	/** Whether this event is used for value binding */
	bindable?: boolean;
	/** The payload that will be given  */
	eventPayloadExample?: string | boolean | object;
};

export type WriterComponentDefinition = {
	name: string; // Display name for the component
	description: string; // Short description
	docs?: string; // Collapsible mini-docs
	toolkit?: "core" | "blueprints";
	deprecated?: boolean;
	category?: string; // Category (Layout, Content, etc)
	allowedChildrenTypes?: (string | "*" | "inherit")[]; // Which component types are allowed inside (if any)
	allowedParentTypes?: string[]; // Which component types can contain this type of component
	slot?: string; // In which slot component should render when "*" is used it will render in all slots
	fields?: Record<
		string, // Id for the field
		WriterComponentDefinitionField
	>;
	events?: Record<
		string, // Event type
		WriterComponentDefinitionEvent
	>;
	previewField?: string; // Which field to use for previewing in the Component Tree
	positionless?: boolean; // Whether this type of component is positionless (like Sidebar)
	outs?: Record<
		string,
		{
			name: string;
			description: string;
			style: string;
			field?: keyof WriterComponentDefinition["fields"];
		}
	>;
};

export type BuilderManager = ReturnType<typeof generateBuilderManager>;

export type NotesManager = ReturnType<typeof useNotesManager>;

export const enum FieldType {
	Text = "Text",
	Boolean = "Boolean",
	KeyValue = "Key-Value",
	Color = "Color",
	Shadow = "Shadow",
	Number = "Number",
	Object = "Object",
	IdKey = "Identifying Key",
	Width = "Width",
	HAlign = "Align (H)",
	VAlign = "Align (V)",
	Padding = "Padding",
	Tools = "Tools",
	ComponentPicker = "Component",
	Code = "Code",
	BlueprintKey = "Blueprint Key",
	Handler = "Handler",
	WriterGraphId = "Graph Id",
	WriterAppId = "App Id",
	WriterModelId = "Model Id",
	ComponentId = "Component Id",
	ComponentEventType = "Component Event Type",
}

export const enum FieldCategory {
	General = "General",
	Style = "Style",
	Tools = "Tools",
}

/**
 * Used to specify the field control if it's different from the default for the FieldType.
 */
export const enum FieldControl {
	Text = "Text",
	Textarea = "Textarea",
}

export type ComponentMap = Record<Component["id"], Component>;

/**
 * Unit of data for non-state-mutation communications between frontend and backend.
 */
export type MailItem = { type: string; payload: Record<string, string> };

export type UserFunction = { name: string; args: string[] };

export type AbstractTemplate = {
	baseType: string;
	writer: WriterComponentDefinition;
};

export type TemplateMap = Record<string, VueComponent>;

export type SourceFilesFile = {
	type: "file";
	complete?: boolean;
	content: string;
};
export type SourceFilesBinary = {
	type: "binary";
	uploading?: boolean;
};

export type SourceFilesDirectory = {
	type: "directory";
	children: Record<string, SourceFiles>;
};

/**
 * Represent a file tree as an object with:
 *
 * - the key representing the filename
 * - the content as a string for a readable text file, or as a recursive `SourceFiles` if it's a directory
 *
 * @example
 * ```json
 * { "type": "directory", "children": { "main.py": { "type": "file", "content": "print('hello')", "complete": true } } }
 * ```
 */
export type SourceFiles =
	| SourceFilesDirectory
	| SourceFilesFile
	| SourceFilesBinary;

export type WriterGraph = {
	id: string;
	name: string;
	description: string;
	file_status: {
		in_progress: number;
		completed: number;
		failed: number;
		total: number;
	};
	type: "connector" | "manual";
	organization_id?: string;
};

export type WriterApplication = {
	id: string;
	name: string;
	type: string;
	status: string;
	organization_id?: string;
};

export type UserCollaborationPing = {
	action: "join" | "select" | "leave" | "auto";
	userId: string;
	time: Date;
	componentIds?: Component["id"][];
	x?: number;
	y?: number;
};

export type WriterModel = {
	id: string;
	name: string;
};
