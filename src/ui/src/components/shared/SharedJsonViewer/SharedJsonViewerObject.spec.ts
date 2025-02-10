import { describe, expect, it } from "vitest";
import SharedJsonViewerObject from "./SharedJsonViewerObject.vue";
import { flushPromises, mount } from "@vue/test-utils";
import SharedJsonViewerCollapsible from "./SharedJsonViewerCollapsible.vue";
import SharedJsonViewer from "./SharedJsonViewer.vue";

describe("SharedJsonViewerObject", () => {
	it("should expand a key", async () => {
		const data = { array: [1, 2, 3], obj: { a: 1, b: 2, c: 3 } };
		const wrapper = mount(SharedJsonViewerObject, { props: { data } });

		const collapsers = wrapper.findAllComponents(
			SharedJsonViewerCollapsible,
		);
		expect(collapsers).toHaveLength(2);

		const arrayCollapser = collapsers.at(0);

		expect(arrayCollapser.props().open).toBeFalsy();

		arrayCollapser.vm.$emit("toggle", true);
		await flushPromises();

		expect(arrayCollapser.props().open).toBeTruthy();

		const arrayElement = wrapper.getComponent(SharedJsonViewer);
		expect(arrayElement.props().data).toStrictEqual(data.array);
		expect(arrayElement.props().path).toStrictEqual(["array"]);
	});
});
