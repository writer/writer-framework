<template>
	<!-- inspired from https://andrejgajdos.com/custom-select-dropdown -->
	<div class="select-wrapper" v-on:click="open">
		<div class="select" ref="selectEl">
			<div class="select__trigger">
				<div class="select__content">
					<div v-if="currentLabel != null" class="frow">
						<div><i class="ri-split-cells-horizontal"></i></div>
						<div>{{currentLabel}}</div>
					</div>
				</div>
				<div class="arrow"><i class="ri-arrow-down-s-fill"></i></div>
			</div>
			<div class="custom-options">
				<div class="custom-option" v-for="option in options" :data-value="option.value" @click="select" :class="option.class">
					<div class="frow">
						<div><i class="ri-split-cells-horizontal"></i></div>
						<div>{{option.label}}</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import {computed, ref, Ref} from "vue";

const props = defineProps<{
	value?: string;
}>();

let currentValue = ref(props.value);
const currentLabel = computed(() => {
	const option = options.value.find((option) => option.value == currentValue.value);
	return option ? option.label : '';
});

const emit = defineEmits(['select'])

const options_list = [
	{ value: "fit-content", label: 'Fit content', class: "" },
	{ value: "full", label: 'Full', class: "" },
	{ value: 'fixed', label: 'Fixed', class: "" },
];

let options = computed(() => {
	options_list.forEach((option) => {
		if (option.value == currentValue) {
			option.class = "selected";
		} else {
			option.class = "";
		}
	})

	return options_list
})


const selectEl: Ref<HTMLElement> = ref(null);

const open = () => {
	selectEl.value.classList.toggle('open');
}

const select = (event) => {
	const value = event.currentTarget.getAttribute('data-value');
	currentValue.value = value;
	emit('select', value);
}

</script>

<style scoped>
.select-wrapper {
    position: relative;
    user-select: none;
    width: 100%;
}

.select {
    position: relative;
    display: flex;
    flex-direction: column;
}

.select__trigger {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    font-weight: 400;
    color: #3b3b3b;
    height: 32px;
    background: #ffffff;
    cursor: pointer;
}

.custom-options {
    position: absolute;
    display: block;
    top: 100%;
    left: 0;
    right: 0;
    border: 1px solid #394a6d;
    background: #fff;
    transition: all 0.2s;
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    z-index: 2;
}

.select.open .custom-options {
    opacity: 1;
    visibility: visible;
    pointer-events: all;
}

.custom-option {
    position: relative;
    display: block;
    padding: 8px;
    font-weight: 400;
    color: #000000e6;
    cursor: pointer;
    transition: all 0.2s;
}

.custom-option:hover {
    cursor: pointer;
    background-color: #000000b3;
    color: #fff
}

.selected {
    background-color: #000000b3;
    color: #fff
}

.arrow {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 300;
    color: #000000e6;
}


.frow {
    display: flex;
    flex-direction: row;
    gap: 8px;
}
</style>