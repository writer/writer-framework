import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import Chatbot from "../../../core_components/content/CoreChatbot.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/content/Chatbot",
	component: Chatbot,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		incomingInitials: { control: "text" },
		outgoingInitials: { control: "text" },
		useMarkdown: { control: "text" },
		enableFileUpload: { control: "text" },
		placeholder: { control: "text" },
		incomingColor: { control: "text" },
		outgoingColor: { control: "text" },
		avatarBackgroundColor: { control: "text" },
		avatarTextColor: { control: "text" },
		containerBackgroundColor: { control: "text" },
		primaryTextColor: { control: "text" },
		secondaryTextColor: { control: "text" },
		separatorColor: { control: "text" },
		buttonColor: { control: "text" },
		buttonTextColor: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof Chatbot>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { Chatbot },
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
				incomingInitials: computed(() => args.incomingInitials),
				outgoingInitials: computed(() => args.outgoingInitials),
				useMarkdown: computed(() => args.useMarkdown),
				enableFileUpload: computed(() => args.enableFileUpload),
				placeholder: computed(() => args.placeholder),
				incomingColor: computed(() => args.incomingColor),
				outgoingColor: computed(() => args.outgoingColor),
				avatarBackgroundColor: computed(() => args.avatarBackgroundColor),
				avatarTextColor: computed(() => args.avatarTextColor),
				containerBackgroundColor: computed(() => args.containerBackgroundColor),
				primaryTextColor: computed(() => args.primaryTextColor),
				secondaryTextColor: computed(() => args.secondaryTextColor),
				separatorColor: computed(() => args.separatorColor),
				buttonColor: computed(() => args.buttonColor),
				buttonTextColor: computed(() => args.buttonTextColor),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<Chatbot :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	