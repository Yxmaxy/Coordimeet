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
                class="rounded-full w-14 p-2 select-none"
                :src="userStore.user!.ProfilePhoto"
                referrerpolicy="no-referrer"
                alt="profile"
            />
        </div>
        <!-- Background -->
        <div
            v-if="showLogout"
            class="fixed left-0 right-0 top-0 bottom-0"
            @click="showLogout = false"
        ></div>
        <!-- Popup -->
        <div v-if="showLogout">
            <!-- Popup triangle -->
            <div class="absolute -bottom-1 right-5
                border-l-transparent border-t-transparent border-r-transparent border-b-main-400 border-8"></div>
            <!-- Content -->
            <div class="absolute w-screen right-0 pl-10 pt-1 max-w-[20rem]">
                <div class="flex flex-col bg-main-300 border-2 border-main-400 rounded-lg [&>*]:p-4 shadow-md">
                    <a :href="logoutLink" class="hover:bg-main-400 transition-colors">
                        Log out
                    </a>
                    <div class="flex justify-between">
                        Theme
                        <div class="flex gap-1 [&>*]:h-5 [&>*]:w-5 [&>*]:rounded-sm [&>*]:border-2 [&>*]:border-main-600 [&>*]:cursor-pointer">
                            <div
                                @click="setTheme(Theme.BLUE)"
                                class="bg-[#41b9d6]"
                            ></div>
                            <div
                                @click="setTheme(Theme.GREEN)"
                                class="bg-[#41D6A9]"
                            ></div>
                            <div
                                @click="setTheme(Theme.PINK)"
                                class="bg-[#e178cd]"
                            ></div>
                            <div
                                @click="setTheme(Theme.DARK)"
                                class="bg-[#2a393f]"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { useUserStore } from "@/stores/UserStore";
import { setTheme, Theme } from "@/utils/theme";

export default {
    setup() {
        const userStore = useUserStore();
        return {
            userStore,
            logoutLink: `${import.meta.env.VITE_BACKEND_URL}/googleLogout.php`,
            Theme,
        }
    },
    data() {
        return {
            showLogout: false,
        }
    },
    methods: {
        setTheme,
    }
}
</script>
