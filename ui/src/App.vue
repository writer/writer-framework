<template>
	<div class="App">

		<div class="topLine"></div>

		<header>
			<img src="./assets/sslogo.png" alt="Streamsync" />
			<h1>{{ title }}</h1>
		</header>

		<main>
			<div ref="container">
			</div>
		</main>


		<img :src="streamsync.state.plot" />

	</div>
</template>

<script>

export default {
	inject: [ "streamsync" ],
	
	mounted: function () {
		this.streamsync.mountComponents(this.$refs.container);
		document.title = this.title;
	},

	computed: {
		title: function () {
			return this.streamsync.state.title ?? "Streamsync App";
		}
	}
}
</script>

<style>

body {
	margin: 0;
	font-family: Roboto, sans-serif;
	color: #202020;
	font-size: 0.75rem;
	--separator: rgba(0, 0, 0, 0.1);
}

.topLine {
	height: 4px;
	background: rgb(54,203,62);
	background: linear-gradient(188deg, rgba(54,203,62,1) 0%, rgba(53,72,95,1) 100%);
}

header {
	padding: 24px 24px 0 24px;
	display: flex;
	align-items: center;
}

header img {
	height: 32px;
	margin-right: 16px;
}

main {
	padding: 8px 24px 24px 24px;
}

h1 {
	margin: 0;
	font-weight: normal;
	font-size: 1.35rem;
}

h2 {
	font-size: 1.2rem;
	letter-spacing: 0.03rem;
	font-weight: normal;
	margin: 0;
	margin-bottom: 16px;
}

h3 {
	margin: 0;
	font-weight: bold;
	font-size: 1rem;
}

.component {
	margin-top: 16px;
	margin-bottom: 16px;
}


</style>
