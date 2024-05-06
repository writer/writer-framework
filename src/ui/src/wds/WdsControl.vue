<template>
	<button><slot></slot></button>
</template>

<style scoped>
button {
	width: 40px;
	height: 40px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 300px;
	background: var(--softenedSeparatorColor);
	border: 1px solid transparent;
	border: none;
	cursor: pointer;
	outline: none;
	font-size: 0.875rem;
}

button:hover {
	background: var(--separatorColor);
}
</style>
