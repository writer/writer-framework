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

	describe("bindings", () => {
		it("should get the binding", () => {
			const component = buildMockComponent({
				...baseComponent,
				binding: {
					stateRef: "foo.bar",
					eventType: "wf-change",
				},
			});
			mockCore.core.addComponent(component);

			const { bindings } = useDynamicUserState(mockCore.core);

			expect(bindings.value).toStrictEqual({
				"foo.bar": { components: [component] },
			});
		});

		it("should not get the binding when key is defined in main.py", () => {
			mockCore.userStateInitial.value = { foo: { bar: 1 } };

			const component = buildMockComponent({
				...baseComponent,
				binding: {
					stateRef: "foo.bar",
					eventType: "wf-change",
				},
			});
			mockCore.core.addComponent(component);

			const { bindings } = useDynamicUserState(mockCore.core);

			expect(bindings.value).toStrictEqual({});
		});

		it("should handle no binding", () => {
			mockCore.core.addComponent(
				buildMockComponent({
					...baseComponent,
					binding: undefined,
				}),
			);

			const { bindings } = useDynamicUserState(mockCore.core);

			expect(bindings.value).toStrictEqual({});
		});
	});

	describe("blueprintsSetStates", () => {
		it("should get binding", () => {
			const component = buildMockComponent({
				...baseComponent,
				content: {
					element: "foo",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			});
			mockCore.core.addComponent(component);

			const { blueprintsSetStates } = useDynamicUserState(mockCore.core);

			expect(blueprintsSetStates.value).toStrictEqual({
				foo: { components: [component] },
			});
		});

		it("should not get binding when the key is empty", () => {
			const component = buildMockComponent({
				...baseComponent,
				content: {
					element: "",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			});
			mockCore.core.addComponent(component);

			const { blueprintsSetStates } = useDynamicUserState(mockCore.core);

			expect(blueprintsSetStates.value).toStrictEqual({});
		});

		it("should not get binding when key is defined in main.py", () => {
			mockCore.userStateInitial.value = { foo: { bar: 1 } };
			const component = buildMockComponent({
				...baseComponent,
				content: {
					element: "foo.bar",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			});
			mockCore.core.addComponent(component);

			const { blueprintsSetStates } = useDynamicUserState(mockCore.core);

			expect(blueprintsSetStates.value).toStrictEqual({});
		});
	});
});
