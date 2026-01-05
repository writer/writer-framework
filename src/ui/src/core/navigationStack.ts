import { computed, type Ref, ref } from "vue";
import type { Component } from "@/writerTypes";

export type NavigationStackItem = {
	id: Component["id"];
	uuid: string;
	key: string;
	type: "page" | "blueprint";
};

export function createNavigationStack(
	activePageId: Ref<Component["id"] | undefined>,
	getComponentById: (id: Component["id"]) => Component | undefined,
) {
	const pageStack = ref<NavigationStackItem[]>([]);
	// needed to keep track of navigation stack
	const currentPageStackItem: Ref<{ uuid: string | undefined }> = ref({
		uuid: undefined,
	});

	const pageStackLength = computed(() => pageStack.value.length);

	/**
	 * Helper to create a stack item
	 */
	function createStackItem(id: Component["id"]): NavigationStackItem {
		const component = getComponentById(id);
		const uuid = window.crypto?.randomUUID() ?? `uuid-${Date.now()}`;
		return {
			id,
			uuid,
			key: component?.content?.key ?? id,
			type: component.type === "page" ? "page" : "blueprint",
		};
	}

	/**
	 * Find the current index in the page stack
	 */
	function getCurrentIndex(): number {
		return pageStack.value.findIndex(
			(item) =>
				item.uuid === currentPageStackItem.value.uuid ||
				(item.id === activePageId.value &&
					currentPageStackItem.value.uuid === undefined),
		);
	}

	/**
	 * Navigate in the page stack
	 */
	function navigateInPageStack(
		pageId: Component["id"] | null = null,
		direction: "forward" | "backward" = "forward",
	): NavigationStackItem | null {
		const currentIdx = getCurrentIndex();

		// Backward navigation - simple case
		if (direction === "backward") {
			if (currentIdx > 0) {
				const previousItem = pageStack.value[currentIdx - 1];
				activePageId.value = previousItem.id;
				currentPageStackItem.value.uuid = previousItem.uuid;
			}
			return getCurrentPageInPageStack();
		}

		// Forward navigation without specific pageId - navigate to next in stack
		if (pageId === null) {
			if (currentIdx + 1 < pageStack.value.length) {
				const nextItem = pageStack.value[currentIdx + 1];
				activePageId.value = nextItem.id;
				currentPageStackItem.value.uuid = nextItem.uuid;
			}
			return getCurrentPageInPageStack();
		}

		// Forward navigation with specific pageId
		const newItem = createStackItem(pageId);

		// Not in stack yet - add it
		if (currentIdx === -1) {
			currentPageStackItem.value.uuid = newItem.uuid;
			pageStack.value.push(newItem);
			return getCurrentPageInPageStack();
		}

		// Already at this page - no change needed
		if (pageStack.value[currentIdx].id === pageId) {
			return getCurrentPageInPageStack();
		}

		// In middle of stack - branch by replacing everything after current position
		if (currentIdx + 1 < pageStack.value.length) {
			currentPageStackItem.value.uuid = newItem.uuid;
			pageStack.value.splice(
				currentIdx + 1,
				pageStack.value.length - currentIdx - 1,
				newItem,
			);
			return getCurrentPageInPageStack();
		}

		// At end of stack - add if different from last page
		const lastPage = pageStack.value[pageStack.value.length - 1];
		if (lastPage.id !== pageId) {
			currentPageStackItem.value.uuid = newItem.uuid;
			pageStack.value.push(newItem);
		}

		return getCurrentPageInPageStack();
	}

	function canGoBackInPageStack() {
		return (
			pageStack.value.findIndex(
				(item) => item.uuid === currentPageStackItem.value.uuid,
			) > 0
		);
	}

	function canGoForwardInPageStack() {
		return (
			pageStack.value.findIndex(
				(item) => item.uuid === currentPageStackItem.value.uuid,
			) +
				1 <
			pageStack.value.length
		);
	}

	function getPreviousPageInPageStack() {
		const currentIdx = pageStack.value.findIndex(
			(item) => item.uuid === currentPageStackItem.value.uuid,
		);
		if (currentIdx > 0) {
			return pageStack.value[currentIdx - 1];
		}
		return null;
	}

	function getNextPageInPageStack() {
		const currentIdx = pageStack.value.findIndex(
			(item) => item.uuid === currentPageStackItem.value.uuid,
		);
		if (currentIdx + 1 < pageStack.value.length) {
			return pageStack.value[currentIdx + 1];
		}
		return null;
	}

	function getCurrentPageInPageStack() {
		const currentIdx = pageStack.value.findIndex(
			(item) => item.uuid === currentPageStackItem.value.uuid,
		);
		if (currentIdx >= 0) {
			return pageStack.value[currentIdx];
		}
		return null;
	}

	return {
		pageStack,
		currentPageStackItem,
		pageStackLength,
		navigateInPageStack,
		canGoBackInPageStack,
		canGoForwardInPageStack,
		getPreviousPageInPageStack,
		getNextPageInPageStack,
		getCurrentPageInPageStack,
	};
}
