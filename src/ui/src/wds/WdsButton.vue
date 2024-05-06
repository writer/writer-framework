<template>
	<button>
		<slot></slot>
	</button>
</template>

<style scoped>
button {
	width: fit-content;
	max-width: 100%;
	display: flex;
	align-items: center;
	gap: 8px;
	border-radius: 300px;
	border: 1px solid var(--buttonColor);
	background: var(--buttonColor);
	font-weight: 600;
	line-height: 20px;
	font-size: 0.875rem;
	padding: 10px 20px 10px 20px;
	color: var(--buttonTextColor);
	cursor: pointer;
	box-shadow: var(--buttonShadow);
}

button:hover {
	border: 1px solid var(--intensifiedButtonColor);
	background: var(--intensifiedButtonColor);
}
</style>
