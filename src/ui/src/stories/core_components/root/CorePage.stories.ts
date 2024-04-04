import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Page from "../../../core_components/root/CorePage.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/root/Page",
	component: Page,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		key: { control: "text" },
		pageMode: { control: "text" },
		accentColor: { control: "text" },
		primaryTextColor: { control: "text" },
		secondaryTextColor: { control: "text" },
		emptinessColor: { control: "text" },
		containerBackgroundColor: { control: "text" },
		containerShadow: { control: "text" },
		separatorColor: { control: "text" },
		buttonColor: { control: "text" },
		buttonTextColor: { control: "text" },
		buttonShadow: { control: "text" },
		selectedColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Page>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Page },
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
				key: computed(() => args.key),
				pageMode: computed(() => args.pageMode),
				accentColor: computed(() => args.accentColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				emptinessColor: computed(() => args.emptinessColor),
				containerBackgroundColor: computed(() => args.containerBackgroundColor),
				containerShadow: computed(() => args.containerShadow),
				separatorColor: computed(() => args.separatorColor),
				buttonColor: computed(() => args.buttonColor),
				buttonTextColor: computed(() => args.buttonTextColor),
				buttonShadow: computed(() => args.buttonShadow),
				selectedColor: computed(() => args.selectedColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Page :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	