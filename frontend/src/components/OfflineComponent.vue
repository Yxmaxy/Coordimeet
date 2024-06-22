<template>
    <transition name="fadeHeight">
        <div
            v-if="!storeOnline.isOnline"
            class="sticky top-14 left-0 right-0 h-6 items-center bg-main-400 text-main-000 transition-all text-sm flex justify-center gap-1"
        >
            You're offline <custom-icon class="text-sm" icon="wifi_off" />
        </div>
    </transition>
</template>

<script lang="ts">
import { Transition } from "vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

import { useStoreOnline } from "@/stores/storeOnline";

export default {
    name: "OfflineComponent",
    components: {
        Transition,
        CustomIcon,
    },
    setup() {
        const storeOnline = useStoreOnline();
        return {
            storeOnline,
        }
    },
    methods: {
        handleOffline() {
            this.storeOnline.isOnline = false;
        },
        handleOnline() {
            this.storeOnline.isOnline = true;
        },
    },
    mounted() {
        window.addEventListener("offline", this.handleOffline);
        window.addEventListener("online", this.handleOnline);
        if (navigator.onLine) {
            this.handleOnline();
        } else {
            this.handleOffline();
        }
    },
    unmounted() {
        window.removeEventListener("offline", this.handleOffline);
        window.removeEventListener("online", this.handleOnline);
    },
}
</script>

<style scoped>
/* fade height */
.fadeHeight-enter-active,
.fadeHeight-leave-active {
    transition: height 150ms linear;
    height: 20px;
}
.fadeHeight-enter-from,
.fadeHeight-leave-to {
    height: 0;
}
.fadeHeight-enter-to,
.fadeHeight-leave-from {
    height: 20px;
}
</style>
