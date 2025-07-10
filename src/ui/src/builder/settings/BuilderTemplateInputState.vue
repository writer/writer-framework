<template>
	<WdsTextInputLayout
		class="BuilderTemplateInputState"
		:left-icon="displayEmptyVariant ? 'alternate_email' : undefined"
		:right-icon="rightIcon"
		@right-icon-click="$emit('rightIconClick')"
		@click="input.focus()"
	>
		<div class="BuilderTemplateInputState__content">
			<div
				class="BuilderTemplateInputState__content__tag"
				:style="tagStyle"
			>
				<span>@</span>
				<input
					ref="input"
					v-model="model"
					type="text"
					@focus="hasFocus = true"
					@blur="hasFocus = false"
				/>
			</div>
		</div>
	</WdsTextInputLayout>
</template>

<script setup lang="ts">
import { computed, CSSProperties, inject, ref, useTemplateRef } from "vue";
import WdsTextInputLayout from "@/wds/WdsTextInputLayout.vue";
import injectionKeys from "@/injectionKeys";
import { extractObjectPaths } from "@/utils/object";
import { WdsColor } from "@/wds/tokens";

defineProps({
	rightIcon: { type: String, required: false, default: undefined },
});

defineEmits({
	rightIconClick: () => true,
});

defineExpose({
	focus,
	setSelectionStart,
	setSelectionEnd,
	getSelection,
});

const wf = inject(injectionKeys.core);

const input = useTemplateRef("input");

const model = defineModel({ type: String });

const hasFocus = ref(false);

const displayEmptyVariant = computed(() => !model.value && !hasFocus.value);

const userStatePath = computed(
	() => new Set(extractObjectPaths(wf.userStateInitial.value)),
);

const tagStyle = computed<CSSProperties>(() => {
	return {
		opacity: displayEmptyVariant.value ? 0 : undefined,
		backgroundColor: userStatePath.value.has(model.value)
			? WdsColor.Green2
			: WdsColor.Gray1,
	};
});

function setSelectionStart(value: number) {
	if (input.value) input.value.selectionStart = value;
}
function setSelectionEnd(value: number) {
	if (input.value) input.value.selectionEnd = value;
}

function getSelection() {
	return {
		selectionStart: input.value?.selectionStart,
		selectionEnd: input.value?.selectionEnd,
	};
}

function focus() {
	input.value?.focus();
}
</script>

<style scoped>
.BuilderTemplateInputState {
	padding-top: 6px;
	padding-bottom: 6px;
}

.BuilderTemplateInputState__content {
	display: grid;
	grid-template-columns: minmax(0, auto) 1fr;
	width: 100%;
}
.BuilderTemplateInputState__content__tag {
	display: grid;
	grid-template-columns: auto minmax(0, 1fr);
	align-items: baseline;
	gap: 4px;
	background-color: var(--wdsColorBlue2);
	padding: 2px 8px;
	border-radius: 4px;
}
.BuilderTemplateInputState__content__tag input {
	background-color: transparent;
	border: none;
	field-sizing: content;
}
.BuilderTemplateInputState__content__tag input:focus {
	outline: none;
}
</style>
