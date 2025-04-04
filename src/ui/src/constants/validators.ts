import injectionKeys from "@/injectionKeys";
import Ajv, { Format, type SchemaObject } from "ajv";
import { inject } from "vue";

export enum ValidatorCustomFormat {
	/**
	 * Check that the blueprint key is existing
	 */
	WriterBlueprintKey = "writer#blueprintKey",
	/**
	 * Check it's a white spaced list of CSS classes
	 */
	CssClassnames = "cssClassnames",
	CssSize = "cssSize",
	Uri = "uri",
	Uuid = "uuid",
}

/**
 * We use an URL to define the `$id` of the schema. The URL doesn't have to exist, it's only used for caching.
 * @see <https://ajv.js.org/guide/managing-schemas.html#cache-key-schema-vs-key-vs-id>
 */
function generateSchemaId(path: string) {
	return `https://dev.writer.com/framework/${encodeURIComponent(path)}.json`;
}

export function buildJsonSchemaForEnum(options: string[]): SchemaObject {
	return {
		$id: generateSchemaId(options.join(",")),
		type: "string",
		enum: options,
	};
}

export function buildJsonSchemaForNumberBetween(
	minimum: number,
	maximum: number,
): SchemaObject {
	return {
		$id: generateSchemaId(`between-${minimum}-${maximum}`),
		type: "number",
		minimum,
		maximum,
	};
}

export const validatorCssClassname: SchemaObject = {
	$id: generateSchemaId("cssClassname"),
	type: "string",
	format: ValidatorCustomFormat.CssClassnames,
};

export const validatorCssSize: SchemaObject = {
	$id: generateSchemaId("cssSize"),
	type: "string",
	format: ValidatorCustomFormat.CssSize,
};

export const validatorArrayOfString: SchemaObject = {
	$id: generateSchemaId("arrayOfString"),
	type: "array",
	items: { type: "string" },
};

export const validatorGpsLat = buildJsonSchemaForNumberBetween(-90, 90);

export const validatorGpsLng = buildJsonSchemaForNumberBetween(-180, 180);

export const validatorGpsMarker: SchemaObject = {
	$id: generateSchemaId("gpsMarker"),
	type: "object",
	properties: {
		name: {
			type: "string",
		},
		lat: validatorGpsLat,
		lng: validatorGpsLng,
	},
	required: ["lat", "lng", "name"],
	additionalProperties: false,
};

export const validatorGpsMarkers: SchemaObject = {
	$id: generateSchemaId("gpsMarkers"),
	type: "array",
	items: validatorGpsMarker,
};

export const validatorObjectRecordNotNested: SchemaObject = {
	$id: generateSchemaId("objectRecordNotNested"),
	type: "object",
	patternProperties: {
		"^.*$": {
			type: ["string", "number", "boolean"],
		},
	},
	additionalProperties: true,
};

export const validatorAnotatedText: SchemaObject = {
	$id: generateSchemaId("anotatedText"),
	type: "array",
	items: {
		oneOf: [
			{ type: "string" },
			{
				type: "array",
				items: { type: "string" },
			},
		],
	},
};

export const validatorRepeaterObject: SchemaObject = {
	$id: generateSchemaId("repeaterObject"),
	oneOf: [
		{
			type: "object",
			patternProperties: {
				"^.*$": {
					type: "object",
				},
			},
			additionalProperties: true,
		},
		{
			type: "array",
			items: {
				type: "object",
			},
		},
	],
};

export const validatorChatBotMessage: SchemaObject = {
	$id: generateSchemaId("chatBotMessage"),
	type: "object",
	properties: {
		role: { type: "string" },
		content: { type: "string" },
		tools: {
			type: "array",
			items: {
				type: "object",
				properties: {
					type: {
						type: "string",
					},
				},
				required: ["type"],
				additionalProperties: true,
			},
		},
	},
	required: ["role"],
	additionalProperties: true,
};

export const validatorChatBotMessages: SchemaObject = {
	$id: generateSchemaId("chatBotMessages"),
	type: "array",
	items: validatorChatBotMessage,
};

export const validatorPositiveNumber: SchemaObject = {
	$id: generateSchemaId("positiveNumber"),
	type: "number",
	minimum: 0,
};

export const validatorUri: SchemaObject = {
	$id: generateSchemaId("uri"),
	type: "string",
	format: "uri",
};

export const ajv = new Ajv({
	strict: true,
	allowUnionTypes: true,
});

/**
 * Compile and cache schema on demand
 */
export function getJsonSchemaValidator(schema: SchemaObject) {
	if (schema?.$id === undefined) return ajv.compile(schema);
	return ajv.getSchema(schema.$id) || ajv.compile(schema);
}

// custom formats

export const validatorCustomSchemas: Record<
	ValidatorCustomFormat,
	{ format: Format; errorMessage: string }
> = {
	[ValidatorCustomFormat.Uri]: {
		format: /^(?:[a-z][a-z0-9+\-.]*:)(?:\/?\/)?[^\s]*$/i,
		errorMessage: "must be a valid URL",
	},
	[ValidatorCustomFormat.Uuid]: {
		format: /^(?:urn:uuid:)?[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i,
		errorMessage: "must be a valid UUID",
	},
	[ValidatorCustomFormat.CssClassnames]: {
		format: /(^\s*[a-zA-Z_][-\w]*(\s+[a-zA-Z_][-\w]*)*\s*$)|(^$)/,
		errorMessage: "must be a valid list of CSS classes separated by spaces",
	},
	[ValidatorCustomFormat.CssSize]: {
		format: /(^([+-]?\d*\.?\d+)(px|em|%|vh|vw|rem|pt|pc|in|cm|mm|ex|ch|vmin|vmax|fr)$)|(^$)/,
		errorMessage: "must be a valid CSS size",
	},
	[ValidatorCustomFormat.WriterBlueprintKey]: {
		format: {
			type: "string",
			validate: (blueprintKey) => {
				const core = inject(injectionKeys.core);
				if (!core) return true;
				const blueprintKeys = core
					.getComponents()
					.filter((c) => c.type === "blueprints_blueprint")
					.map((c) => c.content.key);

				return blueprintKeys.includes(blueprintKey);
			},
		},
		errorMessage: "must correspond to an existing blueprint key",
	},
};

Object.entries(validatorCustomSchemas).map(([name, definition]) =>
	ajv.addFormat(name, definition.format),
);
