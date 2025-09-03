import { isPlainObject } from "@/utils/object";

type ArrayOrObject = unknown[] | Record<string, unknown>;

type TokenType = "key-value" | "collapsed";
type Token = {
	type: TokenType;
	key: string;
	/** index in the selection text */
	index: number;
};

function escapeRegex(text: string) {
	return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Finds the first occurrence of a root key used as a Key:Value entry in the selection text.
 * Accepts either `"key":` or `key` with the colon on the next line.
 *
 * Example matches:
 *   - `"name":`
 *   - `name` (newline) `:` (newline/space) …
 */
function findKeyValueIndex(key: string, selectionText: string): number {
	return selectionText.search(
		new RegExp(`(^|\\n)\\s*"?${escapeRegex(key)}"?\\s*:\\s*`),
	);
}

/**
 * Finds the first occurrence of a root key used as a collapsed header in the selection text.
 * Accepts either the marker on the same line or the next line:
 *
 * Example matches:
 *   - `key Object{N}`
 *   - `key` (newline) `Object{N}`
 *   - `key Array[N]`
 *   - `key` (newline) `Array[N]`
 */
function findCollapsedIndex(key: string, selectionText: string): number {
	return selectionText.search(
		new RegExp(
			`(^|\\n)\\s*"?${escapeRegex(key)}"?\\s*(\\n\\s*)?(Object\\{\\d+\\}|Array\\[\\d+\\])`,
		),
	);
}

/**
 * Returns root-level tokens (first occurrences) found in the selection text.
 * Each root key can contribute two tokens at most: "key-value" and/or "collapsed".
 */
function getRootTokens(
	root: Record<string, unknown>,
	selectionText: string,
): Token[] {
	const result: Token[] = [];

	Object.keys(root).forEach((key) => {
		const keyValueIndex = findKeyValueIndex(key, selectionText);

		if (keyValueIndex !== -1) {
			result.push({ type: "key-value", key, index: keyValueIndex });
		}

		const collapsedIndex = findCollapsedIndex(key, selectionText);

		if (collapsedIndex !== -1) {
			result.push({ type: "collapsed", key, index: collapsedIndex });
		}
	});

	result.sort((a, b) => a.index - b.index);

	return result;
}

type CollapsedSegment = {
	key: string;
	startIndex: number;
	endIndex: number;
};

/**
 * Returns "windows" for collapsed parents.
 * A window spans from the collapsed token to the next token that either:
 *  - is another collapsed root key, OR
 *  - is a root key-value that does NOT belong to this parent
 * If none is found, the window ends at the end of the selection text.
 */
function getCollapsedSegments(
	root: Record<string, unknown>,
	selectionText: string,
	tokens: Token[],
): CollapsedSegment[] {
	const childMap = new Map<string, Set<string>>();

	Object.entries(root).forEach(([key, value]) => {
		childMap.set(
			key,
			isPlainObject(value) ? new Set(Object.keys(value)) : new Set(),
		);
	});

	const result: CollapsedSegment[] = [];

	tokens.forEach((token, tokenIndex) => {
		if (token.type !== "collapsed") {
			return;
		}

		const children = childMap.get(token.key) ?? new Set();
		let endIndex = selectionText.length;

		for (let i = tokenIndex + 1; i < tokens.length; i++) {
			const nextToken = tokens[i];

			if (nextToken.index <= token.index) {
				continue;
			}

			if (nextToken.type === "collapsed") {
				endIndex = nextToken.index;

				break;
			}

			if (
				nextToken.type === "key-value" &&
				!children.has(nextToken.key)
			) {
				endIndex = nextToken.index;

				break;
			}
		}

		result.push({
			key: token.key,
			startIndex: token.index,
			endIndex,
		});
	});

	return result;
}

/**
 * Returns the set of root key-value tokens that are NOT inside any collapsed window.
 * These should be included at the root level.
 */
function getRootKeysOutsideSegments(
	tokens: Token[],
	segments: CollapsedSegment[],
): Set<string> {
	const result = new Set<string>();

	tokens.forEach((token) => {
		if (token.type !== "key-value") {
			return;
		}

		const inside = segments.some(
			(segment) =>
				token.index >= segment.startIndex &&
				token.index < segment.endIndex,
		);

		if (!inside) {
			result.add(token.key);
		}
	});

	return result;
}

/**
 * Finds the exact collapsed segment corresponding to a collapsed token.
 * Primarily matches by (key + startIndex), otherwise falls back to the first segment with the same key.
 */
function findSegmentFor(
	token: Token,
	segments: CollapsedSegment[],
): CollapsedSegment | null {
	const result = segments.find(
		(segment) =>
			segment.key === token.key && segment.startIndex === token.index,
	);

	return (
		result ?? segments.find((segment) => segment.key === token.key) ?? null
	);
}

/**
 * Builds a subset (object + array view) from the given root and selection text.
 * The array preserves textual order of included values.
 * For collapsed parents that are objects, the function recurses into the parent's window.
 */
function buildSubsetFromSelection(
	root: Record<string, unknown>,
	selectionText: string,
) {
	const tokens = getRootTokens(root, selectionText);
	const segments = getCollapsedSegments(root, selectionText, tokens);
	const rootKeys = getRootKeysOutsideSegments(tokens, segments);

	type Result = {
		array: unknown[];
		object: Record<string, unknown>;
	};

	const result: Result = {
		array: [],
		object: {},
	};

	function addToResult(key: string, value: unknown) {
		result.array.push(value);
		result.object[key] = value;
	}

	tokens.forEach((token) => {
		if (token.key in result.object) {
			return;
		}

		const value = root[token.key];

		switch (token.type) {
			case "key-value": {
				if (rootKeys.has(token.key)) {
					addToResult(token.key, value);
				}

				break;
			}
			case "collapsed": {
				const segment = findSegmentFor(token, segments);
				const windowText = segment
					? selectionText.slice(segment.startIndex, segment.endIndex)
					: selectionText;

				if (!isPlainObject(value)) {
					// non-objects (arrays/scalars) are included fully
					addToResult(token.key, value);

					break;
				}

				const nested = buildSubsetFromSelection(value, windowText);
				const hasNested =
					nested.array.length > 0 ||
					Object.keys(nested.object).length > 0;

				addToResult(token.key, hasNested ? nested.object : value);

				break;
			}
			default: {
				break;
			}
		}
	});

	const isResultEmpty =
		result.array.length === 0 || Object.keys(result.object).length === 0;

	if (tokens.length > 0 && isResultEmpty) {
		// copy-all fallback: tokens exist but nothing assembled
		Object.entries(root).forEach(([key, val]) => {
			addToResult(key, val);
		});
	}

	return {
		array: result.array,
		object: result.object,
		tokenCount: tokens.length,
	};
}

/**
 * Builds a JSON subset from raw text selection and the current JSON `data`.
 *
 * Rules:
 *  - Root key-value hits: `key: …` (the colon may appear on the next line).
 *  - Collapsed hits: `key` followed by `Object{N}` or `Array[N]` (same line or next line).
 *  - For a collapsed parent:
 *      * If child keys appear within its window, only those children are included (recursively).
 *      * Otherwise, the whole object/array is included.
 *  - Root key-values inside a parent's window are treated as that parent's children.
 *
 * Return shape:
 *  - If `data` is an object → a subset object.
 *  - If `data` is an array  → a subset array preserving textual order.
 *  - Otherwise              → empty object.
 */
export function selectionToJson(
	data: ArrayOrObject,
	rawSelectionText: string,
): ArrayOrObject {
	const selectionText = rawSelectionText.replace(/\r\n/g, "\n");

	if (isPlainObject(data)) {
		const { object } = buildSubsetFromSelection(data, selectionText);

		return object;
	}

	if (Array.isArray(data)) {
		// array root: project indices to string keys, reuse the same pipeline, map back to array
		const projected: Record<string, unknown> = {};
		data.forEach((item, itemIndex) => {
			projected[String(itemIndex)] = item;
		});

		const { array, tokenCount } = buildSubsetFromSelection(
			projected,
			selectionText,
		);

		if (array.length > 0) {
			return array;
		}

		// copy-all for root array if there were tokens or an explicit Array[N] mention
		const rootArrayRegex = /(^|\n)\s*Array\[\d+\]/;
		if (tokenCount > 0 || rootArrayRegex.test(selectionText)) {
			return data.slice();
		}

		return [];
	}

	return {};
}
