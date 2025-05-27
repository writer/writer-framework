export const COMPONENT_TYPES_ROOT = new Set(["root", "blueprints_root"]);

export const COMPONENT_TYPES_TOP_LEVEL = new Set([
	...COMPONENT_TYPES_ROOT,
	"page",
	"blueprints_blueprint",
]);
