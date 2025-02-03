import type { WdsTabOptions } from "@/wds/WdsTabs.vue";

export type BuilderFieldCssMode = "pick" | "css" | "default";

export const BUILDER_FIELD_CSS_TAB_OPTIONS = Object.freeze<
	WdsTabOptions<BuilderFieldCssMode>[]
>([
	{
		label: "Default",
		value: "default",
	},
	{
		label: "CSS",
		value: "css",
	},
	{
		label: "Pick",
		value: "pick",
	},
]);
