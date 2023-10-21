<template>
    <a
        v-if="!userStore.isLoggedIn"
        class="btn z-50"
        :href="userStore.loginLink"
    >
        Log in
    </a>
    <div
        v-else
        class="h-full relative"
    >
        <div
            @click="showLogout = !showLogout"
            class="h-full flex items-center cursor-pointer select-none"
        >
            <span class="font-bold">
                {{ userStore.user!.FirstName }}
            </span>
            <img
                class="rounded-full h-full p-2 select-none"
                :src="userStore.user!.ProfilePhoto"
                referrerpolicy="no-referrer"
                alt="profile"
            />
        </div>
        <!-- Popup -->
        <div v-if="showLogout">
            <!-- Popup triangle -->
            <div class="absolute -bottom-1 right-5
                border-l-transparent border-t-transparent border-r-transparent border-b-main-400 border-8"></div>
            <!-- Content -->
            <div class="absolute w-screen right-0 pl-10 pt-1 max-w-[20rem]">
                <div class="flex flex-col bg-main-400 rounded-lg [&>*]:p-4 shadow-md">
                    <a :href="logoutLink">
                        Log out
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { useUserStore } from "@/stores/UserStore";

export default {
    setup() {
        const userStore = useUserStore();
        return {
            userStore,
            logoutLink: `${import.meta.env.VITE_BACKEND_URL}/googleLogout.php`,
        }
    },
    data() {
        return {
            showLogout: false,
        }
    },
}
</script>
