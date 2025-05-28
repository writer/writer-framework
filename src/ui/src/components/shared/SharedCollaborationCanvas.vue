<template>
	<div
		class="SharedCollaborationCanvas"
		:style="{ transform: `scale(${props.zoomLevel})` }"
		@mousemove="updatePosition"
	>
		<template v-for="user in users" :key="user.userId">
			<div class="userTag"></div>
			<div
				class="user"
				:style="{
					top: `${user.y - renderOffset.y}px`,
					left: `${user.x - renderOffset.x}px`,
				}"
			>
				user {{ user.userId }}
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import { UserCollaborationPing } from "@/writerTypes";

const outgoingPing: UserCollaborationPing = {
	x: null,
	y: null,
};

const props = defineProps<{
	renderOffset: { x: number; y: number };
	zoomLevel: number;
}>();

const emit = defineEmits({
	toggle: (open: boolean) => typeof open === "boolean",
});

const users = [{ componentId: "k7kdqwxfn5ea5ubv", userId: 12, x: 90, y: 90 }];

function updatePosition(event: MouseEvent) {
	outgoingPing.x = event.clientX;
	outgoingPing.y = event.clientY;
}
</script>

<style scoped>
.SharedCollaborationCanvas {
	width: 100%;
	height: 100%;
	position: absolute;
	top: 0;
	left: 0;
	pointer-events: none;
	transform-origin: top left;
}

.user {
	position: absolute;
	background: green;
	height: 30px;
	width: 30px;
}
</style>
