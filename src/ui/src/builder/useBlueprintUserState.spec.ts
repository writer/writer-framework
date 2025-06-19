import { beforeEach, describe, it, expect, vi } from "vitest";
import { useBlueprintUserState } from "./useBlueprintUserState";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { useLogger } from "@/composables/useLogger";
import { Component } from "@/writerTypes";

describe(useBlueprintUserState.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;

	const baseComponent: Pick<Component, "id" | "type" | "parentId"> = {
		id: "c1",
		parentId: "blueprints_root",
		type: "blueprints_setstate",
	};

	beforeEach(() => {
		mockCore = buildMockCore();
	});

	it("should handle static JSON", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "foo",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({ foo: { bar: "baz" } });
	});

	it("should handle static JSON with nested key", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "foo.bar",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({ foo: { bar: { bar: "baz" } } });
	});

	it("should try to merge existing key", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				id: "1",
				content: {
					element: "foo.two",
					valueType: "text",
					value: "2",
				},
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					id: "2",
					element: "foo",
					valueType: "JSON",
					value: JSON.stringify({ one: "1" }),
				},
			}),
		);
		const state = useBlueprintUserState(mockCore.core);
		expect(state.value).toStrictEqual({ foo: { one: "1", two: "2" } });
	});

	it("should handle static JSON malformed", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "foo",
					valueType: "JSON",
					value: '{ "bar": "baz"',
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({ foo: {} });
	});

	it("should handle static text", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "foo",
					valueType: "text",
					value: "bar",
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({ foo: "bar" });
	});

	it("should handle static text with nested text", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "foo.bar",
					valueType: "text",
					value: "baz",
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({ foo: { bar: "baz" } });
	});

	it("should prevent malicous keys", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				content: {
					element: "__proto__",
					valueType: "text",
					value: "baz",
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core);

		expect(state.value).toStrictEqual({});
	});
});
