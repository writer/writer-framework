<script lang="ts" setup>
import { onUpdated, useTemplateRef } from "vue";

const props = defineProps({
	multiline: { type: Boolean, required: false },
});

const root = useTemplateRef("root");

let previousSelection: number | undefined = undefined;

const emits = defineEmits({
	input: (value: string) => typeof value === "string",
});

async function onChange(e: Event) {
	if (!(e.target instanceof HTMLElement)) return;
	previousSelection = getSelection();
	const text = e.target.innerText || "";
	emits("input", text);
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
	if (previousSelection !== undefined) setSelection(previousSelection);
});

function getSelection() {
	if (!root.value) return;

	const selection = window.getSelection();
	if (selection === null) {
		return;
	}
	if (!selection.rangeCount) return -1;

	const range = selection.getRangeAt(0);
	let position = 0;

	const walker = document.createTreeWalker(
		root.value,
		NodeFilter.SHOW_ALL,
		null,
	);
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
			if (
				range.startContainer === node.parentNode &&
				Array.from(node.parentNode.childNodes).indexOf(
					node as ChildNode,
				) <= range.startOffset
			) {
				position += 1; // Count <br> as one character
			} else if (range.startContainer === node) {
				return position;
			} else {
				position += 1;
			}
		}
	}
	return undefined;
}

function setSelection(targetOffset: number) {
	if (!root.value) return;
	console.log("setSelection", targetOffset);
	previousSelection = targetOffset;

	const walker = document.createTreeWalker(
		root.value,
		NodeFilter.SHOW_ALL,
		null,
	);
	let position = 0;

	while (walker.nextNode()) {
		const node = walker.currentNode;

		if (node.nodeType === Node.TEXT_NODE) {
			const textLength = node.textContent?.length ?? 0;
			if (targetOffset <= position + textLength) {
				const range = document.createRange();
				range.setStart(node, targetOffset - position);
				range.collapse(true);
				const sel = window.getSelection();
				if (sel === null) throw Error("could not get selection");
				sel.removeAllRanges();
				sel.addRange(range);
				return;
			}
			position += textLength;
		}

		if (node.nodeType === Node.ELEMENT_NODE && node.nodeName === "BR") {
			if (position === targetOffset) {
				const range = document.createRange();
				range.setStartAfter(node);
				range.collapse(true);
				const sel = window.getSelection();
				if (sel === null) throw Error("could not get selection");
				sel.removeAllRanges();
				sel.addRange(range);
				return;
			}
			position += 1; // Count <br> as one char
		}
	}
}

function onPressEnter(e: KeyboardEvent) {
	e.preventDefault();
	if (!props.multiline) return;
	if (!(e.target instanceof HTMLElement)) return;
	const text = e.target.innerText || "";
	const selection = getSelection();
	if (selection === undefined) return emits("input", `${text}\n`);

	const before = text.slice(0, selection);
	const after = text.slice(selection);

	previousSelection = selection + 1;
	emits("input", `${before}\n${after}`);
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
