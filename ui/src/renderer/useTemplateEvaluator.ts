import { ComputedRef, computed } from "vue";
import { Component, Core, FieldType, InstancePath } from "../streamsyncTypes";

export function useTemplateEvaluator(ss: Core) {
	const templateRegex = /[\\]?@{([^}]*)}/g;

	function getContextData(instancePath: InstancePath) {
		const context = {};

		for (let i = 0; i < instancePath.length - 1; i++) {
			const pathItem = instancePath[i];
			const { componentId } = pathItem;
			const { type } = ss.getComponentById(componentId);
			if (type !== "repeater") continue;
			if (i + 1 >= instancePath.length) continue;
			const repeaterInstancePath = instancePath.slice(0, i + 1);
			const nextInstancePath = instancePath.slice(0, i + 2);
			const { instanceNumber } = nextInstancePath.at(-1);

			const repeaterObject = evaluateField(
				repeaterInstancePath,
				"repeaterObject"
			);

			if (!repeaterObject) continue;

			const repeaterEntries = Object.entries(repeaterObject);
			const keyVariable = evaluateField(
				repeaterInstancePath,
				"keyVariable"
			);
			const valueVariable = evaluateField(
				repeaterInstancePath,
				"valueVariable"
			);

			context[keyVariable] = repeaterEntries[instanceNumber]?.[0];
			context[valueVariable] = repeaterEntries[instanceNumber]?.[1];
		}

		return context;
	}

	function evaluateTemplate(
		template: string,
		instancePath: InstancePath
	): string {
		if (template === undefined || template === null) return "";

		const contextData = getContextData(instancePath);

		const evaluatedTemplate = template.replace(
			templateRegex,
			(match, captured) => {
				if (match.charAt(0) == "\\") return match.substring(1); // Escaped @, don't evaluate, return without \

				const expr = captured.trim();
				if (!expr) return "";

				const exprValue = ss.evaluateExpression(expr, contextData);

				if (typeof exprValue == "undefined") {
					return "";
				} else if (typeof exprValue == "object") {
					return JSON.stringify(exprValue);
				}

				return exprValue;
			}
		);

		return evaluatedTemplate;
	}

	function getEvaluatedFields(
		instancePath: InstancePath
	): Record<string, ComputedRef<any>> {
		const { componentId } = instancePath.at(-1);
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const evaluatedFields: Record<string, ComputedRef<any>> = {};
		const { fields } = ss.getComponentDefinition(component.type);
		if (!fields) return;
		Object.keys(fields).forEach((fieldKey) => {
			evaluatedFields[fieldKey] = computed(() => evaluateField(instancePath, fieldKey));
		});

		return evaluatedFields;
	}

	function evaluateField(instancePath: InstancePath, fieldKey: string) {
		const { componentId } = instancePath.at(-1);
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const { fields } = ss.getComponentDefinition(component.type);
		const contentValue = component.content?.[fieldKey];
		const defaultValue = fields[fieldKey].default;
		const evaluated = evaluateTemplate(contentValue, instancePath);
		const fieldType = fields[fieldKey].type;
		if (fieldType == FieldType.Object || fieldType == FieldType.KeyValue) {
			if (!evaluated) {
				return JSON.parse(defaultValue) ?? null;
			}
			if (typeof evaluated !== "string") return evaluated;
			let parsedValue: any;
			try {
				parsedValue = JSON.parse(evaluated);
			} catch {
				return JSON.parse(defaultValue) ?? null;
			}
			return parsedValue;
		} else if (fieldType == FieldType.Number) {
			const n = parseFloat(evaluated);
			if (typeof n === undefined || Number.isNaN(n))
				return parseFloat(defaultValue ?? "0");
			return n;
		} else if (fieldType == FieldType.IdKey) {
			return contentValue;
		} else {
			const isValueEmpty =
				typeof evaluated == "undefined" ||
				evaluated === null ||
				evaluated === "";
			if (isValueEmpty) return defaultValue ?? "";
			return evaluated;
		}
	}

	/**
	 * Check the visibility of a component. If an instance path is specified, context is evaluated.
	 *
	 * @param componentId The id of the component.
	 * @param instancePath The specific instance of the component to be evaluated.
	 * @returns Visibility status.
	 */
	function isComponentVisible(
		componentId: Component["id"],
		instancePath?: InstancePath
	): boolean {
		let contextData:Record<string, any>;
		const component = ss.getComponentById(componentId);
		if (!component) return;

		if (typeof component.visible === "undefined") return true;
		if (component.visible === true) return true;
		if (component.visible === false) return false;
		if (instancePath) {
			contextData = getContextData(instancePath);
		}
		const evaluated = ss.evaluateExpression(component.visible as string, contextData);
		return !!evaluated;
	}

	return {
		getEvaluatedFields,
		isComponentVisible
	};
}
