import { Ref, ref, onUnmounted, computed } from "vue";

/**
 * Watch the bounding client rect of an element using `setInterval`
 */
export function useBoundingClientRect(htmlRef: Ref<Element>, ms = 500) {
	const rect = ref<DOMRect>();

	const id = setInterval(() => {
		rect.value = htmlRef.value?.getBoundingClientRect();
	}, ms);

	onUnmounted(() => {
		clearInterval(id);
	});

	return computed(() => rect.value);
}
