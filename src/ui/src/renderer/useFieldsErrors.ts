import type {
	Core,
	InstancePath,
	SecretsManager,
	WriterComponentDefinitionField,
} from "@/writerTypes";
import { computed, ComputedRef } from "vue";
import { TEMPLATE_REGEX, useEvaluator } from "./useEvaluator";
import {
	buildJsonSchemaForEnum,
	getJsonSchemaValidator,
	ValidatorCustomFormat,
	validatorCustomSchemas,
} from "@/constants/validators";
import type { ErrorObject } from "ajv";

export function useFieldsErrors(
	wf: Core,
	instancePath: ComputedRef<InstancePath>,
	secretsManager?: SecretsManager,
) {
	const { getEvaluatedFields } = useEvaluator(wf, secretsManager);

	function includesTemplate(template: string) {
		return Boolean(TEMPLATE_REGEX.exec(template));
	}

	const componentId = computed(() => instancePath.value.at(-1)?.componentId);

	const component = computed(() => {
		if (componentId.value === undefined) return undefined;
		return wf.getComponentById(componentId.value);
	});

	const componentFields = computed(() => {
		return wf.getComponentDefinition(component.value.type).fields ?? {};
	});

	const evaluatedFields = computed(() =>
		getEvaluatedFields(instancePath.value),
	);

	return computed(() => {
		return Object.entries(componentFields.value).reduce(
			(acc, [key, definition]) => {
				// skip validation if the value contains a template var
				const plainValue = component.value.content?.[key] ?? "";
				if (includesTemplate(plainValue)) return acc;

				const value = evaluatedFields.value[key].value;

				acc[key] = computeFieldErrors(
					wf,
					componentId.value,
					definition,
					value,
				);
				return acc;
			},
			{},
		);
	});
}

function computeFieldErrors(
	wf: Core,
	componentId: string,
	field: WriterComponentDefinitionField,
	value: unknown,
) {
	let schema = field.validator;

	if (
		schema === undefined &&
		typeof field.options === "object" &&
		field.options !== null &&
		Object.keys(field.options).length > 0
	) {
		// set an automatic enum schema for options fields
		schema = buildJsonSchemaForEnum(Object.keys(field.options));
	} else if (typeof schema === "function") {
		schema = schema(wf, componentId);
	}

	if (schema === undefined) return undefined;

	const validate = getJsonSchemaValidator(schema);

	const valid = validate(value);

	if (valid || validate.errors === undefined) return undefined;

	return formatAjvErrors(validate.errors);
}

function formatAjvError(error: ErrorObject): string {
	if (
		error.keyword === "format" &&
		Object.values(ValidatorCustomFormat).includes(error.params.format)
	) {
		return validatorCustomSchemas[error.params.format].errorMessage;
	}

	let message = "";

	if (error.instancePath) {
		message += `${error.instancePath} `;
	}

	message += error.message;

	if (Array.isArray(error.params?.allowedValues)) {
		message += `: ${error.params.allowedValues.join(", ")}`;
	}

	return message;
}

function formatAjvErrors(errors: ErrorObject[]): string {
	return errors.map(formatAjvError).join("\n");
}
