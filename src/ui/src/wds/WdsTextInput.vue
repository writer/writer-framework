<template>
	<div
		v-if="leftIcon"
		class="WdsTextInput WdsTextInput--leftIcon"
		@click="input.focus()"
	>
		<i class="material-symbols-outlined">{{ leftIcon }}</i>
		<input
			ref="input"
			v-model="model"
			type="text"
			:placeholder="placeholder"
		/>
	</div>
	<input v-else v-model="model" type="text" class="WdsTextInput" />
</template>

<script setup lang="ts">
import { ref } from "vue";

const model = defineModel({ type: String });

defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	placeholder: { type: String, required: false, default: undefined },
});

const input = ref();
</script>

<style scoped>
.WdsTextInput {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
	color: var(--primaryTextColor);
	background: transparent;
}

.WdsTextInput:focus,
.WdsTextInput--leftIcon:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.WdsTextInput--leftIcon {
	cursor: pointer;
	display: flex;
	gap: 8px;
}

.WdsTextInput--leftIcon i {
	color: #4f4f4f;
}

.WdsTextInput--leftIcon input {
	border: none;
}
.WdsTextInput--leftIcon input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}
</style>
