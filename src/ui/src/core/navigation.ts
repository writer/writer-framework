export type ParsedHash = {
	pageKey?: string;
	routeVars: Map<string, string>; // Stored as Map to avoid injection e.g. prototype pollution
};

// Use to communicate with the backend
export type SerializedHash = {
	pageKey?: string;
	routeVars: Record<string, string>;
};

const hashRegex = /^((?<pageKey>[^/]*))?(\/(?<routeVars>.*))?$/;

/**
 * Parses the current URL hash
 *
 * @example
 * ```js
 * getParsedHash('#main/var1=value1&var2=value2')
 * // => { routeVars: new Map([ ["var1", "value1"], ["var2", "value2"], ]), pageKey: "main" }
 * ```
 */
export function getParsedHash(hash = document.location.hash): ParsedHash {
	const docHash = hash.substring(1);
	const hashMatchGroups = docHash.match(hashRegex)?.groups;
	const pageKey = hashMatchGroups?.pageKey
		? decodeURIComponent(hashMatchGroups.pageKey)
		: undefined;

	if (!hashMatchGroups) return { pageKey, routeVars: new Map() };

	const params = new URLSearchParams(hashMatchGroups.routeVars);

	return { pageKey, routeVars: new Map(params.entries()) };
}

/**
 * Serializes the URL information into a JSON.stringify-compatible object.
 *
 * It's used to send the current URL information to the server.
 *
 * @example
 * ```ts
 * const serializedHash = serializeParsedHash();
 * const urlinfoString = JSON.stringify(serializedHash);
 * ```
 */
export function serializeParsedHash(): SerializedHash {
	const parsedHash = getParsedHash();
	const routeVars = Object.fromEntries(parsedHash.routeVars.entries());
	return { pageKey: parsedHash.pageKey, routeVars };
}

export function serializeParsedHashAsString(parsedHash: ParsedHash) {
	const { pageKey, routeVars } = parsedHash;

	let hash = "";
	if (pageKey) {
		hash += `${encodeURIComponent(pageKey)}`;
	}

	if (routeVars.size > 0) {
		const params = new URLSearchParams([...routeVars.entries()]);
		hash += `/${params.toString()}`;
	}
	return hash;
}

function setHash(parsedHash: ParsedHash) {
	document.location.hash = serializeParsedHashAsString(parsedHash);
}

export function changePageInHash(targetPageKey: string) {
	const parsedHash = getParsedHash();
	parsedHash.pageKey = targetPageKey;
	setHash(parsedHash);
}

export function changeRouteVarsInHash(targetRouteVars: Record<string, string>) {
	const parsedHash = getParsedHash();
	const routeVars = parsedHash?.routeVars ?? {};
	parsedHash.routeVars = new Map(
		Object.entries({ ...routeVars, ...targetRouteVars }),
	);
	setHash(parsedHash);
}
