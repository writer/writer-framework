<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from "vue";

const props = defineProps({
	value: {
		validator: (v) => typeof v === "number" || typeof v === "bigint",
		required: true,
	},
	editable: { type: Boolean, required: false },
});

const emits = defineEmits({
	change: (value: string) => typeof value === "string",
});

const wrapper = useTemplateRef("wrapper");
const input = useTemplateRef("input");
const isEditing = ref(false);

async function startEditing() {
	if (!props.editable) return false;
	isEditing.value = true;
	// focus on the input when it renders
	await nextTick();
	input.value.focus();
}

function stopEditing() {
	isEditing.value = false;
	const newValue = Number(input.value.value);
	if (newValue === props.value) return;
	emits("change", input.value.value);
}
</script>

<template>
	<div
		ref="wrapper"
		class="CoreDataframeCellNumber"
		:class="{ 'CoreDataframeCellNumber--editable': editable }"
		:tabindex="editable && !isEditing ? 0 : -1"
		@focusin="startEditing"
		@click="startEditing"
	>
		<input
			v-if="isEditing"
			ref="input"
			type="number"
			:value="value"
			@focusout="stopEditing"
		/>
		<template v-else>
			{{ value }}
		</template>
	</div>
</template>

<style scoped>
.CoreDataframeCellNumber--editable {
	cursor: pointer;
}
.CoreDataframeCellNumber input {
	width: 100%;
	font-size: 0.75rem;

	border: unset;
	resize: vertical;
}
.CoreDataframeCellNumber input:focus {
	border: unset;
	outline: 1px solid var(--accentColor);
}
</style>
