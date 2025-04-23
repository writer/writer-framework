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
		body: {
			applicationVersionId: string;
			applicationVersionDataId: string;
		},
	): Promise<WriterApiDeployResult> {
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

	async fetchUserProfile(): Promise<WriterApiUserProfile> {
		const url = new URL(`/api/user/v2/profile`, this.#baseUrl);
		const res = await fetch(url, {
			signal: this.#signal,
			credentials: "include",
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
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

export type WriterApiApplicationDeployment = WriterApiDeployResult & {
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
	cloud: { id: string; requiresWriterLogin: boolean } | null;
};

export type WriterApiDeployResult = {
	id: string;
	name: string;
	type: "framework";
	status: "deployed" | "draft";
	protected: boolean;
	createdAt: string;
	createdBy: WriterApiUser;
	lastDeployedAt: string;
	lastDeployedBy: WriterApiUser;
	playground: null;
	lastEditedAt: string;
	icon: string | null;
	recentlyUsedAt: string | null;
};

export type WriterApiUserProfile = {
	id: number;
	clientId: null | unknown;
	avatar: string;
	accountStatus: "signed_up";
	firstName: string;
	lastName: string;
	fullName: string;
	email: string;
	jobTitle: null | string;
	timezone: string;
	phone: null | string;
	lastOnlineTime: string;
	hasPassword: boolean;
	hasSaml: boolean;
	allowUserCreation: boolean;
	allowDirectPasswordLogin: boolean;
	invited: boolean;
	invitedBy: null;
	creator: boolean;
	createdAt: string;
	authType: string;
	billingGroupName: null;
};
