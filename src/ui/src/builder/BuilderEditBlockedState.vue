<template>
	<div class="BuilderEditBlockedState">
		<div class="BuilderEditBlockedState__card">
			<h2>You don't have permission to edit this agent</h2>
			<p>
				Ask an org admin or AI Studio full access user to update this
				agent, or to grant you AI Studio builder access.
			</p>
		</div>
	</div>
</template>

<style scoped>
.BuilderEditBlockedState {
	position: absolute;
	inset: 0;
	z-index: 20;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 32px;
	background: rgb(255 255 255 / 64%);
	backdrop-filter: grayscale(1);
}

.BuilderEditBlockedState__card {
	max-width: 520px;
	padding: 32px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 8px;
	background: var(--wdsColorWhite);
	box-shadow: 0px 3px 40px 0px rgba(172, 185, 220, 0.24);
	text-align: center;
}

.BuilderEditBlockedState__card h2 {
	margin: 0 0 12px;
	color: var(--primaryTextColor);
	font-size: 24px;
	font-weight: 500;
	line-height: 1.4;
}

.BuilderEditBlockedState__card p {
	margin: 0;
	color: var(--secondaryTextColor);
	font-size: 16px;
	line-height: 1.6;
}
</style>
