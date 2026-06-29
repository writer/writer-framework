<template>
	<section
		aria-label="Custom agent deprecation notice"
		class="BuilderDeprecationBanner"
	>
		<img
			:src="bannerBg"
			alt=""
			aria-hidden="true"
			class="BuilderDeprecationBanner__background"
		/>
		<div aria-hidden="true" class="BuilderDeprecationBanner__overlay" />
		<div class="BuilderDeprecationBanner__content">
			<div class="BuilderDeprecationBanner__copy">
				<p class="BuilderDeprecationBanner__title">{{ title }}</p>
				<p class="BuilderDeprecationBanner__body">
					{{ body }}
					<a
						:href="LEARN_MORE_URL"
						target="_blank"
						rel="noopener noreferrer"
						class="BuilderDeprecationBanner__learnMore"
						:aria-label="`Learn more (opens in new tab)`"
						>Learn more</a
					>
				</p>
			</div>
			<div class="BuilderDeprecationBanner__actions">
				<WdsButton
					v-if="showMigrateButton"
					variant="neutral"
					size="small"
					class="BuilderDeprecationBanner__cta"
					@click="onMigrateClick"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						style="flex-shrink: 0"
					>
						<path
							d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
						/>
						<line x1="12" y1="11" x2="12" y2="17" />
						<line x1="9" y1="14" x2="15" y2="14" />
					</svg>
					{{ migrateLabel }}
				</WdsButton>
				<WdsButton
					v-else-if="showPlaybookButton"
					variant="neutral"
					size="small"
					class="BuilderDeprecationBanner__cta"
					@click="onPlaybookClick"
				>
					{{ CREATE_PLAYBOOK_LABEL }}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						style="flex-shrink: 0"
					>
						<line x1="7" y1="17" x2="17" y2="7" />
						<polyline points="7 7 17 7 17 17" />
					</svg>
				</WdsButton>
				<WdsButton
					v-if="!isPostCutoff && showDismiss"
					variant="secondary"
					size="smallIcon"
					aria-label="Dismiss deprecation notice"
					class="BuilderDeprecationBanner__dismiss"
					@click="$emit('dismiss')"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="16"
						height="16"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
					>
						<line x1="18" y1="6" x2="6" y2="18" />
						<line x1="6" y1="6" x2="18" y2="18" />
					</svg>
				</WdsButton>
			</div>
		</div>
	</section>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import injectionKeys from "@/injectionKeys";
import bannerBg from "@/assets/custom-agent-deprecation-banner-bg.png";

const LEARN_MORE_URL =
	"https://docs.google.com/document/d/1Zi1zNMVesciYSqL5Qv5oBskIiBysY5vghocyA0LdBYc/edit";
const CREATE_PLAYBOOK_LABEL = "Create a playbook";
const MIGRATE_AGENT_LABEL = "Migrate agent";
const MIGRATE_AGENTS_LABEL = "Migrate agents";

const DEPRECATION_CUTOFF_DATE = new Date("2026-09-10T00:00:00");

function getDaysUntilCutoff(): number {
	const msPerDay = 1000 * 60 * 60 * 24;
	const diff = DEPRECATION_CUTOFF_DATE.getTime() - Date.now();
	return Math.max(0, Math.ceil(diff / msPerDay));
}

function formatDaysTitle(daysRemaining: number): string {
	const dayLabel = daysRemaining === 1 ? "day" : "days";
	return `In ${daysRemaining} ${dayLabel} this Agent Builder is going away`;
}

const props = defineProps<{
	isOrganizationAdmin: boolean;
	isPostCutoff: boolean;
	daysRemaining?: number;
	showDismiss?: boolean;
}>();

defineEmits<{
	dismiss: [];
}>();

const wf = inject(injectionKeys.core);

const daysRemaining = computed(
	() => props.daysRemaining ?? getDaysUntilCutoff(),
);

const title = computed(() => {
	if (props.isPostCutoff) {
		return "This agent builder is no longer supported";
	}
	return formatDaysTitle(daysRemaining.value);
});

const body = computed(() => {
	if (props.isPostCutoff) {
		return props.isOrganizationAdmin
			? "Migrate your team's agents to the new Agent Builder now."
			: "Create a Playbook instead.";
	}
	return props.isOrganizationAdmin
		? "This legacy agent editor will no longer be available - migrate your agent to the new Agent Builder now."
		: "This legacy agent editor will no longer be available - work with your Admin to migrate your agent to the new Agent Builder now.";
});

const migrateLabel = computed(() =>
	props.isPostCutoff ? MIGRATE_AGENTS_LABEL : MIGRATE_AGENT_LABEL,
);

const showMigrateButton = computed(() => props.isOrganizationAdmin);
const showPlaybookButton = computed(() => !props.isOrganizationAdmin);

const playbooksUrl = computed(() => {
	if (!wf) return "#";
	const orgId = wf.writerOrgId.value;
	if (!orgId) return "#";
	return `/organization/${orgId}/team/default/ai-studio/agent-flow`;
});

function onMigrateClick() {
	if (!wf) return;
	const orgId = wf.writerOrgId.value;
	if (!orgId) return;
	window.location.href = `/organization/${orgId}/team/default/ai-studio/agents`;
}

function onPlaybookClick() {
	window.open(playbooksUrl.value, "_blank", "noopener,noreferrer");
}
</script>

<style scoped>
.BuilderDeprecationBanner {
	position: relative;
	isolation: isolate;
	flex-shrink: 0;
	height: 80px;
	width: 100%;
	overflow: hidden;
}

.BuilderDeprecationBanner__background {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	object-fit: cover;
	object-position: center;
}

.BuilderDeprecationBanner__overlay {
	pointer-events: none;
	position: absolute;
	inset: 0;
	background: linear-gradient(
		to bottom,
		rgb(0 0 0 / 80%),
		rgb(0 0 0 / 40%),
		transparent
	);
}

.BuilderDeprecationBanner__content {
	position: relative;
	display: flex;
	height: 80px;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	padding: 14px 24px 14px 40px;
}

.BuilderDeprecationBanner__copy {
	min-width: 0;
	max-width: 720px;
	color: white;
}

.BuilderDeprecationBanner__title {
	margin: 0;
	font-size: 18px;
	font-weight: 500;
	line-height: 1.35;
}

.BuilderDeprecationBanner__body {
	margin: 0;
	font-size: 12px;
	line-height: 1.5;
}

.BuilderDeprecationBanner__learnMore {
	color: inherit;
	text-decoration: underline;
	text-underline-offset: 2px;
	white-space: nowrap;
}

.BuilderDeprecationBanner__actions {
	display: flex;
	flex-shrink: 0;
	align-items: center;
	gap: 8px;
}

.BuilderDeprecationBanner__cta {
	border-color: white !important;
	background-color: white !important;
	color: black !important;
	gap: 6px !important;
}

.BuilderDeprecationBanner__cta:hover {
	background-color: rgb(255 255 255 / 90%) !important;
}

.BuilderDeprecationBanner__dismiss {
	color: white !important;
	background-color: transparent !important;
	border-color: transparent !important;
}

.BuilderDeprecationBanner__dismiss:hover {
	background-color: rgb(255 255 255 / 10%) !important;
}
</style>
