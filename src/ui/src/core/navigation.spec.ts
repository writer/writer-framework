import { describe, it, expect } from "vitest";
import {
	getParsedHash,
	ParsedHash,
	serializeParsedHashAsString,
} from "./navigation";

const sample: { hash: string; parsedHash: ParsedHash }[] = [
	{
		hash: "#main/var1=value1&var2=value2",
		parsedHash: {
			routeVars: new Map([
				["var1", "value1"],
				["var2", "value2"],
			]),
			pageKey: "main",
		},
	},
	{
		hash: "#main",
		parsedHash: {
			routeVars: new Map(),
			pageKey: "main",
		},
	},
	{
		hash: "#",
		parsedHash: {
			routeVars: new Map(),
			pageKey: undefined,
		},
	},
	{
		hash: "#/var1=value1&var2=value2",
		parsedHash: {
			routeVars: new Map([
				["var1", "value1"],
				["var2", "value2"],
			]),
			pageKey: undefined,
		},
	},
];

describe(getParsedHash.name, () => {
	it.each(sample)("should parse $hash", ({ hash, parsedHash }) => {
		expect(getParsedHash(hash)).toStrictEqual(parsedHash);
	});
});

describe(serializeParsedHashAsString.name, () => {
	it.each(sample)("should serialize $hash", ({ hash, parsedHash }) => {
		expect(serializeParsedHashAsString(parsedHash)).toStrictEqual(
			hash.substring(1),
		);
	});
});
