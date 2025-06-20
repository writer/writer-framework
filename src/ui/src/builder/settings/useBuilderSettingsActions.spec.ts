import {
	BuilderSettingsDropdownActions,
	useBuilderSettingsActions,
} from "./useBuilderSettingsActions";
import { BuilderManager } from "@/writerTypes";
import { beforeEach, describe, expect, it } from "vitest";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { generateBuilderManager } from "../builderManager";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";

describe("useBuilderSettingsActions", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: BuilderManager;

	function getOptionByValue(
		options: WdsDropdownMenuOption[],
		key: BuilderSettingsDropdownActions,
	) {
		return options.find((o) => o.value == key);
	}

	beforeEach(() => {
		mockCore = buildMockCore();
		wfbm = generateBuilderManager();
	});

	it("should disable everything when nnothing is selected", () => {
		const { dropdownOptions } = useBuilderSettingsActions(
			mockCore.core,
			wfbm,
		);

		expect(dropdownOptions.value).toHaveLength(8);

		for (const option of dropdownOptions.value) {
			expect(option.disabled).toBe(true);
		}
	});

	it("should get options for a root", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "root",
				type: "root",
			}),
		);

		wfbm.setSelection("root");

		const { dropdownOptions } = useBuilderSettingsActions(
			mockCore.core,
			wfbm,
		);

		expect(dropdownOptions.value).toHaveLength(8);

		expect(
			dropdownOptions.value.find(
				(o) => o.value == BuilderSettingsDropdownActions.Delete,
			).disabled,
		).toBeTruthy();

		expect(
			dropdownOptions.value.find(
				(o) => o.value == BuilderSettingsDropdownActions.Add,
			).disabled,
		).toBeFalsy();
	});

	it("should get options for a page", () => {
		mockCore.core.addComponent(
			buildMockComponent({
				id: "1",
				type: "root",
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "2",
				parentId: "1",
				type: "page",
			}),
		);

		wfbm.setSelection("2");

		const { dropdownOptions } = useBuilderSettingsActions(
			mockCore.core,
			wfbm,
		);

		expect(dropdownOptions.value).toHaveLength(8);

		expect(
			dropdownOptions.value.find(
				(o) => o.value == BuilderSettingsDropdownActions.Delete,
			).disabled,
		).toBeFalsy();

		expect(
			dropdownOptions.value.find(
				(o) => o.value == BuilderSettingsDropdownActions.Add,
			).disabled,
		).toBeFalsy();
	});
});
