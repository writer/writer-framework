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
	if (slice.includes("\n")) return "";

	if (!slice.startsWith("@{") && slice.includes(" ")) return "";

	return slice.replace(/^@{?/, "");
}
