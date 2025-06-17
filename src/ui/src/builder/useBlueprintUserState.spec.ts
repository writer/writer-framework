import { beforeEach, describe, it, expect, vi } from "vitest";
import { useBlueprintUserState } from "./useBlueprintUserState";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { useLogger } from "@/composables/useLogger";

describe(useBlueprintUserState.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;

	beforeEach(() => {
		mockCore = buildMockCore();
	});

	it("should handle static JSON", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: { bar: "baz" } });
	});

	it("should handle static JSON with nested key", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo.bar",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: { bar: { bar: "baz" } } });
	});

	it("should not override existing key", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c3",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				outs: [{ toNodeId: "c3", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo.two",
					valueType: "text",
					value: "2",
				},
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo",
					valueType: "JSON",
					value: JSON.stringify({ one: "1" }),
				},
			}),
		);
		const c2State = useBlueprintUserState(mockCore.core, "c2");
		expect(c2State.value).toStrictEqual({ foo: { one: "1" } });

		const c3State = useBlueprintUserState(mockCore.core, "c3");
		expect(c3State.value).toStrictEqual({ foo: { one: "1", two: "2" } });
	});

	it("should handle static JSON malformed", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo",
					valueType: "JSON",
					value: '{ "bar": "baz"',
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: {} });
	});

	it("should handle static text", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo",
					valueType: "text",
					value: "bar",
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: "bar" });
	});

	it("should handle static text with nested text", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "foo.bar",
					valueType: "text",
					value: "baz",
				},
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: { bar: "baz" } });
	});

	it("should handle cyclic tree (malformed)", () => {
		const content = { element: "foo.bar", valueType: "text", value: "baz" };

		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_setstate",
				outs: [{ toNodeId: "c1", outId: "o1" }],
				content,
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o2" }],
				type: "blueprints_setstate",
				content,
			}),
		);

		const state = useBlueprintUserState(mockCore.core, "c2");

		expect(state.value).toStrictEqual({ foo: { bar: "baz" } });
	});

	it("should prevent malicous keys", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c2",
				type: "blueprints_logmessage",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "c1",
				outs: [{ toNodeId: "c2", outId: "o1" }],
				type: "blueprints_setstate",
				content: {
					element: "__proto__",
					valueType: "text",
					value: "baz",
				},
			}),
		);

		const logger = useLogger();
		const loggerError = vi
			.spyOn(logger, "error")
			.mockImplementation(() => {});

		const state = useBlueprintUserState(mockCore.core, "c2", logger);

		expect(state.value).toStrictEqual({});
		expect(loggerError).toHaveBeenCalled();
	});
});
