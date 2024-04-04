import { getComponentDefinition } from "../core/templateMap";

export const generateCore = () => {
	return {
		getComponentDefinition,
		getComponentById: (id) => {},
	};
};
