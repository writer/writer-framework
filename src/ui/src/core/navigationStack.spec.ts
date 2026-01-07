import { describe, it, expect, beforeEach } from "vitest";
import { ref } from "vue";
import { createNavigationStack } from "./navigationStack";
import type { Component } from "@/writerTypes";

describe("createNavigationStack", () => {
	let activePageId: ReturnType<typeof ref<Component["id"] | undefined>>;
	let mockComponents: Record<string, Component>;
	let getComponentById: (id: Component["id"]) => Component | undefined;
	let stack: ReturnType<typeof createNavigationStack>;

	beforeEach(() => {
		activePageId = ref(undefined);
		mockComponents = {
			page1: {
				id: "page1",
				type: "page",
				content: { key: "HomePage" },
			} as Component,
			page2: {
				id: "page2",
				type: "page",
				content: { key: "AboutPage" },
			} as Component,
			blueprint1: {
				id: "blueprint1",
				type: "blueprints_blueprint",
				content: { key: "UserBlueprint" },
			} as Component,
		};
		getComponentById = (id: Component["id"]) => mockComponents[id];
		stack = createNavigationStack(activePageId, getComponentById);
	});

	describe("navigateInPageStack", () => {
		it("should add first page to empty stack", () => {
			const result = stack.navigateInPageStack("page1", "forward");

			expect(result).toEqual({
				id: "page1",
				uuid: expect.any(String),
				key: "HomePage",
				type: "page",
			});
			expect(stack.pageStackLength.value).toBe(1);
		});

		it("should add multiple pages in sequence", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");

			expect(stack.pageStackLength.value).toBe(2);
			expect(stack.getCurrentPageInPageStack()?.id).toBe("page2");
		});

		it("should not add duplicate page when already at that page", () => {
			stack.navigateInPageStack("page1", "forward");
			const result = stack.navigateInPageStack("page1", "forward");

			expect(stack.pageStackLength.value).toBe(1);
			expect(result?.id).toBe("page1");
		});

		it("should handle blueprints correctly", () => {
			const result = stack.navigateInPageStack("blueprint1", "forward");

			expect(result?.type).toBe("blueprint");
			expect(result?.key).toBe("UserBlueprint");
		});

		it("should navigate backward in stack", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");

			const result = stack.navigateInPageStack(null, "backward");

			expect(result?.id).toBe("page1");
			expect(activePageId.value).toBe("page1");
		});

		it("should navigate forward in stack", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			stack.navigateInPageStack(null, "backward");

			const result = stack.navigateInPageStack(null, "forward");

			expect(result?.id).toBe("page2");
			expect(activePageId.value).toBe("page2");
		});

		it("should create new branch when navigating from middle of stack", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			stack.navigateInPageStack(null, "backward"); // Go back to page1
			stack.navigateInPageStack("blueprint1", "forward"); // Branch to blueprint

			expect(stack.pageStackLength.value).toBe(2);
			expect(stack.getCurrentPageInPageStack()?.id).toBe("blueprint1");
			expect(stack.canGoForwardInPageStack()).toBe(false);
		});
	});

	describe("canGoBackInPageStack", () => {
		it("should return false for empty stack", () => {
			expect(stack.canGoBackInPageStack()).toBe(false);
		});

		it("should return false for first page in stack", () => {
			stack.navigateInPageStack("page1", "forward");
			expect(stack.canGoBackInPageStack()).toBe(false);
		});

		it("should return true when on second page", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			expect(stack.canGoBackInPageStack()).toBe(true);
		});
	});

	describe("canGoForwardInPageStack", () => {
		it("should return false at end of stack", () => {
			stack.navigateInPageStack("page1", "forward");
			expect(stack.canGoForwardInPageStack()).toBe(false);
		});

		it("should return true after going back", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			stack.navigateInPageStack(null, "backward");

			expect(stack.canGoForwardInPageStack()).toBe(true);
		});
	});

	describe("getPreviousPageInPageStack", () => {
		it("should return null when at first page", () => {
			stack.navigateInPageStack("page1", "forward");
			expect(stack.getPreviousPageInPageStack()).toBeNull();
		});

		it("should return previous page", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");

			const previous = stack.getPreviousPageInPageStack();
			expect(previous?.id).toBe("page1");
		});
	});

	describe("getNextPageInPageStack", () => {
		it("should return null when at end", () => {
			stack.navigateInPageStack("page1", "forward");
			expect(stack.getNextPageInPageStack()).toBeNull();
		});

		it("should return next page after going back", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			stack.navigateInPageStack(null, "backward");

			const next = stack.getNextPageInPageStack();
			expect(next?.id).toBe("page2");
		});
	});

	describe("getCurrentPageInPageStack", () => {
		it("should return null for empty stack", () => {
			expect(stack.getCurrentPageInPageStack()).toBeNull();
		});

		it("should return current page", () => {
			stack.navigateInPageStack("page1", "forward");
			const current = stack.getCurrentPageInPageStack();

			expect(current?.id).toBe("page1");
			expect(current?.key).toBe("HomePage");
		});
	});

	describe("pageStackLength", () => {
		it("should be 0 initially", () => {
			expect(stack.pageStackLength.value).toBe(0);
		});

		it("should update as pages are added", () => {
			stack.navigateInPageStack("page1", "forward");
			expect(stack.pageStackLength.value).toBe(1);

			stack.navigateInPageStack("page2", "forward");
			expect(stack.pageStackLength.value).toBe(2);

			stack.navigateInPageStack("blueprint1", "forward");
			expect(stack.pageStackLength.value).toBe(3);
		});

		it("should shrink when branching from middle", () => {
			stack.navigateInPageStack("page1", "forward");
			stack.navigateInPageStack("page2", "forward");
			stack.navigateInPageStack("blueprint1", "forward");
			expect(stack.pageStackLength.value).toBe(3);

			stack.navigateInPageStack(null, "backward"); // To page2
			stack.navigateInPageStack(null, "backward"); // To page1
			stack.navigateInPageStack("page2", "forward"); // Branch

			expect(stack.pageStackLength.value).toBe(2);
		});
	});
});

