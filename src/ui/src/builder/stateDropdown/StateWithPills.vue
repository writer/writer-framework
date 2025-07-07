<script lang="ts">
import { computeTemplateParts } from "@/utils/template";
import {
	defineComponent,
	h,
	toRef,
	createTextVNode,
	type VNode,
	createElementBlock,
} from "vue";

export default defineComponent({
	props: {
		content: { type: String, required: false, default: undefined },
	},
	setup(props) {
		const content = toRef(props, "content");

		function createTagVNode(tag: string) {
			const children = [
				createTextVNode("@"),
				h("span", { class: "StateWithPill__tag__bracket" }, "{"),
				createTextVNode(tag),
				h("span", { class: "StateWithPill__tag__bracket" }, "}"),
			];
			return h("span", { class: "StateWithPill__tag" }, children);
		}

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
					children.push(createTagVNode(part.content));
				}
			}

			return h(
				"div",
				{ class: "StateWithPill", key: content.value },
				children.length > 0 ? children : createTextVNode(""),
			);
		};
	},
});
</script>

<style lang="css" scoped>
.StateWithPill {
	width: 100%;
	height: 100%;
}
.StateWithPill__tag {
	background-color: #d4fff2;
	color: #000000;
	padding: 4px 8px;
	border-radius: 4px;
}

.StateWithPill__tag__bracket {
	color: transparent;
	caret-color: var(--wdsColorBlack);
}
</style>
