import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import components from "streamsync-ui/components.codegen.json";

// @ts-ignore
hljs.registerLanguage('python', python);

/**
 * Highlight source
 *
 * @param code Source to highlight
 * @param language Language of the source
 */
export function highlightCode(code: string, language = 'python') {
	if (!code) return "";


	let value = hljs.highlight(code,{
		'language': language
	}).value;

	value = value.replace(/\t/g, "  ")
	return value
}

/**
 * Get the list of categories
 */
export function categories() {
	const categoriesAll = Object.entries(categoriesList).map(([name, description]) => {
		return name;
	});

	return categoriesAll;
}

/**
 * Get the description of a category
 * @param name Name of the category
 */
export function categoryDescription(name: string) {
	return categoriesList[name];
}

/**
 * List the components of a category
 *
 * @param category
 */
export function componentsByCategory(category: string) {
	return components.filter((component) => component.category === category);
}

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


