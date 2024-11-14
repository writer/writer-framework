<template>
	<div v-if="isSearchActive" class="BuilderSidebarTitleSearch">
		<input
			ref="searchInput"
			v-model="searchQuery"
			type="text"
			placeholder="Search..."
		/>
		<slot />
		<i
			:class="{ disabled: disabled }"
			class="searchIcon material-symbols-outlined"
			data-writer-tooltip="Close"
			data-writer-tooltip-placement="bottom"
			tabindex="0"
			@keydown.enter="toggleSearch"
			@click="toggleSearch"
		>
			close
		</i>
	</div>
	<div v-else class="BuilderSidebarTitleSearch">
		<i class="material-symbols-outlined">{{ icon }}</i>
		<h3>{{ title }}</h3>
		<i
			data-writer-tooltip="Search"
			data-writer-tooltip-placement="bottom"
			class="searchIcon material-symbols-outlined"
			tabindex="0"
			@keydown.enter="toggleSearch"
			@click="toggleSearch"
		>
			search
		</i>
	</div>
</template>

<script setup lang="ts">
import { nextTick, ref, Ref } from "vue";

defineProps({
	icon: { type: String, required: true },
	title: { type: String, required: true },
	disabled: { type: Boolean, required: false },
});

const searchQuery = defineModel({ type: String, default: "" });

defineEmits({});

const searchInput: Ref<HTMLInputElement> = ref(null);
const isSearchActive: Ref<boolean> = ref(false);

async function toggleSearch() {
	isSearchActive.value = !isSearchActive.value;
	if (isSearchActive.value) {
		await nextTick();
		searchInput.value.focus();
	} else {
		searchQuery.value = "";
	}
}
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarTitleSearch {
	display: flex;
	gap: 8px;
	align-items: center;
	font-size: 1rem;

	background: var(--builderBackgroundColor);
	padding: 16px;
	top: 0;
	position: sticky;
	font-size: 1rem;
}

.BuilderSidebarTitleSearch h3 {
	font-weight: 500;
	font-size: 0.875rem;
	flex-grow: 1;
}

.BuilderSidebarTitleSearch .searchIcon {
	cursor: pointer;
}

.BuilderSidebarTitleSearch .searchIcon.disabled {
	color: var(--builderDisabledColor);
}

.BuilderSidebarTitleSearch input {
	outline: 0;
	border: 0;
	flex-grow: 1;
	width: 50%;
}
</style>
