<script lang="ts" setup>
/**
 * This component will avoid render the slot "content" until it's visible (relying on `IntersectionObserver`)
 */
import { onUnmounted, ref, useTemplateRef, watch } from "vue";

const container = useTemplateRef("container");
const isVisible = ref(false);
const currentObserver = ref<IntersectionObserver | undefined>();

function observeVisibility(element: Element) {
	// close the old IntersectionObserver if exists
	currentObserver.value?.disconnect();

	const observer = new IntersectionObserver((entries) => {
		// check if any observed elements are visible
		const visible = entries.some((entry) => entry.isIntersecting);
		if (!visible) return;

		// the element is visible, we don't need the observer anymore
		observer.unobserve(element);
		isVisible.value = true;
	});

	// observe the element and save the observer to close it if necessary
	observer.observe(element);
	currentObserver.value = observer;
}

watch(
	container,
	() => {
		// handle if the browser doesn't support IntersectionObserver
		if (!window.IntersectionObserver) return (isVisible.value = true);
		// if HTML ref exists, start to observe visibility
		if (container.value) observeVisibility(container.value);
	},
	{ immediate: true },
);

// be sure to close IntersectionObserver if component is destroyed
onUnmounted(() => currentObserver.value?.disconnect());
</script>

<template>
	<div ref="container" class="SharedLazyLoader">
		<slot v-if="isVisible" name="content" />
		<slot v-else name="spinner" />
	</div>
</template>
