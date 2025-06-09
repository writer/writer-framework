<template>
	<div ref="rootEl" class="BuilderCollaborationTracker">
		<template
			v-for="(userIds, instancePath) in collaborationManager
				.connectedUsersByInstancePath.value"
			:key="instancePath"
		>
			<BuilderInstanceTracker
				v-if="isTrackable(instancePath)"
				:is-off-bounds-allowed="false"
				:instance-path="instancePath"
				:vertical-offset-pixels="-32"
				class="instanceTracker"
			>
				<div class="bubble">
					<div class="main">
						<SharedWriterAvatar
							v-for="userId in userIds"
							:key="userId"
							:show-tooltip="true"
							:user-id="userId"
						/>
					</div>
					<div class="triangle"></div>
				</div>
			</BuilderInstanceTracker>
		</template>
	</div>
</template>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";
import BuilderInstanceTracker from "./BuilderInstanceTracker.vue";
import SharedWriterAvatar from "@/components/shared/SharedWriterAvatar.vue";
import { parseInstancePathString } from "@/renderer/instancePath";

const collaborationManager = inject(injectionKeys.collaborationManager);

function isTrackable(instancePathStr: string) {
	const instancePath = parseInstancePathString(instancePathStr);
	if (instancePath.length <= 2) return false;
	return true;
}
</script>

<style scoped>
.BuilderCollaborationTracker {
	--sharedWriterAvatarSize: 24px;
}

.instanceTracker {
	pointer-events: auto;
}

.bubble {
	position: relative;
	height: 32px;
	width: fit-content;
	display: flex;
	align-items: center;
	flex-direction: column;
	filter: drop-shadow(0 1px 1px #bfcbff);
}

.triangle {
	position: relative;
	z-index: 1;
	margin-top: -6px;
	background: #e1a0ff;
	height: 8px;
	width: 8px;
	transform: rotate(45deg);
}

.main {
	padding: 2px;
	position: relative;
	z-index: 2;
	top: 0;
	height: 28px;
	min-width: 28px;
	width: fit-content;
	background: #e1a0ff;
	border-radius: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4px;
}
</style>
