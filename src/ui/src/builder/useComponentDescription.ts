import { generateCore } from "@/core";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { Component } from "@/writerTypes";
import { computed, ComputedRef, unref } from "vue";

export function useComponentDescription(
	wf: ReturnType<typeof generateCore>,
	component: Component | ComputedRef<Component>,
) {
	const def = computed(() =>
		wf.getComponentDefinition(unref(component).type),
	);

	const name = computed(() => {
		const { type, content } = unref(component);
		if (type == "html" && content?.["element"]) {
			return content?.["element"];
		}
		if (type == "blueprints_blueprint") {
			return content?.["key"] || "Blueprint";
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
		return [
			`/components/${unref(component).type}.svg`,
			`/components/category_${def.value.category}.svg`,
		].map((p) => convertAbsolutePathtoFullURL(p));
	});

	return { name, previewText, possibleImageUrls };
}
