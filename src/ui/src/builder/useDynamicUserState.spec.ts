import { beforeEach, describe, it, expect } from "vitest";
import { useDynamicUserState } from "./useDynamicUserState";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { Component } from "@/writerTypes";

describe(useDynamicUserState.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;

	const baseComponent: Pick<Component, "id" | "type" | "parentId"> = {
		id: "c1",
		parentId: "blueprints_root",
		type: "blueprints_setstate",
	};

	beforeEach(() => {
		mockCore = buildMockCore();
	});

	describe("bindingsUserState", () => {
		it("should get the binding", () => {
			mockCore.core.addComponent(
				buildMockComponent({
					...baseComponent,
					binding: {
						stateRef: "foo.bar",
						eventType: "wf-change",
					},
				}),
			);

			const { bindingsUserState } = useDynamicUserState(mockCore.core);

			expect(bindingsUserState.value).toStrictEqual({
				foo: { bar: "unknown value" },
			});
		});

		it("should handle no binding", () => {
			mockCore.core.addComponent(
				buildMockComponent({
					...baseComponent,
					binding: undefined,
				}),
			);

			const { bindingsUserState } = useDynamicUserState(mockCore.core);

			expect(bindingsUserState.value).toStrictEqual({});
		});
	});

	describe("blueprintsUserState", () => {
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({
				foo: { bar: "baz" },
			});
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({
				foo: { bar: { bar: "baz" } },
			});
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
			const { blueprintsUserState } = useDynamicUserState(mockCore.core);
			expect(blueprintsUserState.value).toStrictEqual({
				foo: { one: "1", two: "2" },
			});
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({ foo: {} });
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({ foo: "bar" });
		});

		it("should handle unexisting value text", () => {
			mockCore.core.addComponent(
				buildMockComponent({
					...baseComponent,
					content: {
						element: "foo",
						valueType: undefined,
						value: undefined,
					},
				}),
			);

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({ foo: "" });
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({
				foo: { bar: "baz" },
			});
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

			const { blueprintsUserState } = useDynamicUserState(mockCore.core);

			expect(blueprintsUserState.value).toStrictEqual({});
		});
	});
});
