import type { Meta, StoryObj } from "@storybook/vue3";
import { provide, ref, computed } from "vue";
import VideoPlayer from "../../../core_components/content/CoreVideoPlayer.vue";
import injectionKeys from "../../../injectionKeys";
import "remixicon/fonts/remixicon.css";
import { generateCore } from "../../fakeCore";

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
	title: "core-components/content/VideoPlayer",
	component: VideoPlayer,
	// This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
	tags: ["autodocs"],
	argTypes: {
		src: { control: "text" },
		controls: { control: "text" },
		autoplay: { control: "text" },
		loop: { control: "text" },
		muted: { control: "text" },
		cssClasses: { control: "text" },
	},
} satisfies Meta<typeof VideoPlayer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sample: Story = {
	render: (args) => ({
		components: { VideoPlayer },
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
				src: computed(() => args.src),
				controls: computed(() => args.controls),
				autoplay: computed(() => args.autoplay),
				loop: computed(() => args.loop),
				muted: computed(() => args.muted),
				cssClasses: computed(() => args.cssClasses),
			});
			provide(injectionKeys.isDisabled, ref(false));
			provide(injectionKeys.core, ss as any);
			return { args };
		},
		template:
			'<VideoPlayer :style="args.rootStyle" :prop-name="args.propName" />',
	}),
};
	