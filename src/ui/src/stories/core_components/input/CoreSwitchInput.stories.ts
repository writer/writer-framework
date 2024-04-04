import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import SwitchInput from "../../../core_components/input/CoreSwitchInput.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/input/SwitchInput",
	component: SwitchInput,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		label: { control: "text" },
		accentColor: { control: "text" },
		primaryTextColor: { control: "text" },
		separatorColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof SwitchInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { SwitchInput },
		setup() {
			const ss = generateCore();
			args.rootStyle = computed(() => {
				return {
					"--accentColor": "#29cf00",
					"--buttonColor": "#ffffff",
					"--emptinessColor": "#e9eef1",
					"--separatorColor": "rgba(0, 0, 0, 0.07)",
					"--primaryTextColor": "#202829",
					"--buttonTextColor": "#202829",
					"--secondaryTextColor": "#5d7275",
					"--containerBackgroundColor": "#ffffff",
				};
			});
			provide(injectionKeys.evaluatedFields, {
				label: computed(() => args.label),
				accentColor: computed(() => args.accentColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				separatorColor: computed(() => args.separatorColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<SwitchInput :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	