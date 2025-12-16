import { useLogger } from "@/composables/useLogger";

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

	async fetchApplicationDeployment(
		orgId: number,
		appId: string,
	): Promise<WriterApiApplicationDeployment> {
		const url = new URL(
			`/api/template/organization/${orgId}/application/${appId}/deployment`,
			this.#baseUrl,
		);
		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
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
		const url = new URL(
			`/api/user/v2/organization/${orgId}`,
			this.#baseUrl,
		);
		const params = new URLSearchParams();
		for (const [key, value] of Object.entries(filters)) {
			params.append(key, String(value));
		}

		const res = await fetch(
			`${url}?${params.toString()}`,
			this.#requestInitBase,
		);
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
			...this.#requestInitBase,
			method: "PUT",
			body: JSON.stringify(body),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async updateApplicationMetadata(
		orgId: number,
		appId: string,
		body: Partial<
			Omit<
				WriterApiApplicationMetadata,
				| "id"
				| "applicationId"
				| "createdBy"
				| "createdAt"
				| "updatedAt"
				| "updatedBy"
			>
		>,
	): Promise<WriterApiApplicationMetadata> {
		const url = new URL(
			`/api/template/organization/${orgId}/application/${appId}/metadata`,
			this.#baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "PUT",
			body: JSON.stringify(body),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async fetchUserProfile(): Promise<WriterApiUserProfile> {
		const url = new URL(`/api/user/v2/profile`, this.#baseUrl);
		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async fetchUserById(userId: number): Promise<WriterApiUser> {
		const url = new URL(`/api/user/v2/user/${userId}`, this.#baseUrl);
		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
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
			method: "POST",
			body: JSON.stringify({
				name,
				organizationId,
				properties,
			}),
			signal: this.#signal,
			credentials: "include",
		});
		if (!res.ok) throw Error(await res.text());
	}

	async fetchThirdUserProfile(
		userId: number,
	): Promise<WriterApiThirdUserProfile> {
		const url = new URL(`/api/user/v2/user/${userId}`, this.#baseUrl);
		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	// secrets

	async createSecret(
		orgId: number,
		appId: string,
		key: string,
		data: unknown,
	): Promise<WriterApiSecretResponse> {
		const res = await fetch(this.#getSecretUrl(orgId, appId), {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({ key, secret: data }),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async fetchSecret(
		orgId: number,
		appId: string,
		key: string,
	): Promise<WriterApiSecretResponse> {
		const res = await fetch(
			this.#getSecretUrl(orgId, appId, key),
			this.#requestInitBase,
		);
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async deleteSecret(orgId: number, appId: string, key: string) {
		const res = await fetch(this.#getSecretUrl(orgId, appId, key), {
			...this.#requestInitBase,
			method: "DELETE",
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async updateSecret(
		orgId: number,
		appId: string,
		key: string,
		data: unknown,
	): Promise<WriterApiSecretResponse> {
		const res = await fetch(this.#getSecretUrl(orgId, appId, key), {
			...this.#requestInitBase,
			method: "PUT",
			body: JSON.stringify({ key, secret: data }),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	#getSecretUrl(orgId: number, appId: string, key?: string) {
		const url = new URL(
			`/api/template/organization/${orgId}/agent/${appId}/secret`,
			this.#baseUrl,
		);

		return key ? `${url}/${key}` : url;
	}

	async fetchMcpConnectedApps(
		orgId: number,
		appId?: string,
	): Promise<WriterApiMcpApp[]> {
		const url = new URL(
			`/api/mcp-gateway/v2/organization/${orgId}/app-configurations`,
			this.#baseUrl,
		);
		const params = new URLSearchParams({
			limit: "100",
		});

		const headers = {
			...this.#requestInitBase.headers,
		};

		if (appId) {
			headers["X-Agent-Id"] = appId;
		}

		const requestUrl = `${url}?${params.toString()}`;

		const res = await fetch(requestUrl, {
			...this.#requestInitBase,
			headers,
		});

		if (!res.ok) {
			const errorText = await res.text();
			throw Error(errorText);
		}

		const data = await res.json();

		return data.result || [];
	}

	async fetchMcpAppFunctions(
		appId: string,
		agentId?: string,
	): Promise<WriterApiMcpFunction[]> {
		const url = new URL(
			`/api/mcp-gateway/v1/functions/list/${appId}`,
			this.#baseUrl,
		);

		const headers = {
			...this.#requestInitBase.headers,
		};

		if (agentId) {
			headers["X-Agent-Id"] = agentId;
		}

		const res = await fetch(url, {
			...this.#requestInitBase,
			headers,
		});

		if (!res.ok) {
			const errorText = await res.text();
			throw Error(errorText);
		}

		return await res.json();
	}

	async fetchMcpTools(
		orgId: number,
		appId?: string,
	): Promise<WriterApiMcpTool[]> {
		const apps = await this.fetchMcpConnectedApps(orgId, appId);
		const allTools: WriterApiMcpTool[] = [];

		for (const app of apps) {
			const appConfigId = app.appId;
			if (!appConfigId) {
				continue;
			}

			try {
				const functions = await this.fetchMcpAppFunctions(
					appConfigId,
					appId,
				);

				const allFunctionsEnabled = app.allFunctionsEnabled ?? true;
				const enabledFunctions = app.enabledFunctions || [];

				let filteredFunctions: WriterApiMcpFunction[];
				if (allFunctionsEnabled) {
					filteredFunctions = functions;
				} else if (enabledFunctions.length > 0) {
					filteredFunctions = functions.filter(
						(func) =>
							func.name && enabledFunctions.includes(func.name),
					);
				} else {
					filteredFunctions = [];
				}

				const appName =
					app.connector?.displayName ||
					app.connector?.name ||
					app.name ||
					"";

				for (const func of filteredFunctions) {
					allTools.push({
						appId: appConfigId,
						appName,
						functionName: func.name || "",
						function: func,
						connector: app.connector
							? {
									logo: app.connector.logo,
								}
							: undefined,
					});
				}
			} catch (e) {
				useLogger().error("Error fetching MCP app functions:", e);
			}
		}

		return allTools;
	}

	async fetchConfigJs(): Promise<string> {
		const url = new URL(`/env/config.js`, this.#baseUrl);
		const res = await fetch(url, {
			signal: this.#signal,
			credentials: "include",
			headers: {
				"X-Client": "Framework",
			},
			...this.#requestInitBase,
		});
		if (!res.ok) {
			const errorText = await res.text();
			throw Error(errorText);
		}
		return res.text();
	}

	// Shared blueprints

	#getAgentStorageBaseUrl(): string {
		return (
			import.meta.env.VITE_AGENT_STORAGE_URL ||
			this.#baseUrl
		);
	}

	async publishSharedBlueprint(
		orgId: number,
		data: {
			title: string;
			description: string;
			components: unknown;
			metadata: {
				name?: string;
				stateInputs?: string[];
				stateOutputs?: string[];
				vaultKeys?: string[];
				dependencies?: unknown[];
				author?: string;
			};
		},
	): Promise<{ snippet_id: string }> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/organization/${orgId}/shared-blueprints`,
			baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({
				title: data.title,
				description: data.description,
				components: data.components,
				metadata: data.metadata,
			}),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async listSharedBlueprints(
		orgId: number,
		search?: string,
	): Promise<
		Array<
			Pick<
				WriterApiSharedBlueprint,
				"id" | "title" | "description" | "category" | "createdBy"
			>
		>
	> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/organization/${orgId}/shared-blueprints`,
			baseUrl,
		);

		if (search) {
			url.searchParams.append("search", search);
		}

		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async getSharedBlueprint(
		orgId: number,
		blueprintId: string,
	): Promise<WriterApiSharedBlueprint> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/organization/${orgId}/shared-blueprints/${blueprintId}`,
			baseUrl,
		);

		const res = await fetch(url, this.#requestInitBase);
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async deleteSharedBlueprint(
		orgId: number,
		blueprintId: string,
	): Promise<void> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/organization/${orgId}/shared-blueprints/${blueprintId}`,
			baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "DELETE",
		});
		if (!res.ok) throw Error(await res.text());
	}

	async trackBlueprintInstallation(
		orgId: number,
		blueprintId: string,
		appId: string,
	): Promise<{ id: string }> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/organization/${orgId}/shared-blueprints/installations`,
			baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({
				blueprint_id: blueprintId,
				app_id: appId,
			}),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}

	async proposeGlobalBlueprint(data: {
		title: string;
		description: string;
		components: unknown;
		metadata: {
			name?: string;
			stateInputs?: string[];
			stateOutputs?: string[];
			vaultKeys?: string[];
			dependencies?: unknown[];
			author?: string;
		};
	}): Promise<{ pr_url: string; branch_name: string; blueprint_id: string }> {
		const baseUrl = this.#getAgentStorageBaseUrl();
		const url = new URL(
			`/api/agent-storage/v1/global-blueprints/propose`,
			baseUrl,
		);

		const res = await fetch(url, {
			...this.#requestInitBase,
			method: "POST",
			body: JSON.stringify({
				title: data.title,
				description: data.description,
				components: data.components,
				metadata: data.metadata,
			}),
		});
		if (!res.ok) throw Error(await res.text());

		return res.json();
	}
}

export type WriterApiUser = Pick<
	WriterApiUserProfile,
	"id" | "avatar" | "firstName" | "lastName" | "email"
>;

export type WriterApiSharedBlueprint = {
	id: string;
	title: string;
	description: string;
	category: string;
	visibility: string;
	orgId: string;
	createdBy: number;
	components: unknown;
	metadata: unknown;
	createdAt: string;
	updatedAt: string;
};

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

export type WriterApiMcpApp = {
	allFunctionsEnabled: boolean;
	appId: string;
	connector?: {
		name: string;
		displayName: string;
		logo: string;
		scopes: null;
	};
	displayName: string;
	name: string | null;
	scopes: null;
	createdAt: string;
	createdBy: number;
	createdByTeamId: null;
	credentialLevel: string;
	credentialManager: string;
	description: null;
	enabled: boolean;
	enabledFunctions: string[];
	id: string;
	linkedAccountId: null;
	orgId: number;
	securityScheme: string;
	securitySchemeOverrides: Record<string, unknown>;
	status: string;
	teamIds: number[];
	tenantUrl: null;
	totalToolCount: number;
	updatedAt: string;
	visibility: string;
};

export type WriterApiMcpFunction = {
	name: string;
	description?: string;
	parameters?: Record<string, unknown>;
	[key: string]: unknown;
};

export type WriterApiMcpTool = {
	appId: string;
	appName: string;
	functionName: string;
	function: WriterApiMcpFunction;
	connector?: {
		logo?: string;
	};
};
