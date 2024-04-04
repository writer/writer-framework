import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Column from "../../../core_components/layout/CoreColumn.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/layout/Column",
	component: Column,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		title: { control: "text" },
		width: { control: "text" },
		isSticky: { control: "text" },
		isCollapsible: { control: "text" },
		startCollapsed: { control: "text" },
		separatorColor: { control: "text" },
		contentPadding: { control: "text" },
		contentHAlign: { control: "text" },
		contentVAlign: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Column>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Column },
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
				title: computed(() => args.title),
				width: computed(() => args.width),
				isSticky: computed(() => args.isSticky),
				isCollapsible: computed(() => args.isCollapsible),
				startCollapsed: computed(() => args.startCollapsed),
				separatorColor: computed(() => args.separatorColor),
				contentPadding: computed(() => args.contentPadding),
				contentHAlign: computed(() => args.contentHAlign),
				contentVAlign: computed(() => args.contentVAlign),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Column :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	