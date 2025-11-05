<template>
	<label
		ref="dropZoneElement"
		:for="inputId"
		class="SharedDropZone"
		:class="{
			SharedDropZone_active: isOverDropZone.value,
		}"
	>
		<input
			v-show="false"
			:id="inputId"
			type="file"
			:multiple="multiple"
			:accept="acceptAttr"
			@change="onSelectFiles"
		/>
		<div class="SharedDropZone__labelWrapper">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="60"
				height="61"
				viewBox="0 0 60 61"
				class="SharedDropZone__svg"
			>
				<circle
					class="SharedDropZone__svgCircle"
					cx="30"
					cy="30.5"
					r="30"
				/>
				<path
					d="M17.6288 40.455C16.6907 39.2586 15.9316 37.9585 15.3513 36.5546C14.7713 35.1507 14.3873 33.6881 14.1992 32.1667H16.7505C16.9171 33.3611 17.2227 34.5069 17.6671 35.6042C18.1116 36.7014 18.6949 37.7222 19.4171 38.6667L17.6288 40.455ZM14.1992 28.8333C14.4001 27.3119 14.7874 25.8493 15.3613 24.4454C15.9349 23.0415 16.7014 21.7521 17.6609 20.5771L19.4171 22.3333C18.6949 23.2778 18.1116 24.2986 17.6671 25.3958C17.2227 26.4931 16.9171 27.6389 16.7505 28.8333H14.1992ZM28.2505 46.25C26.7291 46.0725 25.2734 45.6926 23.8834 45.1104C22.4934 44.5282 21.197 43.7713 19.9942 42.8396L21.7505 41C22.7227 41.7222 23.7505 42.3194 24.8338 42.7917C25.9171 43.2639 27.056 43.5833 28.2505 43.75V46.25ZM21.8338 19.9679L19.9942 18.1604C21.2248 17.2179 22.542 16.461 23.9459 15.8896C25.3498 15.3179 26.8124 14.9381 28.3338 14.75V17.25C27.1394 17.4167 25.9935 17.7281 24.8963 18.1842C23.7991 18.6406 22.7782 19.2351 21.8338 19.9679ZM31.5838 46.25V43.75C32.7955 43.5833 33.9552 43.2761 35.063 42.8283C36.1707 42.3808 37.2055 41.7821 38.1671 41.0321L40.0067 42.8396C38.7762 43.799 37.452 44.5603 36.0342 45.1233C34.6164 45.6864 33.133 46.0619 31.5838 46.25ZM38.2505 20C37.2782 19.2778 36.2366 18.6806 35.1255 18.2083C34.0144 17.7361 32.8616 17.4167 31.6671 17.25V14.75C33.1885 14.9275 34.6553 15.3047 36.0676 15.8817C37.4801 16.4583 38.7931 17.2179 40.0067 18.1604L38.2505 20ZM42.3401 40.4229L40.5838 38.6667C41.306 37.7222 41.8894 36.7014 42.3338 35.6042C42.7782 34.5069 43.0838 33.3611 43.2505 32.1667H45.8017C45.6009 33.6881 45.2135 35.1507 44.6396 36.5546C44.066 37.9585 43.2995 39.2479 42.3401 40.4229ZM43.2505 28.8333C43.0838 27.6389 42.7782 26.4931 42.3338 25.3958C41.8894 24.2986 41.306 23.2778 40.5838 22.3333L42.3721 20.545C43.3102 21.7414 44.0694 23.0415 44.6496 24.4454C45.2296 25.8493 45.6137 27.3119 45.8017 28.8333H43.2505ZM28.7763 38.2563V27.5321L24.0263 32.2821L22.2696 30.5L30.0263 22.7437L37.7826 30.5L36.0005 32.2563L31.2759 27.5321V38.2563H28.7763Z"
				/>
			</svg>
			<span class="SharedDropZone__label">
				<template v-if="label">{{ label }}</template>
				<template v-else>
					Drag & drop, or <span>browse files</span>
				</template>
			</span>
		</div>
	</label>
</template>

<script setup lang="ts">
import { useTemplateRef, PropType, toRef, useId } from "vue";
import { useDropZone } from "@vueuse/core";
import { useFileTypeAccept } from "@/composables/useFileTypeAccept";

const props = defineProps({
	multiple: {
		type: Boolean,
		default: false,
	},
	acceptedFileTypes: {
		type: Array as PropType<string[]>,
		default: undefined,
	},
	totalSizeLimit: {
		type: Number,
		default: undefined,
	},
	label: {
		type: String,
		default: "",
	},
	restrictions: {
		type: String,
		default: "",
	},
});

const emit = defineEmits({
	drop: (files: File[]) => Array.isArray(files) && files.length > 0,
});

const inputId = useId();

const { acceptAttr, checkIsFileAccepted } = useFileTypeAccept({
	acceptedFileTypes: toRef(props, "acceptedFileTypes"),
});

function emitAcceptedFiles(files: File[]) {
	const acceptedFiles = files.filter((file) => checkIsFileAccepted(file));

	if (acceptedFiles.length > 0) {
		emit(
			"drop",
			props.multiple ? acceptedFiles : acceptedFiles.slice(0, 1),
		);
	}
}

const dropZoneElement = useTemplateRef("dropZoneElement");
const { isOverDropZone } = useDropZone(dropZoneElement, {
	onDrop: (files: File[] | null) => {
		if (Array.isArray(files)) {
			emitAcceptedFiles(files);
		}
	},
});

function onSelectFiles(event: Event): void {
	if (
		event.target instanceof HTMLInputElement &&
		event.target.files instanceof FileList
	) {
		emitAcceptedFiles(Array.from(event.target.files));

		// allows reuploading the same file by resetting the input value
		event.target.value = "";
	}
}
</script>

<style scoped>
.SharedDropZone {
	padding: 12px;
	gap: 16px;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;

	cursor: pointer;

	background-color: var(--wdsColorWhite);
	border-width: 2px;
	border-style: dashed;
	border-color: var(--wdsColorBlue3);
	border-radius: 12px;
	width: 100%;
}

.SharedDropZone__labelWrapper {
	padding: 20px 0;
	gap: 8px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-around;
}

.SharedDropZone__svg {
	fill: var(--wdsColorBlue3);
}

.SharedDropZone__svgCircle {
	fill: var(--wdsColorBlue1);
}

.SharedDropZone__label {
	color: var(--wdsColorBlack);
	font-size: 14px;
	line-height: 180%;
}

.SharedDropZone__label span {
	color: var(--wdsColorBlue5);
}

.SharedDropZone_active {
	border-style: solid;
	background-color: var(--wdsColorBlue1);
	border-color: var(--wdsColorBlue4);
}

.SharedDropZone_active .SharedDropZone__svg {
	fill: var(--wdsColorBlue4);
}

.SharedDropZone_active .SharedDropZone__svgCircle {
	fill: var(--wdsColorBlue2);
}
</style>
