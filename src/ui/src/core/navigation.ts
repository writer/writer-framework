type ParsedHash = {
	pageKey?: string;
	routeVars: Record<string, string>;
};

const hashRegex = /^((?<pageKey>[^/]*))?(\/(?<routeVars>.*))?$/;
const routeVarRegex = /^(?<key>[^=]+)=(?<value>.*)$/;

export function getParsedHash(): ParsedHash {
	const docHash = document.location.hash.substring(1);
	const hashMatchGroups = docHash.match(hashRegex)?.groups;

	if (!hashMatchGroups) return { pageKey: undefined, routeVars: {} };

	const routeVars: Record<string, string> = {};
	const pageKey = hashMatchGroups?.pageKey
		? decodeURIComponent(hashMatchGroups.pageKey)
		: undefined;

	const routeVarsSegments = hashMatchGroups.routeVars?.split("&") ?? [];
	routeVarsSegments.forEach((routeVarSegment) => {
		const matchGroups = routeVarSegment.match(routeVarRegex)?.groups;
		if (!matchGroups) return;
		const { key, value } = matchGroups;
		const decodedKey = decodeURIComponent(key);
		const decodedValue = decodeURIComponent(value);
		routeVars[decodedKey] = decodedValue;
	});

	return { pageKey, routeVars };
}

function setHash(parsedHash: ParsedHash) {
	const { pageKey, routeVars } = parsedHash;

	let hash = "";
	if (pageKey) {
		hash += `${encodeURIComponent(pageKey)}`;
	}
	if (Object.keys(routeVars).length > 0) {
		hash += "/";
		hash += Object.entries(routeVars)
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
	parsedHash.routeVars = { ...routeVars, ...targetRouteVars };
	setHash(parsedHash);
}