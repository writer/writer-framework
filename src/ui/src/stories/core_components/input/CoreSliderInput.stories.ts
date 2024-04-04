import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import SliderInput from "../../../core_components/input/CoreSliderInput.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/input/SliderInput",
	component: SliderInput,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		label: { control: "text" },
		minValue: { control: "text" },
		maxValue: { control: "text" },
		stepSize: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof SliderInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { SliderInput },
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
				minValue: computed(() => args.minValue),
				maxValue: computed(() => args.maxValue),
				stepSize: computed(() => args.stepSize),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<SliderInput :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	