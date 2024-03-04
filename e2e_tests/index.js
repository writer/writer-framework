const express = require("express");
const fs = require("node:fs").promises;
const { spawn } = require("node:child_process");
const httpProxy = require("http-proxy");

class Streamsync {
	constructor() {
		this.process = null;
		this.initialized = false;
		this.port = 7358;
	}

	async start() {
		return new Promise((resolve, reject) => {
			const ss = spawn(
				"streamsync",
				["edit", "./runtime", "--port", this.port]
			);
			this.process = ss;
			const startupTimeout = setTimeout(() => {
				// eslint-disable-next-line no-console
				console.error("Streamsync startup timeout");
				ss.kill();
				reject();
			}, 5000);

			ss.stdout.on("data", (data) => {
				// eslint-disable-next-line no-console
				console.log(
					`[${ss.pid}] stdout: ${Buffer.from(data, "utf-8").toString()}`,
				);
				if (data.includes("Builder is available at")) {
					this.initialized = true;
					clearTimeout(startupTimeout);
					resolve(ss);
				}
			});

			ss.stderr.on("data", (data) => {
				// eslint-disable-next-line no-console
				console.error(`[${ss.pid}] stderr: ${data}`);
			});

			ss.on("close", () => {
				// eslint-disable-next-line no-console
				console.log(`[${ss.pid}] child process closed`);
			});
			ss.on("error", (err) => {
				// eslint-disable-next-line no-console
				console.log(`[${ss.pid}] child process error`, err);
			});
			ss.on("exit", (code) => {
				// eslint-disable-next-line no-console
				this.process = null;
				console.log(
					`[${ss.pid}] child process exited with code ${code}`,
				);
			});
		});
	}

	async stop() {
		return new Promise((resolve) => {
			if (this.process) {
				this.process.once("exit", () => {
					resolve();
				});
				this.process.kill("SIGTERM");
			} else {
				resolve();
			}
		});
	}

	async restart() {
		await this.stop();
		this.port += 1;
		await this.start();
	}

	async loadPreset(preset) {
		await this.stop();
		this.port += 1;
		await fs.copyFile(`./presets/${preset}/ui.json`, "./runtime/ui.json");
		await fs.copyFile(`./presets/${preset}/main.py`, "./runtime/main.py");
		await this.start();
	}
}

const ss = new Streamsync();
(async () => {
	await fs.mkdir("runtime", { recursive: true });
})();

var proxy = httpProxy.createProxyServer();

proxy.on('error', function (e) {
	// eslint-disable-next-line no-console
	console.error(e);
});

const app = express();

app.get("/preset/:preset", async (req, res) => {
	console.log("Loading preset", req.params.preset);
	const preset = req.params.preset;
	await ss.loadPreset(preset);
	res.send("UI updated");
});

app.use((req, res) => {
	if(ss.initialized === false) {
		res.send("Server not initialized yet");
		return;
	}
	proxy.web(req, res, {target: 'http://127.0.0.1:'+ ss.port});
})

const server = app.listen(7357, () => {
	// eslint-disable-next-line no-console
	console.log("Server is running on port 7357");
});

server.on('upgrade', (req, socket, head) => {
	proxy.ws(req, socket, head, {target: 'ws://127.0.0.1:'+ss.port, ws: true});
});
