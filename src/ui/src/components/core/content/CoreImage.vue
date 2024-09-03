<docs lang="md">
Use your app's static folder to serve images directly. For example, \`static/my_image.png\`.

Alternatively, pass a Matplotlib figure via state.

\`state["my_fig"] = fig\` and then setting the _Image_ source to \`@{fig}\`

You can also use packed files or bytes:

\`state["img_b"] = wf.pack_bytes(img_bytes, "image/png")\`

\`state["img_f"] = wf.pack_file(img_file, "image/png")\`
</docs>

<template>
	<div ref="rootEl" class="CoreImage" :style="rootStyle" @click="handleClick">
		<img
			:src="fields.src.value"
			:alt="fields.caption.value"
			draggable="false"
			:style="imgStyle"
		/>
		<div
			v-if="fields.caption.value || fields.caption.value === 0"
			class="captionContainer"
		>
			{{ fields.caption.value }}
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import { cssClasses, secondaryTextColor } from "@/renderer/sharedStyleFields";
import { getClick } from "@/renderer/syntheticEvents";

const description = "A component to display images.";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the image is clicked

	state["counter"] += 1`;

export default {
	writer: {
		name: "Image",
		description,
		category: "Content",
		fields: {
			src: {
				name: "Source",
				default:
					"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQoAAAEKCAYAAADqyxvJAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAemSURBVHgB7d3baltHGIZhJd5DW3pS2vu/tkKgEFragiXLjuvVkpOS5PMa6Z8ZWc8DPXPBJNGrpX82evfrh4/PG4BveL8BCIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiIQCiC43HN3PP/24ubyoafCnT8+bD7/9vur/+f67u80PL/9V+fjHX5vtdv/qn794+bP55eXPaJbfh8wTRYGHh7p/pO/fv/v3hbZG5e+zuLm+WvXzT0+fNo8v/1XZ7582HJdQFKj+h3p7c73q5/ePTy9PInUvzOuVoVhUxWsJ0FNhhM6VUBS43z1sKl1fXaz6+eXjyv6xMBSXF5t3L086a+weHjcVqp+ezpVQFFje0Srfwdc+USz2jzUvzM+WWKyxK3pB74SihFAU2e7mmlNst7VPObe36+JVFdOqJ5VzJxRFqucUaweIy5yi0tXl+gW0Y8fUfKKOUBTZla80rHth/jenqIvFVcOc4tgx3e89TVQRiiLVKw03DSsNu+Jl29Fzim3xEPmcCUWhh8LPy8uMYu07+EPx5/frho9Dx4yp/RN1hKJQ9WDtbuXqx26yjVeLY8Wr+qPVuROKQtVLklcN+ykqd0RerfzosThWTC2L1hKKQsuLoHJOcdewn6Lyc/wyp1g7ZD3WC9yyaC2hKFa5I7JlTlH9Of5y5TLpseYUdmTWEopi1Rud1r6DV68MrP19FofG1HyinlAUq55TrB0gVs8pWgaah8ZUJOoJRbFzOrm5WOYUa4eah8b0fmv/RDWhKHZOJzc/672f4vHRILOaUHRwLic3P2vbXt4eCise9YSigxlPbs42p2iNl0j0IRQdzHhy861c12ejVR9C0cHyaF35zrc86s+2n6Llur4W9k/0IRSdzDanmPG6vpaY+ujRh1B0MtvJzerr+lrmFGtjKhL9CEUnb/nk5pcsM4r1c4p1v8/esmg3QtFJjxum1qp+R14br7Ux3dpo1Y1QdFR9w9Sok5tfU31d34Ot290IRUdv9eTm11Tup1gi8fwSFvoQio6qT27e3bZ838dcx+BfO6ewLNqXUHQ04w1T1Z/zq67rs9GqL6Ho7K2d3EyqruuzNNqXUHQ228nN6uv6Wo7Bp49o5hP9CUVns600LGY7Bp+Gvo++6Kc7oejsLZ3cfK1jL9ve+6Kf7oRigLdycvO1bhq2l38rpr7opz+hGGDGk5uVc4pjHoP3RcRjCMUAM57crJxTtByD/9rQ1/6JMYRigOqTm7c3LRuvTuO6PvsnxhCKQba7ueYUM17X96WY2j8xhlAMUj2nuGm4CbtSy5zi/zE1nxhHKAY59ZOba10dYT/F3v6JYYRikFM+udli+Th06Jxia//EMEIxUPUNU1UnN1sd+sVA9k+MIxQDVQ/mqk5utjrkuj5fRDyWUAx0qic3Wx1yXZ9l0bGEYqDqk5t3DfspKucAh1zXZ1l0LKEYbLYbpma9rs+OzLGEYrDZlkmrVxZajsEvcwrzibGEYrDZTm5WzylaBpp//n2/YSyhGKx6P8V100rDbNf1eZoYTSgGqz652XLD1GzX9TGeUEzgVE5uHsvaY/CMJxQTmPHkZuWcouUYPGMJxQRmPLk523V9jOVvawLLnKJyLtByw9Rs1/UxllBMYrY5xWzX9TGWUExitpOb1df13Vj5OClCMYmZT25WWGYU5hSnw9/UJHrcMLVW9X4KTxWnQygmUn3D1LG/setQLec+GEMoJjLryc0qnihOh1BMpPrk5t1ty/d9zHUMnjGEYiIz3jBVvWv0zn6KkyAUk5nv5OZc1/UxhlBMZraTm9XX9TlJehqEYjIzrjTMdgye/oRiMtUnN2f7YqCFZdL5CcWEZju5Odt1ffT37tcPH583AN/giQKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKIhAKI/gE7SXVdY25ypwAAAABJRU5ErkJggg==",
				desc: "A valid URL. Alternatively, you can provide a state reference to a Matplotlib figure or a packed file.",
				type: FieldType.Text,
			},
			caption: {
				name: "Caption",
				init: "Image Caption",
				desc: "Leave blank to hide.",
				type: FieldType.Text,
			},
			maxWidth: {
				name: "Max width (px)",
				type: FieldType.Number,
				default: "-1",
				category: FieldCategory.Style,
			},
			maxHeight: {
				name: "Max height (px)",
				type: FieldType.Number,
				default: "-1",
				category: FieldCategory.Style,
			},
			secondaryTextColor,
			cssClasses,
		},
		events: {
			"wf-click": {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "caption",
	},
};
</script>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const wf = inject(injectionKeys.core);
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);

const rootStyle = computed(() => {
	const component = wf.getComponentById(componentId);
	const isClickHandled =
		typeof component.handlers?.["wf-click"] !== "undefined";

	return {
		cursor: isClickHandled ? "pointer" : "unset",
	};
});

const imgStyle = computed(() => {
	const maxWidth = fields.maxWidth.value;
	const maxHeight = fields.maxHeight.value;
	return {
		"max-width": maxWidth !== -1 ? `${maxWidth}px` : undefined,
		"max-height": maxHeight !== -1 ? `${maxHeight}px` : undefined,
	};
});

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreImage {
	width: fit-content;
}

img {
	max-width: 100%;
}

.CoreImage.selected img {
	opacity: 0.5;
	mix-blend-mode: multiply;
}
.captionContainer {
	color: var(--secondaryTextColor);
	text-align: center;
	font-size: 0.8rem;
	margin-top: 8px;
}
</style>
