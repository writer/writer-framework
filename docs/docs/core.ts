import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import { marked } from 'marked';
import components from "writer-ui/components.codegen.json" assert { type: "json" };

// @ts-ignore
hljs.registerLanguage('python', python);

export function highlightCode(code: string, language = 'python') {
	if (!code) return "";


	let value = hljs.highlight(code,{
		'language': language
	}).value;

	value = value.replace(/\t/g, "  ")
	return value
}

export function markdownToHtml(markdown: string) {
	if (!markdown) return "";

	return marked.parse(markdown);
}

export function categories() {
	const categoriesAll = Object.entries(categoriesList).map(([name, description]) => {
		return name;
	});

	return categoriesAll;
}


export function categoryDescription(name: string) {
	return categoriesList[name];
}

export function componentByName(name: string) {
	return components.find((component) => component.name === name);
}


export function componentsByCategory(category: string) {
	return components.filter((component) => component.category === category);
}

/**
 *
 * @example
 * <pre><code v-html="generateEventHandler()"></code></pre>
 */
export function generateEventHandler() {
	let code = `def handle_event(state, payload, context, ui):
  pass
`
	return highlightCode(code)
}

/**
 * Generates an example of component usage in Low Code
 *
 * @param component_name Name of a component
 * @returns Example code
 * 
 * @example
 * <pre><code v-html="generateLowCodeUsage("Button")"></code></pre>
 */
export function generateLowCodeUsage(component_name: string) : string {
	const component = components.find(c => c.name === component_name);
	
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
	return highlightCode(code, 'python')
}

export function values(obj: object) {
	if (!obj) return [];

	return Object.keys(obj).map((key) => {
		return obj[key]
	})
}

function renderDefaultValue(properties: object) {
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

const renderPyOptions = (options) => {
	if (!options) return "";

	return "[" + Object.keys(options).join(", ") + "]"
};


/**
 * List of categories and their descriptions (internal)
 */
const categoriesList = {
	"Layout": "Components to organise the app's layout. Not meaningful by themselves; their objective is to enhance how other components are presented.",
	"Content": "Components that present content and are meaningful by themselves. For example, charts, images or text.",
	"Input": "Components whose main objective is to allow the user to input data into the app.",
	"Other": "These components occupy a special role and are amongst the most powerful in the framework.",
	"Embed": "Components that integrate external functionalities seamlessly.",
	"Root": "These components are the top-level containers."
};


