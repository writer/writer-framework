<template>
	<div class="BuilderToasts">
		<TransitionGroup name="list" tag="div">
			<WdsToast
				v-for="toast of toasts"
				:key="toast.id"
				class="BuilderToasts__toast"
				:closable="toast.closable"
				:message="toast.message"
				:type="toast.type"
				@click="removeToast(toast.id)"
			/>
		</TransitionGroup>
	</div>
</template>

<script setup lang="ts">
import WdsToast from "@/wds/WdsToast.vue";
import { useToasts } from "./useToast";

const { toasts, removeToast } = useToasts();
</script>

<style scoped>
.BuilderToasts {
	position: fixed;
	bottom: 12px;
	right: 12px;
	z-index: 1;
}

.BuilderToasts__toast {
	margin-top: 12px;
}

.list-enter-active,
.list-leave-active {
	transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
	opacity: 0;
	transform: translateX(30px);
}
</style>
