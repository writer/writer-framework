const express = require("express");
const fs = require("node:fs").promises;
const { spawn } = require("node:child_process");

class Streamsync {
	constructor() {
		this.process = null;
	}

	async start() {
		return new Promise((resolve) => {
			const ss = spawn(
				"streamsync",
				["edit", "./runtime", "--port", "7357"],
				{
					shell: true,
				},
			);
			this.process = ss;

			ss.stdout.on("data", (data) => {
				// eslint-disable-next-line no-console
				console.log(
					`[${ss.pid}] stdout: ${Buffer.from(data, "utf-8").toString()}`,
				);
				if (data.includes("Builder is available at")) {
					resolve(ss);
				}
			});

			ss.stderr.on("data", (data) => {
				// eslint-disable-next-line no-console
				console.error(`[${ss.pid}] stderr: ${data}`);
			});

			ss.on("close", (code) => {
				// eslint-disable-next-line no-console
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
					this.process = null;
					resolve();
				});
				this.process.kill("SIGINT");
			} else {
				resolve();
			}
		});
	}

	async restart() {
		await this.stop();
		await this.start();
	}

	async loadPreset(preset) {
		await this.stop();
		await fs.copyFile(`./presets/${preset}/ui.json`, "./runtime/ui.json");
		await fs.copyFile(`./presets/${preset}/main.py`, "./runtime/main.py");
		await this.start();
	}
}

const ss = new Streamsync();
(async () => {
	await fs.mkdir("runtime", { recursive: true });
	await ss.loadPreset("empty_page");
})();
const app = express();

app.get("/:preset", async (req, res) => {
	const preset = req.params.preset;
	await ss.loadPreset(preset);
	res.send("UI updated");
});

app.listen(7358, () => {
	// eslint-disable-next-line no-console
	console.log("Server is running on port 7358");
});
