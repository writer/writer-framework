import { ComputedRef, computed } from "vue";
import { Component, Core, FieldType, InstancePath } from "@/writerTypes";
import { flattenInstancePath } from "./instancePath";

export function useEvaluator(wf: Core) {
	function getEvaluatedBinding(
		instancePath?: InstancePath,
	): ComputedRef<any> {
		const flattenedInstancePath = flattenInstancePath(instancePath);
		return computed(
			() =>
				wf.evaluatedTree.value?.[flattenedInstancePath]?.["binding"]?.[
					"reference"
				],
		);
	}

	function getEvaluatedFields(
		instancePath: InstancePath,
	): Record<string, ComputedRef<any>> {
		const { componentId } = instancePath.at(-1);
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const evaluatedFields: Record<string, ComputedRef<any>> = {};
		const { fields } = wf.getComponentDefinition(component.type);
		if (!fields) return;
		Object.keys(fields).forEach((fieldKey) => {
			evaluatedFields[fieldKey] = computed(() =>
				evaluateField(instancePath, fieldKey),
			);
		});

		return evaluatedFields;
	}

	function evaluateField(instancePath: InstancePath, fieldKey: string) {
		const { componentId } = instancePath.at(-1);
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const { fields } = wf.getComponentDefinition(component.type);
		const contentValue = component.content?.[fieldKey];
		const defaultValue = fields[fieldKey].default;
		const flattenedInstancePath = flattenInstancePath(instancePath);
		const evaluated =
			(wf.evaluatedTree.value?.[flattenedInstancePath]?.["content"]?.[
				fieldKey
			] ??
				contentValue) ||
			defaultValue;
		const fieldType = fields[fieldKey].type;
		const isValueEmpty =
			typeof evaluated == "undefined" ||
			evaluated === null ||
			evaluated === "";
		if (
			fieldType == FieldType.Object ||
			fieldType == FieldType.KeyValue ||
			fieldType == FieldType.Tools
		) {
			if (!evaluated) {
				return JSON.parse(defaultValue ?? null);
			}
			if (typeof evaluated !== "string") return evaluated;
			let parsedValue: any;
			try {
				parsedValue = JSON.parse(evaluated);
			} catch {
				return JSON.parse(defaultValue ?? null);
			}
			return parsedValue;
		} else if (fieldType == FieldType.Number) {
			const floatDefaultValue =
				defaultValue === null ? null : parseFloat(defaultValue);
			if (isValueEmpty) return floatDefaultValue ?? null;

			const n = parseFloat(evaluated);
			if (typeof n === "undefined" || Number.isNaN(n))
				return floatDefaultValue ?? null;
			return n;
		} else if (fieldType == FieldType.IdKey) {
			return contentValue;
		} else {
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
		instancePath?: InstancePath,
	): boolean {
		const component = wf.getComponentById(componentId);
		if (!component) return;

		if (typeof component.visible === "undefined") return true;
		if (component.visible.expression === true) return true;
		if (component.visible.expression === false) return false;
		// const evaluated = evaluateExpression(
		// 	component.visible.binding as string,
		// 	instancePath,
		// );

		return component.visible.reversed === true ? !evaluated : !!evaluated;
	}

	return {
		getEvaluatedFields,
		isComponentVisible,
		getEvaluatedBinding,
	};
}
