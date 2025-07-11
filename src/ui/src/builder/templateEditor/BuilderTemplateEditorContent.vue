<script lang="ts">
import { computeTemplateParts } from "@/utils/template";
import BuilderTemplateEditorContentTag from "./BuilderTemplateEditorContentTag.vue";
import {
	defineComponent,
	h,
	toRef,
	createTextVNode,
	type VNode,
	createElementBlock,
	PropType,
	createVNode,
} from "vue";

export default defineComponent({
	props: {
		content: { type: String, required: false, default: undefined },
		backgroundColors: {
			type: Object as PropType<Record<string, Set<string>>>,
			required: false,
			default: () => {},
		},
	},
	setup(props) {
		const content = toRef(props, "content");
		const backgroundColors = toRef(props, "backgroundColors");

		return () => {
			const children = [];

			for (const part of computeTemplateParts(content.value)) {
				if (part.type === "text") {
					const nodes = (part.content ?? "")
						.split("\n")
						.reduce<VNode[]>((acc, v, i, arr) => {
							acc.push(createTextVNode(v ?? ""));
							if (arr.length > 1 && arr.length !== i + 1) {
								acc.push(createElementBlock("br"));
							}
							return acc;
						}, []);
					children.push(...nodes);
				} else {
					children.push(
						createVNode(BuilderTemplateEditorContentTag, {
							tag: part.content ?? "",
							backgroundColors: backgroundColors.value,
						}),
					);
				}
			}

			return h(
				"div",
				{ class: "BuilderTemplateEditorContent", key: content.value },
				children.length > 0 ? children : createTextVNode(""),
			);
		};
	},
});
</script>

<style lang="css" scoped>
.BuilderTemplateEditorContent {
	width: 100%;
	height: 100%;
}
</style>
