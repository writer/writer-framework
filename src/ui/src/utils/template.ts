export function autocompleteTemplateVariable(input: string, variable: string) {
	const matches: { start: number; end: number }[] = [];

	// Pattern 2: @{...} or @{...
	const pattern2 = /@\{[^}]*\}|@\{[^}\s]*/g;
	let match: RegExpExecArray | null;
	while ((match = pattern2.exec(input)) !== null) {
		matches.push({
			start: match.index,
			end: match.index + match[0].length,
		});
		if (pattern2.lastIndex === match.index) {
			pattern2.lastIndex = match.index + 1;
		}
	}
	pattern2.lastIndex = 0;

	// Pattern 3: ${...} or ${...
	const pattern3 = /\$\{[^}]*\}|\$\{[^}\s]*/g;
	while ((match = pattern3.exec(input)) !== null) {
		matches.push({
			start: match.index,
			end: match.index + match[0].length,
		});
		if (pattern3.lastIndex === match.index) {
			pattern3.lastIndex = match.index + 1;
		}
	}
	pattern3.lastIndex = 0;

	// Pattern 1: standalone "@" followed by whitespace or end
	const pattern1 = /@(?=\s|$)/g;
	while ((match = pattern1.exec(input)) !== null) {
		const start = match.index;
		const end = start + 1; // "@" is length 1
		// Check for overlaps with existing matches
		let overlaps = false;
		for (const existingMatch of matches) {
			if (!(end <= existingMatch.start || start >= existingMatch.end)) {
				overlaps = true;
				break;
			}
		}
		if (!overlaps) {
			matches.push({ start, end });
		}
		if (pattern1.lastIndex === match.index) {
			pattern1.lastIndex = match.index + 1;
		}
	}
	pattern1.lastIndex = 0;

	if (matches.length === 0) {
		return input;
	}

	// Find the match with the highest start index
	let lastMatch = matches[0];
	for (const match of matches) {
		if (match.start > lastMatch.start) {
			lastMatch = match;
		}
	}

	const replacement = `@{${variable}}`;
	return (
		input.substring(0, lastMatch.start) +
		replacement +
		input.substring(lastMatch.end)
	);
}

export function getCurrentOpenedTemplate(input: string): string {
	const openers = [
		{ prefix: "@{", length: 2 },
		{ prefix: "${", length: 2 },
	];
	const stack: Array<{ position: number; length: number }> = [];

	for (let i = 0; i < input.length; i++) {
		let openerFound = false;
		for (const opener of openers) {
			if (input.startsWith(opener.prefix, i)) {
				stack.push({ position: i, length: opener.length });
				i += opener.length - 1; // skip past the opener
				openerFound = true;
				break;
			}
		}
		if (openerFound) continue;

		if (input[i] === "}" && stack.length > 0) {
			stack.pop();
		}
	}

	if (stack.length === 0) {
		return "";
	}

	const lastOpener = stack[stack.length - 1];
	const contentStart = lastOpener.position + lastOpener.length;
	return input.slice(contentStart);
}
