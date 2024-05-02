<template>
    <transition name="fade">
        <div
            v-if="storeMessages.message"
            :class="[{
                '!bg-calendar-available': storeMessages.message.type === MessageType.SUCCESS,
                '!bg-calendar-unavailable': storeMessages.message.type === MessageType.ERROR,
            }, 'fixed bottom-0 left-0 z-50',
                'bg-main-000 border-2 border-main-400',
                'max-w-md m-4 p-2 rounded-md shadow-lg']"
        >
            <div class="flex justify-end">
                <custom-icon
                    class="cursor-pointer"
                    icon="close"
                    @click="storeMessages.hideMessage"
                />
            </div>
            <div class="p-1.5">
                {{ storeMessages.message.content }}
            </div>
        </div>
    </transition>
</template>

<script lang="ts">
import { Transition } from "vue";
import { useStoreMessages } from "@/stores/storeMessages";

import { MessageType } from "@/types/message";

import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "Message",
    components: {
        CustomIcon,
    },
    setup() {
        const storeMessages = useStoreMessages();
        return {
            storeMessages,
            MessageType,
        }
    },
}
</script>
