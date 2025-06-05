import type { BuilderManagerMode } from "@/builder/builderManager";

export const BUILDER_MANAGER_MODE_ICONS = Object.freeze<
	Record<BuilderManagerMode, string>
>({
	ui: "grid_3x3",
	blueprints: "linked_services",
	preview: "visibility",
	vault: "key",
});
