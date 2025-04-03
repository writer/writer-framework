<template>
	<svg
		:class="customClass"
		width="592"
		height="592"
		viewBox="0 0 592 592"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
	>
		<g>
			<g
				clip-path="url(#paint0_angular_167_137448_clip_path)"
				data-figma-skip-parse="true"
			>
				<g
					transform="matrix(0.208791 0.208791 -0.208791 0.208791 296.078 296.082)"
				>
					<foreignObject
						x="-1003.39"
						y="-1003.39"
						width="2006.77"
						height="2006.77"
					>
						<div
							xmlns="http://www.w3.org/1999/xhtml"
							style="
								background: conic-gradient(
									from 90deg,
									rgba(240, 207, 255, 1) 0deg,
									rgba(191, 203, 255, 1) 360deg
								);
								height: 100%;
								width: 100%;
								opacity: 1;
							"
						></div>
					</foreignObject>
				</g>
			</g>
			<ellipse
				cx="296.078"
				cy="296.082"
				rx="295.275"
				ry="295.275"
				transform="rotate(-45 296.078 296.082)"
				data-figma-gradient-fill="{&#34;type&#34;:&#34;GRADIENT_ANGULAR&#34;,&#34;stops&#34;:[{&#34;color&#34;:{&#34;r&#34;:0.94117647409439087,&#34;g&#34;:0.81176471710205078,&#34;b&#34;:1.0,&#34;a&#34;:1.0},&#34;position&#34;:0.0},{&#34;color&#34;:{&#34;r&#34;:0.74901962280273438,&#34;g&#34;:0.79607844352722168,&#34;b&#34;:1.0,&#34;a&#34;:1.0},&#34;position&#34;:1.0}],&#34;stopsVar&#34;:[{&#34;color&#34;:{&#34;r&#34;:0.94117647409439087,&#34;g&#34;:0.81176471710205078,&#34;b&#34;:1.0,&#34;a&#34;:1.0},&#34;position&#34;:0.0},{&#34;color&#34;:{&#34;r&#34;:0.74901962280273438,&#34;g&#34;:0.79607844352722168,&#34;b&#34;:1.0,&#34;a&#34;:1.0},&#34;position&#34;:1.0}],&#34;transform&#34;:{&#34;m00&#34;:417.58184814453125,&#34;m01&#34;:-417.58175659179688,&#34;m02&#34;:296.07785034179688,&#34;m10&#34;:417.58184814453125,&#34;m11&#34;:417.58175659179688,&#34;m12&#34;:-121.50022125244141},&#34;opacity&#34;:1.0,&#34;blendMode&#34;:&#34;NORMAL&#34;,&#34;visible&#34;:true}"
			/>
		</g>

		<defs>
			<clipPath id="paint0_angular_167_137448_clip_path">
				<ellipse
					cx="296.078"
					cy="296.082"
					rx="295.275"
					ry="295.275"
					transform="rotate(-45 296.078 296.082)"
				/>
			</clipPath>
		</defs>
	</svg>
</template>

<script>
export default {
	name: "RotatingCircle",
	props: {
		customClass: {
			type: String,
			required: true,
		},
	},
};
</script>

<style scoped>
.rotating-circle {
	transform-origin: center;
	position: absolute;
}
</style>
