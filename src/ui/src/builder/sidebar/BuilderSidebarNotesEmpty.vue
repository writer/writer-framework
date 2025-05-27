<template>
	<div class="BuilderSidebarNotesEmpty">
		<svg
			width="77"
			height="77"
			viewBox="0 0 77 77"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<circle cx="38.5" cy="38.5" r="38.5" fill="#E4E9FF" />
			<path
				d="M54 44.3333C54 45.2763 53.6254 46.1807 52.9586 46.8475C52.2918 47.5143 51.3874 47.8889 50.4444 47.8889H29.1111L22 55V26.5556C22 25.6126 22.3746 24.7082 23.0414 24.0414C23.7082 23.3746 24.6126 23 25.5556 23H50.4444C51.3874 23 52.2918 23.3746 52.9586 24.0414C53.6254 24.7082 54 25.6126 54 26.5556V44.3333Z"
				fill="white"
			/>
			<path d="M38 30.1111V40.7778V30.1111Z" fill="white" />
			<path d="M32.6667 35.4444H43.3333H32.6667Z" fill="white" />
			<path
				d="M38 30.1111V40.7778M32.6667 35.4444H43.3333M54 44.3333C54 45.2763 53.6254 46.1807 52.9586 46.8475C52.2918 47.5143 51.3874 47.8889 50.4444 47.8889H29.1111L22 55V26.5556C22 25.6126 22.3746 24.7082 23.0414 24.0414C23.7082 23.3746 24.6126 23 25.5556 23H50.4444C51.3874 23 52.2918 23.3746 52.9586 24.0414C53.6254 24.7082 54 25.6126 54 26.5556V44.3333Z"
				stroke="black"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>
		<h5>No Notes</h5>
		<p>Click anywhere on a blueprint or interface to add a note</p>
	</div>
</template>

<style scoped>
.BuilderSidebarNotesEmpty {
	display: flex;
	gap: 24px;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	padding: 16px;
	height: 100%;
}
.BuilderSidebarNotesEmpty h5 {
	font-size: 13px;
	font-weight: 500;
	text-transform: uppercase;
}
.BuilderSidebarNotesEmpty p {
	font-size: 12px;
}
</style>
