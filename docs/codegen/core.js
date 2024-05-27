/**
 * Generates an example of component usage in Low Code
 *
 * @param component {object} Name of a component
 * @returns Example code {string}
 *
 * @example
 * component.low_code_usage = core.generateLowCodeUsage(component)
 */
export function generateLowCodeUsage(component) {
	let contents = "content={\n"
	for (let fieldKey in component.fields) {
		const properties = component.fields[fieldKey]
		contents += `        "${fieldKey}": ${renderDefaultValue(properties)}, # ${renderPyType(properties['type'])} ${renderPyOptions(properties['options'])}\n`
	}
	contents += "    }"

	let handlers = ""
	if (component.events && Object.keys(component.events).length > 0) {
		handlers += "\n,\n    handlers={\n"
		for (let event in component.events) {
			handlers += `        "${event}": handle_event,\n`
		}
		handlers += "    }"
	}

	// @ts-ignore
	let code = `ui.${component.name.replaceAll(/\s/g, "")}(${contents.trim()}${handlers.trim()}
)`
	return code
}

/**
 *
 * @example
 * component.event_handler = core.generateEventHandler()
 */
export function generateEventHandler() {
	let code = `def handle_event(state, payload, context, ui):
  pass`
	return code
}

/**
 *
 * @param obj {object}
 * @returns {*[]}
 */
export function values(obj) {
	if (!obj) return [];

	return Object.keys(obj).map((key) => {
		return obj[key]
	})
}

/**
 *
 * @param properties {object}
 * @returns {string}
 */
function renderDefaultValue(properties) {
	const type = properties['type'];
	switch (type) {
		case "Number":
			return '0.0';
		case "Object":
			return "{}";
		case "Key-Value":
			return "{}";
		default:
			if (properties['options'] && properties['default']) {
				return `"${ properties['default'] }"`;
			}

			return '""';
	}
}

/**
 *
 * @param type {string}
 * @returns {string}
 */
const renderPyType = (type) => {
	switch (type) {
		case "Number":
			return "Union[float, str]";
		case "Object":
			return "Union[Dict, str]";
		case "Key-Value":
			return "Union[Dict, str]";
		default:
			return "str";
	}
};

/**
 *
 * @param options {object}
 * @returns {string}
 */
const renderPyOptions = (options) => {
	if (!options) return "";

	return "[" + Object.keys(options).join(", ") + "]"
};
