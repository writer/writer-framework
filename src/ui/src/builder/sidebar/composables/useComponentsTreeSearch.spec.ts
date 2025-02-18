import { computed, ref } from "vue";
import { beforeAll, describe, expect, it } from "vitest";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import {
	useComponentsTreeSearch,
	useComponentsTreeSearchForComponent,
} from "./useComponentsTreeSearch";
import { generateCore } from "@/core";

describe(useComponentsTreeSearch.name, () => {
	const q = ref("");
	const component = buildMockComponent({
		type: "button",
		content: {
			tag1: "Tag1",
		},
	});
	let hook: ReturnType<typeof useComponentsTreeSearch>;

	beforeAll(() => {
		const core = buildMockCore().core;
		core.addComponent(component);
		hook = useComponentsTreeSearch(core, q);
	});

	it("should match a component when the query is empty", () => {
		q.value = "";
		expect(hook.isComponentMatchingQuery(component)).toBe(true);
	});

	it("should match a component from its content", () => {
		q.value = "tag1";
		expect(hook.isComponentMatchingQuery(component)).toBe(true);
	});

	it("should match a component from its type", () => {
		q.value = "button";
		expect(hook.isComponentMatchingQuery(component)).toBe(true);
	});

	it("should not match a component", () => {
		q.value = "foo";
		expect(hook.isComponentMatchingQuery(component)).toBe(false);
	});
});

describe(useComponentsTreeSearchForComponent.name, () => {
	let core: ReturnType<typeof generateCore>;
	const q = ref("");
	const component1 = buildMockComponent({
		id: "component1",
		type: "button",
		content: {
			tag1: "Tag1",
		},
	});
	const component2 = buildMockComponent({
		id: "component2",
		parentId: component1.id,
		type: "button",
		content: {
			tag1: "Tag2",
		},
	});
	let hook: ReturnType<typeof useComponentsTreeSearchForComponent>;

	beforeAll(() => {
		core = buildMockCore().core;
		core.addComponent(component1);
		core.addComponent(component2);
		hook = useComponentsTreeSearchForComponent(
			core,
			q,
			computed(() => component1),
		);
	});

	it("should match a component when the query is empty", () => {
		q.value = "";

		expect(hook.hasMatchingChildren.value).toBe(true);
		expect(hook.matched.value).toBe(true);
	});

	it("should match a component from its content", () => {
		q.value = "tag1";

		expect(hook.hasMatchingChildren.value).toBe(false);
		expect(hook.matched.value).toBe(true);
	});

	it("should match a children from its content", () => {
		q.value = "tag2";

		expect(hook.hasMatchingChildren.value).toBe(true);
		expect(hook.matched.value).toBe(false);
	});

	it("should not match a component", () => {
		q.value = "foo";

		expect(hook.hasMatchingChildren.value).toBe(false);
		expect(hook.matched.value).toBe(false);
	});
});
