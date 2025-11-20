import type {
	INSTANCE_TYPE_OPTIONS,
	STATUS_OPTIONS,
	TRIGGER_OPTIONS,
} from "./journalConstants";

// Type helpers
export type StatusValue = (typeof STATUS_OPTIONS)[number]["value"];
export type TriggerValue = (typeof TRIGGER_OPTIONS)[number]["value"];
export type InstanceTypeValue = (typeof INSTANCE_TYPE_OPTIONS)[number]["value"];

export interface JournalFilters {
	search: string;
	statuses: string[];
	triggers: string[];
	instanceTypes: string[];
}
