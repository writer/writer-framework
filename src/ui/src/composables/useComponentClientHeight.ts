import { ref, onMounted, onUnmounted, ShallowRef } from "vue";

/**
 * Composable function to calculate the height of a DOM element and update it regularly
 */
export function useElementClientHeight(
	elementRef: ShallowRef<HTMLDivElement>,
	intervalMs = 500,
) {
	const height = ref(0);
	let intervalId = null;

	function updateHeight() {
		if (elementRef.value) {
			height.value = elementRef.value.clientHeight;
		}
	}

	onMounted(() => {
		updateHeight();
		intervalId = setInterval(updateHeight, intervalMs);
	});

	onUnmounted(() => {
		if (!intervalId) return;
		clearInterval(intervalId);
	});

	return height;
}
