import { defineStore } from "pinia";
import { Message, MessageType } from "@/types/message";

export const useStoreMessages = defineStore("storeMessages", {
    state: () => {
        return {
            message: null as Message|null,
            _messageTimeout: null as number|null,
        }
    },
    actions: {
        showMessage(message: string, timeout: number|null = null) {
            this._showMessage(message, MessageType.INFO, timeout);
        },
        showMessageError(message: string, timeout: number|null = null) {
            this._showMessage(message, MessageType.ERROR, timeout);
        },
        showMessageSuccess(message: string, timeout: number|null = null) {
            this._showMessage(message, MessageType.SUCCESS, timeout);
        },
        _showMessage(message: string, messageType: MessageType = MessageType.INFO, timeout: number|null = null) {
            this.message = {
                content: message,
                type: messageType,
            } as Message;

            if (timeout) {
                // clear previous timeout
                if (this._messageTimeout) {
                    clearTimeout(this._messageTimeout);
                }
                // add new timeout
                this._messageTimeout = setTimeout(() => {
                    this.hideMessage();
                    this._messageTimeout = null;
                }, timeout);
            }
        },
        hideMessage() {
            if (this.message) {
                this.message = null;
            }
        },
    }
});
