<script lang="ts" setup>
import { nextTick, onUpdated, ref, useTemplateRef } from "vue";

const props = defineProps({
	multiline: { type: Boolean, required: false },
});

const root = useTemplateRef("root");

let previousSelection = ref<number | undefined>();

const emits = defineEmits({
	input: (value: string) => typeof value === "string",
});

async function onChange(e: Event) {
	if (!(e.target instanceof HTMLElement)) return;
	previousSelection.value = getSelection();
	const text = e.target.innerText || "";
	if (props.multiline) {
		emits("input", text);
	} else {
		emits("input", text.replace("\n", ""));
	}
}
async function onPressDelete(e: KeyboardEvent) {
	if (!(e.target instanceof HTMLElement)) return;
	const text = e.target.innerText || "";
	if (text.length <= 1) {
		// prevent deleting the node
		e.preventDefault();
		emits("input", "");
	}
}

onUpdated(() => {
	if (previousSelection.value !== undefined)
		setSelection(previousSelection.value);
});

function getSelection() {
	if (!root.value) return undefined;

	const selection = window.getSelection();
	if (selection === null) return undefined;
	if (!selection.rangeCount) return undefined;

	const range = selection.getRangeAt(0);
	let position = 0;

	const walker = document.createTreeWalker(root.value, NodeFilter.SHOW_ALL);
	while (walker.nextNode()) {
		const node = walker.currentNode;

		if (node.nodeType === Node.TEXT_NODE) {
			if (range.startContainer === node) {
				return position + range.startOffset;
			}
			position += node.textContent?.length ?? 0;
		} else if (
			node.nodeType === Node.ELEMENT_NODE &&
			node.nodeName === "BR"
		) {
			if (range.startContainer === node.parentNode) {
				const siblings = Array.from(node.parentNode.childNodes);
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				const index = siblings.indexOf(node as any);
				if (index >= 0 && index < range.startOffset) {
					position += 1;
				} else if (index === range.startOffset) {
					return position;
				}
			}

			// If the range is directly at the <br> element itself
			if (range.startContainer === node) {
				return position;
			}

			position += 1;
		}
	}
	return undefined;
}

function setSelection(targetOffset: number) {
	if (!root.value) return;
	previousSelection.value = targetOffset;

	const walker = document.createTreeWalker(root.value, NodeFilter.SHOW_ALL);
	let position = 0;

	function setSelectionRange(range: Range) {
		const sel = window.getSelection();
		if (sel === null) throw Error("could not get selection");
		sel.removeAllRanges();
		sel.addRange(range);
	}

	while (walker.nextNode()) {
		const node = walker.currentNode;

		if (node.nodeType === Node.TEXT_NODE) {
			const textLength = node.textContent?.length ?? 0;
			if (targetOffset <= position + textLength) {
				const range = document.createRange();
				range.setStart(node, targetOffset - position);
				range.collapse(true);
				return setSelectionRange(range);
			}
			position += textLength;
		}

		if (node.nodeType === Node.ELEMENT_NODE && node.nodeName === "BR") {
			if (position === targetOffset) {
				const range = document.createRange();
				range.setStartAfter(node);
				range.collapse(true);
				return setSelectionRange(range);
			}
			position += 1; // Count <br> as one char
		}
	}

	// if we traversed the DOM and the requested position is too far, we fallback to the last position
	if (position < targetOffset) {
		const child = root.value.children[0];
		if (!child) return;
		previousSelection.value = position;
		const range = document.createRange();
		range.setStartAfter(child);
		setSelectionRange(range);
	}
}

async function onPressEnter(e: KeyboardEvent) {
	e.preventDefault();
	if (!props.multiline) return;
	if (!(e.target instanceof HTMLElement)) return;
	const text = e.target.innerText || "";
	const selection = getSelection();
	if (selection === undefined) return emits("input", `${text}\n`);

	const before = text.slice(0, selection);
	const after = text.slice(selection);

	previousSelection.value = selection + 1;
	emits("input", `${before}\n${after}`);
	await nextTick();
	setSelection(previousSelection.value);
}

function focus() {
	root.value?.focus();
}

defineExpose({ setSelection, getSelection, focus });
</script>

<template>
	<div
		ref="root"
		class="SharedContentEditable"
		contenteditable="true"
		role="textbox"
		@click="focus"
		@input="onChange"
		@keydown.enter.prevent="onPressEnter"
		@keydown.delete="onPressDelete"
	>
		<slot />
	</div>
</template>
