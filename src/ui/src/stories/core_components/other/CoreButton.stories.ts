import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Button from "../../../core_components/other/CoreButton.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/other/Button",
	component: Button,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		text: { control: "text" },
		isDisabled: { control: "text" },
		buttonColor: { control: "text" },
		buttonTextColor: { control: "text" },
		icon: { control: "text" },
		buttonShadow: { control: "text" },
		separatorColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Button },
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
				text: computed(() => args.text),
				isDisabled: computed(() => args.isDisabled),
				buttonColor: computed(() => args.buttonColor),
				buttonTextColor: computed(() => args.buttonTextColor),
				icon: computed(() => args.icon),
				buttonShadow: computed(() => args.buttonShadow),
				separatorColor: computed(() => args.separatorColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Button :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	