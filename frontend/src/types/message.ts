export enum MessageType {
    ERROR = "error",
    SUCCESS = "success",
    INFO = "info",
}

export interface Message {
    content: string;
    type: MessageType,
}
