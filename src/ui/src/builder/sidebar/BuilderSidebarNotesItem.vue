<template>
	<li
		:key="component.id"
		class="BuilderSidebarNotesItem"
		:data-note-id="component.id"
		tabindex="0"
	>
		<div class="BuilderSidebarNotesItem__header">
			<div class="BuilderSidebarNotesItem__avatar">
				<div class="BuilderSidebarNotesItem__avatar__type">
					<i class="icon material-symbols-outlined"
						>linked_services</i
					>
				</div>
				<img src="https://picsum.photos/100" />
			</div>

			<p class="BuilderSidebarNotesItem__header__info">
				Pete
				<br />
				Jan 13 08:23pm
			</p>
			<div class="BuilderSidebarNotesItem__header__actions">
				<SharedMoreDropdown :options="[]" trigger-custom-size="16px" />
			</div>
		</div>

		Note : {{ component.id }}
	</li>
</template>

<script setup lang="ts">
import { PropType } from "vue";
import { Component } from "@/writerTypes";
import SharedMoreDropdown from "@/components/shared/SharedMoreDropdown.vue";

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
});

console.log(props.component.content);
</script>

<style scoped>
.BuilderSidebarNotesItem {
	border-bottom: 1px solid var(--wdsColorGray2);
	cursor: pointer;
	padding: 16px;
}
.BuilderSidebarNotesItem:hover {
	background-color: var(--wdsColorBlue1);
}

.BuilderSidebarNotesItem__header {
	display: grid;
	grid-template-columns: auto 1fr auto;
	gap: 8px;
}

.BuilderSidebarNotesItem__avatar {
	position: relative;
}

.BuilderSidebarNotesItem__avatar__type {
	position: absolute;
	background-color: white;
	display: block;
	height: 22px;
	width: 22px;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 1px solid var(--wdsColorGray2);
	transform: translate(-50%, -50%);
}
.BuilderSidebarNotesItem__avatar img {
	border-radius: 50%;
	height: 32px;
	width: 32px;
}
</style>
