<script lang="ts" setup>
const props = defineProps({
	disabled: { type: Boolean, required: false, default: false },
});

const checked = defineModel({ type: Boolean, default: false });

function handleToggle() {
	if (!props.disabled) {
		checked.value = !checked.value;
	}
}
</script>

<template>
	<div
		class="WdsSwitch"
		:class="{
			'WdsSwitch--on': checked,
			'WdsSwitch--disabled': disabled,
		}"
		role="switch"
		:aria-checked="checked"
		:tabindex="disabled ? -1 : 0"
		@click="handleToggle"
		@keydown.enter.space.prevent="handleToggle"
	>
		<div class="WdsSwitch__toggle"></div>
	</div>
</template>

<style scoped>
.WdsSwitch {
	background: var(--wdsColorGray3);
	width: 34px;
	height: 14px;
	border-radius: 14px;
	cursor: pointer;
	position: relative;
	transition: background-color 0.2s ease-in-out;
}

.WdsSwitch:focus-visible {
	outline: 2px solid var(--wdsColorBlue3);
	outline-offset: 2px;
}

.WdsSwitch--on {
	background: var(--wdsColorBlue3);
}

.WdsSwitch--disabled {
	opacity: 0.4;
	cursor: not-allowed;
}

.WdsSwitch__toggle {
	position: absolute;
	top: -3px;
	left: 0;
	width: 20px;
	height: 20px;
	background: var(--wdsColorGray4);
	border-radius: 10px;
	transition: all 0.2s ease-in-out;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.WdsSwitch--on .WdsSwitch__toggle {
	left: 16px;
	background: var(--wdsColorBlue5);
}

.WdsSwitch:hover:not(.WdsSwitch--disabled) .WdsSwitch__toggle {
	box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
</style>
