import {
	validatorCssClassname,
	validatorCssSize,
} from "@/constants/validators";
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinitionField,
} from "@/writerTypes";

export const accentColor: WriterComponentDefinitionField = {
	name: "Accent",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const primaryTextColor: WriterComponentDefinitionField = {
	name: "Primary text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const secondaryTextColor: WriterComponentDefinitionField = {
	name: "Secondary text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const emptinessColor: WriterComponentDefinitionField = {
	name: "Emptiness",
	desc: "Page background color",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const containerBackgroundColor: WriterComponentDefinitionField = {
	name: "Container background",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const containerShadow: WriterComponentDefinitionField = {
	name: "Container shadow",
	type: FieldType.Shadow,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const separatorColor: WriterComponentDefinitionField = {
	name: "Separator",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonColor: WriterComponentDefinitionField = {
	name: "Button",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonTextColor: WriterComponentDefinitionField = {
	name: "Button text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonShadow: WriterComponentDefinitionField = {
	name: "Button shadow",
	type: FieldType.Shadow,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const cssClasses: WriterComponentDefinitionField = {
	name: "Custom CSS classes",
	type: FieldType.Text,
	category: FieldCategory.Style,
	desc: "CSS classes, separated by spaces. You can define classes in custom stylesheets.",
	validator: validatorCssClassname,
};

export const contentWidth: WriterComponentDefinitionField = {
	name: "Content width",
	type: FieldType.Width,
	default: "100%",
	category: FieldCategory.Style,
	desc: "Configure content width using CSS units, e.g. 100px, 50%, 10vw, etc.",
	validator: validatorCssSize,
};

export const contentHAlign: WriterComponentDefinitionField = {
	name: "Content alignment (H)",
	type: FieldType.HAlign,
	default: "unset",
	category: FieldCategory.Style,
};

export const contentVAlign: WriterComponentDefinitionField = {
	name: "Content alignment (V)",
	type: FieldType.VAlign,
	default: "unset",
	category: FieldCategory.Style,
};

export const contentPadding: WriterComponentDefinitionField = {
	name: "Padding",
	type: FieldType.Padding,
	default: "0",
	category: FieldCategory.Style,
};

export function createBooleanField(
	params: Omit<WriterComponentDefinitionField, "type" | "validator"> & {
		default: "yes" | "no";
	},
): WriterComponentDefinitionField {
	return {
		...params,
		type: FieldType.Boolean,
		validator: {
			type: "boolean",
		},
	};
}

export function createEnableCopyButtonField(params: {
	default: "yes" | "no";
}): WriterComponentDefinitionField {
	return createBooleanField({
		name: "Enable copy button",
		desc: "Enable a copy button that lets users to copy the contents in this field to their clipboard",
		default: params.default,
		category: FieldCategory.Style,
	});
}

export const isCollapsible = createBooleanField({
	name: "Collapsible",
	default: "no",
	category: FieldCategory.Style,
});

export const startCollapsed = createBooleanField({
	name: "Start collapsed",
	category: FieldCategory.Style,
	default: "no",
	desc: "Only applied when the component is collapsible.",
});
