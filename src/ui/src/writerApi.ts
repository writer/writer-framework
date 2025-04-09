export class WriterApi {
	#signal: AbortSignal | undefined;
	#baseUrl: string;

	constructor(opts?: { signal?: AbortSignal; baseUrl?: string }) {
		this.#signal = opts?.signal;
		this.#baseUrl = opts?.baseUrl ?? window.location.origin;
	}

	async fetchApplicationDeployment(
		orgId: number,
		appId: string,
	): Promise<WriterApiApplicationDeployment> {
		const url = new URL(
			`/api/template/organization/${orgId}/application/${appId}/deployment`,
			this.#baseUrl,
		);
		const res = await fetch(url, {
			signal: this.#signal,
			credentials: "include",
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async publishApplication(
		orgId: number,
		appId: string,
		body?: {
			applicationVersionId: string;
			applicationVersionDataId: string;
		},
	): Promise<WriterApiDeployResult> {
		if (body === undefined) {
			const deployInformation = await this.fetchApplicationDeployment(
				orgId,
				appId,
			);
			body = {
				applicationVersionId: deployInformation.applicationVersion.id,
				applicationVersionDataId:
					deployInformation.applicationVersionData.id,
			};
		}
		const url = new URL(
			`/api/template/organization/${orgId}/application/${appId}/publish`,
			this.#baseUrl,
		);

		const res = await fetch(url, {
			method: "PUT",
			body: JSON.stringify(body),
			signal: this.#signal,
			credentials: "include",
		});
		if (!res.ok) throw Error(await res.text());

		const data = await res.json();
		return data;
	}
}

type WriterApiUser = {
	id: number;
	email: string;
	firstName: string;
	lastName: string;
	avatar: string | null;
};

type WriterApiBlamable = {
	createdBy: number;
	updatedBy: number;
	createdAt: string;
	updatedAt: string;
};

export type WriterApiApplicationDeployment = {
	id: string;
	name: string;
	type: "framework";
	status: "deployed";
	protected: boolean;
	createdAt: string;
	createdBy: WriterApiUser;
	lastDeployedAt: string;
	lastDeployedBy: WriterApiUser;
	tagIds: [];
	applicationVersion: {
		id: string;
		applicationId: string;
		name: string;
		description: null;
		shortDescription: null;
		guideUrl: null;
		tutorialUrl: null;
		icon: null;
		idAlias: null;
	} & WriterApiBlamable;
	metadataEditable: boolean;
	applicationVersionData: {
		id: string;
		applicationId: string;
		data: {
			type: "framework";
			apiId: string;
			deploymentUrl: string;
			agentEditorUrl: string;
			tokenEncryptionKey: string | null;
		};
	} & WriterApiBlamable;
	configurationEditable: false;
	playground: null;
	embed: null;
	writer: {
		id: string;
		teamIds: number[];
		access: "private-team" | "private" | "private-organization";
		featured: boolean;
		beta: boolean;
	} | null;
	slack: null;
	cloud: null;
};

export type WriterApiDeployResult = {
	id: string;
	name: string;
	type: "framework";
	status: "deployed";
	protected: true;
	createdAt: string;
	createdBy: WriterApiUser;
	lastDeployedAt: string;
	lastDeployedBy: WriterApiUser;
	playground: null;
	lastEditedAt: string;
	icon: string | null;
	recentlyUsedAt: string | null;
};
