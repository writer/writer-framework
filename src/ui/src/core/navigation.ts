type ParsedHash = {
	pageKey?: string;
	routeVars: Map<string, string>; // Stored as Map to avoid injection e.g. prototype pollution
};

// Use to communicate with the backend
type SerializedHash = {
	pageKey?: string;
	routeVars: Record<string, string>;
};

const hashRegex = /^((?<pageKey>[^/]*))?(\/(?<routeVars>.*))?$/;
const routeVarRegex = /^(?<key>[^=]+)=(?<value>.*)$/;

/**
 * Parses the current URL hash
 *
 * * http://x.x.x.x:5000/#main/var1=value1&var2=value2
 *
 * pageKey: "main"
 * routeVars: { var1: "value1", var2: "value2" }
 */
export function getParsedHash(): ParsedHash {
	const docHash = document.location.hash.substring(1);
	const hashMatchGroups = docHash.match(hashRegex)?.groups;
	const routeVars: Map<string, string> = new Map();
	const pageKey = hashMatchGroups?.pageKey
		? decodeURIComponent(hashMatchGroups.pageKey)
		: undefined;

	if (!hashMatchGroups) return { pageKey, routeVars };

	const routeVarsSegments = hashMatchGroups.routeVars?.split("&") ?? [];
	routeVarsSegments.forEach((routeVarSegment) => {
		const matchGroups = routeVarSegment.match(routeVarRegex)?.groups;
		if (!matchGroups) return;
		const { key, value } = matchGroups;
		const decodedKey = decodeURIComponent(key);
		const decodedValue = decodeURIComponent(value);
		routeVars.set(decodedKey, decodedValue);
	});

	return { pageKey, routeVars };
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

function setHash(parsedHash: ParsedHash) {
	const { pageKey, routeVars } = parsedHash;

	let hash = "";
	if (pageKey) {
		hash += `${encodeURIComponent(pageKey)}`;
	}

	if (routeVars.keys.length > 0) {
		hash += "/";
		hash += Array.from(routeVars.entries())
			.map(([key, value]) => {
				// Vars set to null are excluded from the hash

				if (value === null) return null;
				return `${encodeURIComponent(key)}=${encodeURIComponent(
					value,
				)}`;
			})
			.filter((segment) => segment)
			.join("&");
	}
	document.location.hash = hash;
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
