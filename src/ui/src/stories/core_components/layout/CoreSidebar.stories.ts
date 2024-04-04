import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Sidebar from "../../../core_components/layout/CoreSidebar.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/layout/Sidebar",
	component: Sidebar,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		startCollapsed: { control: "text" },
		sidebarBackgroundColor: { control: "text" },
		accentColor: { control: "text" },
		primaryTextColor: { control: "text" },
		secondaryTextColor: { control: "text" },
		containerBackgroundColor: { control: "text" },
		containerShadow: { control: "text" },
		separatorColor: { control: "text" },
		buttonColor: { control: "text" },
		buttonTextColor: { control: "text" },
		buttonShadow: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Sidebar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Sidebar },
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
				startCollapsed: computed(() => args.startCollapsed),
				sidebarBackgroundColor: computed(() => args.sidebarBackgroundColor),
				accentColor: computed(() => args.accentColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				containerBackgroundColor: computed(() => args.containerBackgroundColor),
				containerShadow: computed(() => args.containerShadow),
				separatorColor: computed(() => args.separatorColor),
				buttonColor: computed(() => args.buttonColor),
				buttonTextColor: computed(() => args.buttonTextColor),
				buttonShadow: computed(() => args.buttonShadow),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Sidebar :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	