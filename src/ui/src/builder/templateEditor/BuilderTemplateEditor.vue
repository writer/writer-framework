<script lang="ts" setup>
import injectionKeys from "@/injectionKeys";
import { computed, inject, watch } from "vue";
import { useDynamicUserState } from "../useDynamicUserState";
import { WdsColor } from "@/wds/tokens";
import { extractObjectPaths } from "@/utils/object";
import { EditorContent, useEditor } from "@tiptap/vue-3";
import Paragraph from "@tiptap/extension-paragraph";
import Document from "@tiptap/extension-document";
import HardBreak from "@tiptap/extension-hard-break";
import Text from "@tiptap/extension-text";
import { UndoRedo } from "@tiptap/extensions";
import { Extension } from "@tiptap/core";
import { Plugin } from "@tiptap/pm/state";
import type { Node } from "@tiptap/pm/model";
import { Decoration, DecorationSet } from "@tiptap/pm/view";
import { TEMPLATE_REGEX } from "@/renderer/useEvaluator";

const wf = inject(injectionKeys.core);
const secretsManager = inject(injectionKeys.secretsManager);

const model = defineModel({ type: String });

const props = defineProps({
	multiline: { type: Boolean, required: false },
});

defineExpose({
	focus,
	getSelection,
	setSelectionEnd,
	setSelectionStart,
});

const { bindings, blueprintsResults, blueprintsSetStates } =
	useDynamicUserState(wf);

const backgroundTagColors = computed(() => ({
	[WdsColor.Green2]: [...extractObjectPaths(wf.userState.value)],
	[WdsColor.Gray2]: [...extractObjectPaths(bindings.value)],
	[WdsColor.Blue2]: [
		...extractObjectPaths(blueprintsSetStates.value),
		...extractObjectPaths(blueprintsResults.value),
	],
	[WdsColor.Yellow2]: [
		...extractObjectPaths(secretsManager.secrets.value),
	].map((v) => `vault.${v}`),
}));

const templateRegex = new RegExp(TEMPLATE_REGEX.source, "g");

function findTemplateTags(doc: Node): DecorationSet {
	const decorations: Decoration[] = [];

	doc.descendants((node, position) => {
		if (!node.text) return;

		templateRegex.lastIndex = 0;

		Array.from(node.text.matchAll(templateRegex)).forEach((match) => {
			const tag = match[1];

			const color = Object.entries(backgroundTagColors.value)
				.find(([, tags]) =>
					tags.some((t) => t === tag || tag.startsWith(`${t}.`)),
				)
				?.pop();

			const index = match.index || 0;
			const from = position + index;
			const to = from + match[0].length;
			const decoration = Decoration.inline(from, to, {
				class: "BuilderTemplateEditorInterpolation",
				style: color ? `background-color: ${color}` : undefined,
			});

			decorations.push(decoration);
		});
	});

	return DecorationSet.create(doc, decorations);
}

const Interpolation = Extension.create({
	name: "interpolation",

	addProseMirrorPlugins() {
		return [
			new Plugin({
				state: {
					init(_, { doc }) {
						return findTemplateTags(doc);
					},
					apply(transaction, oldState) {
						return transaction.docChanged
							? findTemplateTags(transaction.doc)
							: oldState;
					},
				},
				props: {
					decorations(state) {
						return this.getState(state);
					},
				},
			}),
		];
	},
});

const editorExtensions = [Paragraph, Interpolation, Text, UndoRedo];
if (props.multiline) {
	editorExtensions.push(
		Document,
		HardBreak.extend({
			addKeyboardShortcuts() {
				return {
					Enter: () => this.editor.commands.setHardBreak(),
				};
			},
		}),
	);
} else {
	editorExtensions.push(Document.extend({ content: "block" }));
}

const editor = useEditor({
	extensions: editorExtensions,
	content: model.value,
	editorProps: {
		attributes: {
			"data-automation-key": "template-editor",
		},
	},
	parseOptions: {
		preserveWhitespace: "full",
	},
	onUpdate(props) {
		const text = props.editor.getText();
		if (model.value !== text) model.value = text;
	},
});

watch(model, () => {
	const isSame = editor.value.getText() === model.value;
	if (!isSame) {
		editor.value.commands.setContent(model.value, {
			parseOptions: { preserveWhitespace: "full" },
		});
	}
});

function setSelectionStart(value: number) {
	editor.value.commands.setTextSelection(value);
}
function setSelectionEnd(value: number) {
	editor.value.commands.setTextSelection(value);
}

function getSelection() {
	const selection = editor.value.state.selection;
	return {
		selectionStart: selection.from,
		selectionEnd: selection.to,
	};
}

function focus() {
	editor.value.commands.focus();
}
</script>

<template>
	<EditorContent
		ref="input"
		v-model="model"
		class="BuilderTemplateEditor"
		:editor="editor"
	/>
</template>

<style scoped>
.BuilderTemplateEditor:deep(.tiptap:focus-visible) {
	outline: none;
}
.BuilderTemplateEditor:deep(.BuilderTemplateEditorInterpolation) {
	background-color: var(--wdsColorGray1);
	color: var(--wdsColorBlack);
	padding: 2px 8px;
	border-radius: 4px;
}
</style>
