<template>
    <div
        v-if="userStore.isLoggedIn"
        class="h-full relative"
    >
        <div
            @click="showLogout = !showLogout"
            class="h-full flex items-center cursor-pointer select-none"
        >
            <span class="font-bold">
                {{ userDisplayName }}
            </span>
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
                    <button @click="onLogout" class="hover:bg-main-400 transition-colors text-left">
                        Log out
                    </button>
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
import { useStoreUser } from "@/stores/storeUser";
import { setTheme, Theme } from "@/utils/theme";

import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "UserComponent",
    components: {
        CustomButton,
    },
    setup() {
        const userStore = useStoreUser();
        return {
            userStore,
            Theme,
        }
    },
    data() {
        return {
            showLogout: false,
        }
    },
    computed: {
        userDisplayName() {
            if (this.userStore.user!.first_name && this.userStore.user!.last_name)
                return `${this.userStore.user!.first_name} ${this.userStore.user!.last_name}`;
            if (this.userStore.user!.first_name)
                return this.userStore.user!.first_name;
            return this.userStore.user!.email;
        }
    },
    methods: {
        setTheme,
        onLogout() {
            this.userStore.onLogout();
            this.showLogout = false;
            this.$router.push("/");
        }
    }
}
</script>
