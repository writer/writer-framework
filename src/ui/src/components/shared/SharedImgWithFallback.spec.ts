import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import SharedImgWithFallback from "./SharedImgWithFallback.vue";
import { flushPromises, shallowMount } from "@vue/test-utils";

describe("SharedImgWithFallback", () => {
	let fetch: Mock;

	beforeEach(() => {
		fetch = vi.fn().mockResolvedValue({
			ok: true,
			headers: new Map([["Content-Type", "image/png"]]),
		});
		global.fetch = fetch;
	});

	it("should use the last image because the first two are not valid", async () => {
		fetch
			.mockRejectedValueOnce(new Error())
			.mockResolvedValueOnce({
				ok: true,
				headers: new Map([["Content-Type", "text/html"]]),
			})
			.mockResolvedValue({
				ok: true,
				headers: new Map([["Content-Type", "image/png"]]),
			});

		const wrapper = shallowMount(SharedImgWithFallback, {
			props: { urls: ["/img1.svg", "/img2.svg", "/img3.svg"] },
		});
		expect(wrapper.get("img").attributes().src).toBe("");

		await flushPromises();

		expect(wrapper.get("img").attributes().src).toBe("/img3.svg");
	});
});
