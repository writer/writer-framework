import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import CoreButton from "../core_components/other/CoreButton.vue";
import injectionKeys from "../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "./fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "Core-Components/CoreButton",
	component: CoreButton,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		isDisabled: { control: "select", options: ["yes", "no"] },
		buttonColor: { control: "color" },
		buttonTextColor: { control: "color" },
		separatorColor: { control: "color" },
		icon: { control: "text" },
		text: { control: "text" },
	},
} satisfies Meta<typeof CoreButton>;

export default meta;
type Story = StoryObj<typeof meta>;

/*
 *👇 Render functions are a framework specific feature to allow you control on how the component renders.
 * See https://storybook.js.org/docs/api/csf
 * to learn how to use render functions.
 */

export const Sample: Story = {
	render: (args) => ({
		components: { CoreButton },
		setup() {
			const ss = generateCore();
			const rootStyle = computed(() => {
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
				icon: computed(() => args.icon),
				isDisabled: computed(() => args.isDisabled),
				buttonColor: computed(() => args.buttonColor),
				buttonTextColor: computed(() => args.buttonTextColor),
				separatorColor: computed(() => args.separatorColor),
			});
			provide(
				injectionKeys.isDisabled,
				computed(() => false),
			);
			provide(injectionKeys.core, ss as any);
			return { args, rootStyle };
		},
		template:
			'<CoreButton :style="rootStyle" :prop-name="args.propName" />',
	}),
};
