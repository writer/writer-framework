<script setup lang="ts">
import { computed, inject, PropType } from "vue";
import { BUILDER_MANAGER_MODE_ICONS } from "@/constants/icons";
import SharedMoreDropdown, {
	Option,
} from "@/components/shared/SharedMoreDropdown.vue";
import {
	useWriterApiCurrentUserProfile,
	useWriterApiUserProfile,
} from "@/composables/useWriterApiUser";
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
	excerpt: { type: Boolean },
});

const { user: currentUser } = useWriterApiCurrentUserProfile();

const emits = defineEmits({
	select: () => true,
	edit: () => true,
	delete: () => true,
});

const notesManager = inject(injectionKeys.notesManager);

const { createdAtFormatted, type, content, createdBy } =
	notesManager.useNoteInformation(computed(() => props.component));

const {
	user,
	isLoading: isLoadingUser,
	error: isLoadingUserError,
} = useWriterApiUserProfile(createdBy);
const displayUserLoader = computed(
	() => isLoadingUser.value || isLoadingUserError.value,
);

const contentExcerpt = computed(() => {
	if (content.value.length < 100) return content.value;
	const exerpt = content.value.slice(0, 100);
	return `${exerpt}...`;
});

const contentParagraphs = computed(() => content.value.split("\n"));

const avatarUrl = computed(() => user.value?.avatar ?? "");
const completeName = computed(() => {
	if (!user.value) return "";
	return [user.value.firstName, user.value.lastName]
		.filter(Boolean)
		.join(" ");
});

const dropdownOptions = computed<Option[]>(() => {
	if (currentUser.value?.id !== createdBy.value) return undefined;

	return [
		{
			value: "edit",
			label: "Edit",
			icon: "edit",
		},
		{
			value: "delete",
			label: "Delete",
			icon: "delete",
			variant: "danger",
		},
	];
});

function onDropdownSelect(value: string) {
	switch (value) {
		case "edit":
			return emits("edit");
		case "delete":
			return emits("delete");
	}
}
</script>

<template>
	<div
		class="BuilderSidebarNote"
		:data-note-id="component.id"
		tabindex="0"
		@click="$emit('select')"
	>
		<div class="BuilderSidebarNote__header">
			<div class="BuilderSidebarNote__header__avatar">
				<div class="BuilderSidebarNote__header__avatar__type">
					<i class="icon material-symbols-outlined">{{
						BUILDER_MANAGER_MODE_ICONS[type]
					}}</i>
				</div>
				<WdsSkeletonLoader
					v-if="displayUserLoader || !avatarUrl"
					class="BuilderSidebarNote__header__avatar__loader"
				/>
				<img v-else :src="avatarUrl" />
			</div>

			<div class="BuilderSidebarNote__header__info">
				<WdsSkeletonLoader
					v-if="displayUserLoader"
					class="BuilderSidebarNote__header__info__loader"
				/>
				<p v-else>{{ completeName }}</p>
				<p>{{ createdAtFormatted }}</p>
			</div>

			<div
				v-if="dropdownOptions"
				class="BuilderSidebarNote__header__actions"
			>
				<SharedMoreDropdown
					:options="dropdownOptions"
					trigger-custom-size="16px"
					@select="onDropdownSelect"
				/>
			</div>
		</div>
		<div v-if="content" class="BuilderSidebarNote__content">
			<p v-if="excerpt">{{ contentExcerpt }}</p>
			<p v-for="(paragraph, i) of contentParagraphs" v-else :key="i">
				{{ paragraph }}
			</p>
		</div>
	</div>
</template>

<style scoped>
.BuilderSidebarNote {
	cursor: pointer;
	display: flex;
	flex-direction: column;
	gap: 16px;
}
.BuilderSidebarNote__header {
	display: grid;
	grid-template-columns: auto 1fr auto;
	gap: 8px;
}

.BuilderSidebarNote__header__avatar {
	position: relative;
	display: flex;
	align-items: center;
}

.BuilderSidebarNote__header__avatar__type {
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
.BuilderSidebarNote__header__avatar img,
.BuilderSidebarNote__header__avatar__loader {
	border-radius: 50%;
	height: 32px;
	width: 32px;
}
.BuilderSidebarNote__header__info {
	display: flex;
	flex-direction: column;
	gap: 2px;
	font-size: 10px;
	font-weight: 500;
	color: var(--wdsColorGray4);
}
.BuilderSidebarNote__header__info__loader {
	/* takes extra space to avoid layout shift */
	margin-top: 3px;
	margin-bottom: 4px;
}
.BuilderSidebarNote__header__actions {
	display: flex;
	align-items: center;
}

.BuilderSidebarNote__content {
	display: flex;
	flex-direction: column;
	gap: 8px;
	font-size: 12;
}
</style>
