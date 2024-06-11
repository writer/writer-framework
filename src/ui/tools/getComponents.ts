import { generateCore } from "../src/core";
const wf = generateCore();
const types = wf.getSupportedComponentTypes();
const data = types.map((type) => {
	const def = wf.getComponentDefinition(type);
	return { type, ...def };
});
export { data };
