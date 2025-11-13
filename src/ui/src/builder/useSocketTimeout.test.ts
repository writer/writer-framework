import {
	describe,
	it,
	expect,
	vi,
	beforeEach,
	afterEach,
	MockInstance,
} from "vitest";
import { nextTick } from "vue";
import { useSocketTimeout } from "./useSocketTimeout";
import { buildMockCore } from "@/tests/mocks";

// Mock dependencies
vi.mock("@/composables/useLogger", () => ({
	useLogger: () => ({
		warn: vi.fn(),
		log: vi.fn(),
		info: vi.fn(),
		error: vi.fn(),
	}),
}));

describe("useSocketTimeout", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let stopSync: MockInstance;

	beforeEach(() => {
		mockCore = buildMockCore();
		stopSync = vi.spyOn(mockCore.core, "stopSync");
		vi.useFakeTimers();

		// Mock document.visibilityState
		Object.defineProperty(document, "visibilityState", {
			writable: true,
			value: "visible",
		});
	});

	afterEach(() => {
		vi.restoreAllMocks();
		vi.useRealTimers();
	});

	it("should initialize with correct defaults", () => {
		const { timeoutMin, socketClosed, reconnecting, prevent } =
			useSocketTimeout(mockCore.core, 5);
		expect(timeoutMin).toBe(5);
		expect(socketClosed.value).toBe(false);
		expect(reconnecting.value).toBe(false);
		expect(prevent.value).toBe(false);
	});

	it("should schedule timeout when tab is hidden and can close socket", async () => {
		const { schedule, socketClosed } = useSocketTimeout(mockCore.core, 1); // 1 minute
		changeVisibilityState("hidden");
		schedule();
		vi.advanceTimersByTime(60 * 1000);
		await nextTick();
		expect(stopSync).toHaveBeenCalled();
		expect(socketClosed.value).toBe(true);
	});

	it("should not schedule timeout if prevent is true", () => {
		const { schedule, prevent, onVisibilityChange } = useSocketTimeout(
			mockCore.core,
			1,
		);
		prevent.value = true;
		changeVisibilityState("hidden");
		onVisibilityChange();

		expect(schedule()).toBe(false);
	});

	it("should schedule timeout if frontend message exists, but it's collaborationPing", () => {
		mockCore.frontendMessageMap.value.set(1, { type: "collaborationPing" });
		const { schedule, onVisibilityChange } = useSocketTimeout(
			mockCore.core,
			1,
		);
		changeVisibilityState("hidden");
		onVisibilityChange();

		expect(schedule()).toBe(true);
	});

	it("should not schedule timeout if frontend message exists", () => {
		mockCore.frontendMessageMap.value.set(1, { type: "event" });
		const { schedule, onVisibilityChange } = useSocketTimeout(
			mockCore.core,
			1,
		);
		changeVisibilityState("hidden");
		onVisibilityChange();

		expect(schedule()).toBe(false);
	});

	it("should clear schedule when clearSchedule is called", () => {
		const { schedule, clearSchedule } = useSocketTimeout(mockCore.core, 1);
		changeVisibilityState("hidden");
		schedule();
		expect(vi.getTimerCount()).toBe(1);
		clearSchedule();
		expect(vi.getTimerCount()).toBe(0);
	});

	function changeVisibilityState(visibilityState: string) {
		// @ts-expect-error mock `visibilityState`
		document.visibilityState = visibilityState;
	}

	it("should clear schedule on visibility change to visible", async () => {
		const { onVisibilityChange } = useSocketTimeout(mockCore.core, 1);
		changeVisibilityState("hidden");
		onVisibilityChange();
		expect(vi.getTimerCount()).toBe(1);

		changeVisibilityState("visible");
		onVisibilityChange();
		expect(vi.getTimerCount()).toBe(0);
	});

	it("should reschedule on visibility change to hidden if can close socket", async () => {
		const { socketClosed, onVisibilityChange } = useSocketTimeout(
			mockCore.core,
			1,
		);
		changeVisibilityState("visible");
		onVisibilityChange();
		await nextTick();
		expect(vi.getTimerCount()).toBe(0);

		changeVisibilityState("hidden");
		onVisibilityChange();

		expect(vi.getTimerCount()).toBe(1);
		await nextTick();

		vi.advanceTimersByTime(10 * 60 * 1_000 + 2_000);
		expect(socketClosed.value).toBe(true);
	});

	it("should reconnect successfully", async () => {
		const init = vi.spyOn(mockCore.core, "init");
		const { reconnect, socketClosed } = useSocketTimeout(mockCore.core, 1);
		socketClosed.value = true;
		await reconnect();
		expect(init).toHaveBeenCalled();
	});

	it("should watch canCloseSocket and clear/reschedule accordingly", async () => {
		const { prevent } = useSocketTimeout(mockCore.core, 1);
		changeVisibilityState("hidden");
		// Initially can close, so schedule
		expect(vi.getTimerCount()).toBe(0); // No timer yet
		prevent.value = true; // Now cannot close
		await nextTick();
		expect(vi.getTimerCount()).toBe(0); // Should clear
		prevent.value = false; // Can close again
		await nextTick();
		expect(vi.getTimerCount()).toBe(1); // Should reschedule
	});
});
