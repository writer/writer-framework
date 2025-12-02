import { generateCore } from "@/core";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { Component, Core } from "@/writerTypes";
import { computed, ComputedRef, unref } from "vue";

/**
 * Gets the display name for a shared blueprint by looking up its source blueprint.
 * Returns the source blueprint's key (name), or null if not found.
 */
export function getSourceBlueprintName(
	wf: Core,
	component: Component,
): string | null {
	if (component?.type !== "shared_blueprint") return null;
	const sourceBlueprintId = component.content?.sourceBlueprintId;
	if (!sourceBlueprintId) return null;
	const sourceBlueprint = wf.getComponentById(sourceBlueprintId);
	return sourceBlueprint?.content?.key || null;
}

export function useComponentDescription(
	wf: ReturnType<typeof generateCore>,
	component: Component | ComputedRef<Component>,
) {
	const def = computed(() =>
		wf.getComponentDefinition(unref(component).type),
	);

	const name = computed(() => {
		const c = unref(component);
		const { type, content } = c;
		if (type == "html" && content?.["element"]) {
			return content?.["element"];
		}
		if (type == "blueprints_blueprint") {
			return content?.["key"] || "Blueprint";
		}
		if (type == "shared_blueprint") {
			return getSourceBlueprintName(wf, c) || "Shared Blueprint";
		}
		return def.value?.name ?? `Unknown (${type})`;
	});

	const previewText = computed(() => {
		const key = def.value?.previewField;
		if (!key) return;
		const text = unref(component).content?.[key];

		let shortenedText: string;
		const MAX_PREVIEW_TEXT_LENGTH = 70;
		if (text?.length > MAX_PREVIEW_TEXT_LENGTH) {
			shortenedText = text.substring(0, MAX_PREVIEW_TEXT_LENGTH) + "...";
		} else {
			shortenedText = text;
		}

		return shortenedText;
	});

	const possibleImageUrls = computed(() => {
		const componentType = unref(component).type;
		const category = def.value.category;
		return [
			`/components/${componentType}.svg`,
			`/components/category_${category}.svg`,
			componentType.startsWith("blueprints_")
				? `/components/blueprints_category_${category}.svg`
				: undefined,
		]
			.filter(Boolean)
			.map((p) => convertAbsolutePathtoFullURL(p));
	});

	return { name, previewText, possibleImageUrls };
}
