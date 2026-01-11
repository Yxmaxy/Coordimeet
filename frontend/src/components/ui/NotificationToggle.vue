<template>
    <button
        v-if="isLoading"
        disabled
        class="hover:bg-main-400 transition-colors flex items-center justify-between"
    >
        Loading ...
        <span class="material-symbols-outlined align-middle text-lg animate-spin">progress_activity</span>
    </button>
    <button
        v-else-if="!isSupported"
        disabled
        class="hover:bg-main-400 transition-colors flex items-center justify-between"
    >
        Notifications not supported
        <span class="material-symbols-outlined align-middle text-lg">notifications_off</span>
    </button>
    <button
        v-else
        :disabled="disabled"
        @click="handleToggle"
        class="hover:bg-main-400 transition-colors flex items-center justify-between"
    >
        {{ isSubscribed ? "Disable notifications" : "Enable notifications" }}
        <span class="material-symbols-outlined align-middle text-lg">{{ isSubscribed ? "notifications" : "notifications_off" }}</span>
    </button>
</template>

<script lang="ts">
import NotificationService from "@/utils/NotificationService";
import { useStoreMessages } from "@/stores/storeMessages";

export default {
    name: "NotificationToggle",
    props: {
        disabled: {
            type: Boolean,
            default: false,
        },
    },
    setup() {
        const storeMessages = useStoreMessages();
        return {
            storeMessages,
        };
    },
    data() {
        return {
            isSupported: false,
            isSubscribed: false,
            isLoading: false,
        };
    },
    methods: {
        async initializeNotifications() {
            this.isLoading = true;
            try {
                const supported = await NotificationService.initialize();
                this.isSupported = supported;

                if (supported) {
                    const subscribed = await NotificationService.isSubscribed();
                    this.isSubscribed = subscribed;
                }
            } catch (error) {
                this.storeMessages.showMessageError("Failed to initialize notifications");
            }
            this.isLoading = false;
        },
        async handleToggle() {
            if (!this.isSupported) return;

            this.isLoading = true;
            try {
                await NotificationService.initialize();
                if (this.isSubscribed) {
                    const success = await NotificationService.unsubscribe();
                    if (success) {
                        this.isSubscribed = false;
                    } else {
                        this.storeMessages.showMessageError("Failed to unsubscribe from notifications");
                    }
                } else {
                    const success = await NotificationService.subscribe();
                    if (success) {
                        this.isSubscribed = true;
                    } else {
                        this.storeMessages.showMessageError("Failed to subscribe to notifications");
                    }
                }
            } catch (error) {
                this.storeMessages.showMessageError("An error occurred while toggling notifications");
            }
            this.isLoading = false;
        },
    },
    async mounted() {
        await this.initializeNotifications();
    },
}
</script>
