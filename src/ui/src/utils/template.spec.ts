import { describe, it, expect } from "vitest";
import {
	autocompleteTemplateVariable,
	getCurrentOpenedTemplate,
} from "./template";

describe(autocompleteTemplateVariable.name, () => {
	it.each([
		{ input: "foo", result: "foo@{foo.bar}" },
		{ input: "@", result: "@{foo.bar}" },
		{ input: "@{", result: "@{foo.bar}" },
		{ input: "@{other", result: "@{foo.bar}" },
		{ input: "@{other.", result: "@{foo.bar}" },
		{ input: "@{other.var}", result: "@{foo.bar}" },
		{ input: "@other.var", result: "@{foo.bar}" },
		{ input: "before @{other.var}", result: "before @{foo.bar}" },
		{ input: "before @{var1} @{var", result: "before @{var1} @{foo.bar}" },
	])("should assign %s", ({ input, result }) => {
		expect(autocompleteTemplateVariable(input, "foo.bar")).toStrictEqual(
			result,
		);
	});
});

describe(getCurrentOpenedTemplate.name, () => {
	it.each([
		{ input: "@", result: "" },
		{ input: "@{", result: "" },
		{ input: "@{other", result: "other" },
		{ input: "@{other.", result: "other." },
		{ input: "@{other.var}", result: "" },
		{ input: "before @{other.var}", result: "" },
		{ input: "before @{var1} @{var", result: "var" },
		{ input: "before @var1", result: "var1" },
		{ input: "before @var1 ", result: "" },
		{ input: "before @{var1 ", result: "var1 " },
	])("should assign %s", ({ input, result }) => {
		expect(getCurrentOpenedTemplate(input)).toStrictEqual(result);
	});
});
