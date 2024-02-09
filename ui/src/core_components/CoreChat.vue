<template>
	<div class="CoreChat" ref="rootEl">
		<div class="messageArea" ref="messageAreaEl">
			<div class="message" :class="message.origin" v-for="message, messageId in messages" :key="messageId">
				<div class="avatar">{{ message.origin == 'incoming' ? fields.incomingInitials.value : fields.outgoingInitials.value }}</div>
				<div class="contents">
					<template v-if="message.isLoading">
						<LoadingSymbol></LoadingSymbol>
					</template>
					<template v-else>
						{{ message.content }}
					</template>
				</div>
				<div class="time" v-if="message.date" :title="getFormattedDate(message.date, false)">{{ getFormattedDate(message.date, true) }}</div>
			</div>
		</div>
		<div class="inputArea">
			<textarea placeholder="Write something..." v-model="outgoingMessage" v-on:keydown.prevent.enter="handleMessageSent"></textarea>
			<button v-on:click="handleMessageSent"><i class="ri-send-plane-line"></i></button>
		</div>
	</div>
</template>

<script lang="ts">
import LoadingSymbol from "../renderer/LoadingSymbol.vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import { buttonColor, buttonTextColor, containerBackgroundColor, cssClasses, primaryTextColor, secondaryTextColor, separatorColor } from "../renderer/sharedStyleFields";
import { nextTick } from "vue";

const description =
	"A chat component to build human-to-AI interactions.";

const docs = `Chat
`;

export default {
	streamsync: {
		name: "Chat",
		description,
		docs,
		category: "Content",
		fields: {
			incomingInitials: {
				name: "Incoming initials",
				default: "AI",
				type: FieldType.Text
			},
			outgoingInitials: {
				name: "Outgoing initials",
				default: "YOU",
				type: FieldType.Text
			},
			incomingColor: {
				name: "Incoming",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true
			},
			outgoingColor: {
				name: "Outgoing",
				default: "#F5F5F9",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true
			},
			avatarBackgroundColor: {
				name: "Avatar",
				default: "#2C2D30",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true
			},
			avatarTextColor: {
				name: "Avatar text",
				default: "#FFFFFF",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true
			},
			containerBackgroundColor,
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			buttonColor,
			buttonTextColor,
			cssClasses,
		},
		events: {
			"chat-message": {
				desc: "Triggered when the user sends a message. Return a string to answer it."
			},
		},
		previewField: "name",
	},
	components: { LoadingSymbol },
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../injectionKeys";

type Message = {
	origin: "incoming" | "outgoing";
	content: string;
	isLoading?: boolean;
	date?: Date;
};

const rootEl:Ref<HTMLElement> = ref(null);
const messageAreaEl:Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const messages:Ref<Record<string, Message>> = ref({});
let messageCounter = 0;

const outgoingMessage:Ref<string> = ref("");

function getFormattedDate(date: Date, isTimeOnly:boolean) {
	if (!date) return;

	if (!isTimeOnly) {
		return date.toLocaleString();
	}

	const options:Intl.DateTimeFormatOptions = {
		hour: 'numeric',
		minute: 'numeric',
		hour12: true
	};
	return date.toLocaleTimeString(undefined, options);
}

async function addMessage(message: Message) {
	messageCounter += 1;
	const messageKey = `msg${messageCounter}`;
	messages.value[messageKey] = message;
	await nextTick();
	messageAreaEl.value.scrollTo(0, messageAreaEl.value.scrollHeight);
	return messageKey;
}

async function replaceMessage(messageKey: string, message: Message) {
	messages.value[messageKey] = message;
	await nextTick();
	messageAreaEl.value.scrollTo(0, messageAreaEl.value.scrollHeight);
}

async function handleMessageSent() {
	await addMessage({
		origin: "outgoing",
		content: outgoingMessage.value,
		date: new Date()
	});
	outgoingMessage.value = "";
	const outgoingMessageKey = await addMessage({
		origin: "incoming",
		content: "Loading...",
		isLoading: true
	});
	const event = new CustomEvent("chat-message", {
		detail: {
			payload: outgoingMessage.value,
			callback: ({payload}) => {
				const content:string = payload.result?.result;
				replaceMessage(outgoingMessageKey, {
					origin: "incoming",
					content,
					date: new Date()
				});
			}
		},
	});
	rootEl.value.dispatchEvent(event);
}

</script>
<style scoped>
@import "../renderer/sharedStyles.css";

.CoreChat {
	display: flex;
	flex-direction: column;
	height: 80vh;
	border-radius: 8px;
	overflow: hidden;
	background: var(--containerBackgroundColor);
	border: 1px solid var(--separatorColor);
}

.messageArea {
	padding: 16px;
	display: flex;
	gap: 16px;
	flex-direction: column;
	overflow-y: auto;
	overflow-x: hidden;
	flex: 0 0 80%;
}

.message {
	display: flex;
	gap: 8px;
}

.message .avatar {
	border-radius: 50%;
	background: var(--avatarBackgroundColor);
	color: var(--avatarTextColor);
	height: 36px;
	width: 36px;
	flex: 0 0 36px;
	display: flex;
	font-weight: bold;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	text-transform: uppercase;
}

.message .contents {
	line-height: 2.0;
	padding: 12px 16px 12px 16px;
	border-radius: 8px;
	width: fit-content;
	flex: 0 1 auto;
	color: var(--primaryTextColor);
	white-space: pre-wrap;
}

.message .time {
	color: var(--secondaryTextColor);
	font-size: 0.70rem;
	align-self: end;
	text-wrap: nowrap;
}

.message.incoming .contents {
	background: v-bind("fields.incomingColor.value ? fields.incomingColor.value : 'linear-gradient(264.27deg, rgb(245, 235, 255) 0.71%, rgb(255, 241, 237) 100%)'");
}

.message.outgoing .contents {
	background: var(--outgoingColor);
}

.inputArea {
	border-top: 1px solid var(--separatorColor);
	flex: 1 1 auto;
	text-align: right;
	display: flex;
	align-items: top;
}

.inputArea textarea {
	border: none;
	width: 100%;
	height: 100%;
	padding: 16px;
	resize: none;
	background: transparent;
	color: var(--primaryTextColor);
	font-size: 0.8rem;
}

.inputArea button {
	margin: 16px;
	height: fit-content;
	flex: 0 0 auto;
	display: flex;
	gap: 8px;
	align-items: center;
}

</style>
