<template>
	<Transition name="slide-fade"><slot /></Transition>
</template>

<style lang="css" scoped>
.slide-fade-enter-active {
	transition: all 0.1s ease-out;
}

.slide-fade-leave-active {
	transition: all 0.1s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
	transform: translateY(-18px);
	opacity: 0;
}
@media (prefers-reduced-motion) {
	.slide-fade-enter-from,
	.slide-fade-leave-to,
	.slide-fade-enter-active,
	.slide-fade-leave-active {
		transition: unset;
	}
}
</style>
