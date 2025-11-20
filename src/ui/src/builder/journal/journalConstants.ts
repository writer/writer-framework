export const STATUS_OPTIONS = [
	{ value: "success", label: "Success" },
	{ value: "error", label: "Error" },
	{ value: "stopped", label: "Stopped" },
] as const;

export const TRIGGER_OPTIONS = [
	{ value: "On demand", label: "On demand" },
	{ value: "UI", label: "UI" },
	{ value: "API", label: "API" },
	{ value: "Cron", label: "Scheduled" },
] as const;

export const INSTANCE_TYPE_OPTIONS = [
	{ value: "editor", label: "Editor" },
	{ value: "agent", label: "Agent" },
] as const;
