type RequestInit = Parameters<typeof fetch>[1];

export class WriterApi {
	#signal: AbortSignal | undefined;
	#baseUrl: string;
	#requestInitBase: Pick<RequestInit, "signal" | "credentials" | "headers">;

	constructor(opts?: { signal?: AbortSignal; baseUrl?: string }) {
		this.#signal = opts?.signal;
		this.#baseUrl = opts?.baseUrl ?? window.location.origin;
		this.#requestInitBase = {
			signal: this.#signal,
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-Client": "Framework",
			},
		};
	}

	async #fetchJSON(
		path: string,
		params?: RequestInit & {
			query?: Record<string, string | number | boolean>;
		},
	) {
		const query = new URLSearchParams(
			Object.entries(params?.query ?? {}).map(([k, v]) => [k, String(v)]),
		);

		const url = new URL(
			query.size > 0 ? `${path}?${query}` : path,
			this.#baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: params?.method ?? "GET",
			headers: {
				...this.#requestInitBase.headers,
				accept: "application/json",
				"content-type": "application/json",
				...(params?.headers ?? {}),
			},
			body: params?.body,
		});
		if (!res.ok) throw Error(`Error fetching ${url}\n${await res.text()}`);
		return res.json();
	}

	fetchApplicationDeployment(
		orgId: number,
		appId: string,
	): Promise<WriterApiApplicationDeployment> {
		return this.#fetchJSON(
			`/api/template/organization/${orgId}/application/${appId}/deployment`,
		);
	}

	async fetchOrganizationUsers(
		orgId: number,
		filters: {
			search?: string;
			userType?: "individual" | "application";
			offset?: number;
			limit?: number;
		} = {},
	): Promise<WriterApiOrganizationUsers> {
		return this.#fetchJSON(`/api/user/v2/organization/${orgId}`, {
			query: filters,
		});
	}

	publishApplication(
		orgId: number,
		appId: string,
		body: {
			applicationVersionId: string;
			applicationVersionDataId: string;
		},
	): Promise<WriterApiDeployResult> {
		return this.#fetchJSON(
			`/api/template/organization/${orgId}/application/${appId}/publish`,
			{
				method: "PUT",
				body: JSON.stringify(body),
			},
		);
	}

	updateApplicationMetadata(
		orgId: number,
		appId: string,
		body: Partial<
			Omit<
				WriterApiApplicationMetadata,
				| "id"
				| "applicationId"
				| "createdBy"
				| "createdBy"
				| "updatedAt"
				| "updatedBy"
			>
		>,
	): Promise<WriterApiApplicationMetadata> {
		return this.#fetchJSON(
			`/api/template/organization/${orgId}/application/${appId}/metadata`,
			{
				method: "PUT",
				body: JSON.stringify(body),
			},
		);
	}

	fetchUserProfile(): Promise<WriterApiUserProfile> {
		return this.#fetchJSON(`/api/user/v2/profile`);
	}

	fetchUserById(userId: number): Promise<WriterApiUser> {
		return this.#fetchJSON(`/api/user/v2/user/${userId}`);
	}

	async analyticsIdentify() {
		const url = new URL(`/api/analytics/identify`, this.#baseUrl);
		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({ traits: {} }),
		});
		if (!res.ok) throw Error(await res.text());
	}

	async analyticsTrack(
		eventName: string,
		properties: Record<string, unknown>,
	) {
		const url = new URL(`/api/analytics/track`, this.#baseUrl);
		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({ eventName, properties }),
		});
		if (!res.ok) throw Error(await res.text());
	}

	async analyticsPage(
		name: string,
		organizationId: number,
		properties: Record<string, unknown>,
	) {
		const url = new URL(`/api/analytics/page`, this.#baseUrl);
		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({
				name,
				organizationId,
				properties,
			}),
		});
		if (!res.ok) throw Error(await res.text());
	}

	fetchThirdUserProfile(userId: number): Promise<WriterApiThirdUserProfile> {
		return this.#fetchJSON(`/api/user/v2/user/${userId}`);
	}

	// secrets

	createSecret(
		orgId: number,
		appId: string,
		key: string,
		data: unknown,
	): Promise<WriterApiSecretResponse> {
		return this.#fetchJSON(this.#getSecretUrl(orgId, appId), {
			method: "POST",
			body: JSON.stringify({ key, secret: data }),
		});
	}

	async fetchSecret(
		orgId: number,
		appId: string,
		key: string,
	): Promise<WriterApiSecretResponse> {
		return this.#fetchJSON(this.#getSecretUrl(orgId, appId, key));
	}

	deleteSecret(orgId: number, appId: string, key: string) {
		return this.#fetchJSON(this.#getSecretUrl(orgId, appId, key), {
			method: "DELETE",
		});
	}

	async updateSecret(
		orgId: number,
		appId: string,
		key: string,
		data: unknown,
	): Promise<WriterApiSecretResponse> {
		return this.#fetchJSON(this.#getSecretUrl(orgId, appId, key), {
			method: "PUT",
			body: JSON.stringify({ key, secret: data }),
		});
	}

	#getSecretUrl(orgId: number, appId: string, key?: string) {
		const url = `/api/template/organization/${orgId}/agent/${appId}/secret`;
		return key ? `${url}/${key}` : url;
	}
}

export type WriterApiUser = Pick<
	WriterApiUserProfile,
	"id" | "avatar" | "firstName" | "lastName" | "email"
>;

type WriterApiBlamable = {
	createdBy: number;
	updatedBy: number;
	createdAt: string;
	updatedAt: string;
};

type WriterApiApplicationMetadata = {
	id: string;
	applicationId: string;
	name: string;
	description: string | null;
	shortDescription: string | null;
	guideUrl: string | null;
	tutorialUrl: string | null;
	icon: string | null;
	idAlias: string | null;
} & WriterApiBlamable;

export type WriterApiOrganizationUsers = {
	result: {
		user: WriterApiUserProfile;
		managedByScim: boolean;
		role: "member" | "admin";
		consoleRole: "View" | "Draft" | "FullAccess" | null;
		teams: {
			id: number;
			name: string;
			role: "member" | "admin";
		}[];
		approvedByInviter: boolean;
		userStatus: "active" | "invite_pending" | "approval_pending";
		billingGroup: null;
	}[];
	pagination: {
		offset: number | null;
		limit: number;
	};
	totalCount: number;
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

export type WriterApiThirdUserProfile = {
	id: number;
	firstName: string;
	lastName: string;
	fullName: string;
	email: string;
	avatar: null | string;
};

export type WriterApiSecretResponse = {
	name: string;
	secret: Record<string, string>;
};
