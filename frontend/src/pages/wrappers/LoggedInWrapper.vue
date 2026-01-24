<template>
    <div v-if="!storeUser.isLoggedIn" class="flex justify-center items-center h-screen">
        <div class="text-2xl font-bold">
            <custom-icon icon="progress_activity" class="text-4xl animate-spin text-main-400" />
        </div>
    </div>
    <template v-else>
        <app-header>
            <user-component />
        </app-header>
        <slot></slot>
    </template>
</template>

<script lang="ts">
import { useStoreUser } from "@/stores/storeUser";
import AppHeader from "@/components/AppHeader.vue";
import UserComponent from "@/components/UserComponent.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "LoggedInWrapper",
    components: {
        CustomIcon,
        AppHeader,
        UserComponent,
    },
    setup() {
        const storeUser = useStoreUser();
        return {
            storeUser,
        }
    },
    async mounted() {
        await this.storeUser.getUser();
    },
}
</script>
