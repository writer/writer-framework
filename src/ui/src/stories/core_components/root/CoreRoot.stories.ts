import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Root from "../../../core_components/root/CoreRoot.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/root/Root",
	component: Root,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		appName: { control: "text" },
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
		contentWidth: { control: "text" },
		contentHAlign: { control: "text" },
		contentVAlign: { control: "text" },
		contentPadding: { control: "text" },
	},
} satisfies Meta<typeof Root>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Root },
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
				appName: computed(() => args.appName),
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
				contentWidth: computed(() => args.contentWidth),
				contentHAlign: computed(() => args.contentHAlign),
				contentVAlign: computed(() => args.contentVAlign),
				contentPadding: computed(() => args.contentPadding),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Root :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	