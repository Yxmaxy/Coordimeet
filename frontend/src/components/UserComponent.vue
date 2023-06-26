<template>
    <a
        v-if="!userStore.isLoggedIn"
        class="btn"
        :href="userStore.loginLink"
    >
        Log in
    </a>
    <div
        v-else
        class="h-full"
    >
        <Popup v-model:show="showLogout">
            <template v-slot:initiator>
                <div class="h-full flex items-center cursor-pointer select-none">
                    <span class="font-bold">
                        {{ userStore.user!.FirstName }}
                    </span>
                    <img
                        class="rounded-full h-full p-2"
                        :src="userStore.user!.ProfilePhoto"
                        referrerpolicy="no-referrer"
                        alt="profile"
                    />
                </div>
            </template>
            <template v-slot:content>
                Neki
            </template>
        </Popup>
    </div>
    <!-- <a 
        v-else
        class="btn"
        :href="logoutLink"
    >
        Log out
    </a> -->
</template>

<script lang="ts">
import { useUserStore } from "@/stores/UserStore";

import Popup from "@/components/Popup.vue"

export default {
    setup() {
        const userStore = useUserStore();
        return {
            userStore,
            logoutLink: `${import.meta.env.VITE_BACKEND_URL}/googleLogout.php`,
        }
    },
    components: {
        Popup,
    },
    data() {
        return {
            showLogout: true,
        }
    },
}
</script>
