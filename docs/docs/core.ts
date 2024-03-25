import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';

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
