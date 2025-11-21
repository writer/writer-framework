import { WdsTabOptions } from "@/wds/WdsTabs.vue";

export const STATUS_OPTIONS = Object.freeze([
	{ value: "success", label: "Success" },
	{ value: "error", label: "Error" },
	{ value: "stopped", label: "Stopped" },
] as const);

export const TRIGGER_OPTIONS = Object.freeze([
	{ value: "On demand", label: "On demand" },
	{ value: "UI", label: "UI" },
	{ value: "API", label: "API" },
	{ value: "Cron", label: "Scheduled" },
] as const);

export const INSTANCE_TYPE_OPTIONS = Object.freeze([
	{ value: "editor", label: "Editor" },
	{ value: "agent", label: "Agent" },
] as const);

export const JOURNAL_TABS = Object.freeze<
	WdsTabOptions<"outputs" | "metadata" | "raw">[]
>([
	{ label: "Outputs", value: "outputs" },
	{ label: "Metadata", value: "metadata" },
	{ label: "Raw JSON", value: "raw" },
] as const);
