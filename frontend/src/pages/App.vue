<!-- Wrapper page for all other pages -->
<template>
    <div class="min-h-screen">
        <template v-if="!storeUser.isLoggedIn">
            <div class="flex justify-center items-center h-screen">
                <div class="text-2xl font-bold">
                    <custom-icon icon="progress_activity" class="text-4xl animate-spin text-main-400" />
                </div>
            </div>
        </template>
        <template v-else>
            <header class="sticky top-0 h-14 flex items-center justify-between pl-2 pr-4 bg-main-200 z-30">
                <img
                    class="h-12 p-2 cursor-pointer"
                    src="/images/logo.svg"
                    alt="logo"
                    @click="$router.push('/')"
                />
                <user-component />
            </header>
            <router-view class="min-h-[calc(100vh-3.5rem)] h-full" />
            <message />
        </template>
    </div>
</template>

<script lang="ts">
import UserComponent from "@/components/UserComponent.vue";
import Message from "@/components/ui/Message.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

import { useStoreUser } from "@/stores/storeUser";

export default {
    name: "App",
    components: {
        UserComponent,
        Message,
        CustomIcon,
    },
    setup() {
        const storeUser = useStoreUser();
        return {
            storeUser,
        }
    },
    async mounted() {
        await this.storeUser.getUser();
    }
}
</script>
