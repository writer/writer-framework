export function autocompleteTemplateVariable(input: string, variable: string) {
	const lastAtPos = input.lastIndexOf("@");

	if (lastAtPos !== -1) {
		// Determine the start position of replacement considering '{'
		let replacementStartPos = lastAtPos;
		const remainingString = input.slice(lastAtPos);

		// If there's an opening brace after '@', extend start position
		const braceOpenPos = remainingString.indexOf("{");
		if (braceOpenPos !== -1) {
			replacementStartPos += braceOpenPos + 1;
		}

		// Check for closing brace
		const closeBracePos = input.indexOf("}", replacementStartPos);

		if (closeBracePos !== -1) {
			// If closing brace found, replace entire segment from @{ to }
			return input.substring(0, lastAtPos) + `@{${variable}}`;
		} else {
			// Otherwise, replace from @ or @{
			const prefix = input.slice(0, lastAtPos);
			return prefix + `@{${variable}}`;
		}
	}

	// If no '@' found, append the template variable
	return input + `@{${variable}}`;
}

export function getCurrentOpenedTemplate(input: string): string {
	const startIndex = input.lastIndexOf("@");
	if (startIndex === -1) return "";

	const slice = input.slice(startIndex);
	if (slice.includes("}")) return "";

	if (!slice.startsWith("@{") && slice.includes(" ")) return "";

	return slice.replace(/^@{?/, "");
}

export function* computeTemplateParts(
	input: string,
): Generator<{ content: string; type: "text" | "tag" }, void, unknown> {
	if (input === undefined) return;
	let currentText = "";
	let i = 0;
	const n = input.length;

	while (i < n) {
		if (input.startsWith("@{", i)) {
			if (currentText.length > 0) {
				yield { content: currentText, type: "text" as const };
				currentText = "";
			}
			let j = i + 2;
			let foundClosingBrace = false;
			while (j < n) {
				if (input[j] === "}") {
					foundClosingBrace = true;
					break;
				}
				j++;
			}
			if (foundClosingBrace) {
				const tagContent = input.slice(i + 2, j);
				yield { content: tagContent, type: "tag" as const };
				i = j + 1;
			} else {
				currentText += input.slice(i);
				i = n;
			}
		} else {
			currentText += input[i];
			i++;
		}
	}
	if (currentText.length > 0) {
		yield { content: currentText, type: "text" as const };
	}
}
