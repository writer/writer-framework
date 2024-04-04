import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import MultiselectInput from "../../../core_components/input/CoreMultiselectInput.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/input/MultiselectInput",
	component: MultiselectInput,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		label: { control: "text" },
		options: { control: "text" },
		placeholder: { control: "text" },
		maximumCount: { control: "text" },
		accentColor: { control: "text" },
		chipTextColor: { control: "text" },
		selectedColor: { control: "text" },
		primaryTextColor: { control: "text" },
		secondaryTextColor: { control: "text" },
		containerBackgroundColor: { control: "text" },
		separatorColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof MultiselectInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { MultiselectInput },
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
				options: computed(() => args.options),
				placeholder: computed(() => args.placeholder),
				maximumCount: computed(() => args.maximumCount),
				accentColor: computed(() => args.accentColor),
				chipTextColor: computed(() => args.chipTextColor),
				selectedColor: computed(() => args.selectedColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				containerBackgroundColor: computed(() => args.containerBackgroundColor),
				separatorColor: computed(() => args.separatorColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<MultiselectInput :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	