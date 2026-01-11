import { defineStore } from "pinia";
import { CoordimeetUser } from "@/types/user";

import ApiService from "@/utils/ApiService";

import NotificationService from "@/utils/NotificationService";


export const useStoreUser = defineStore("storeUser", {
    state: () => {
        return {
            user: undefined as CoordimeetUser|undefined,
            redirectAfterLogin: undefined as string|undefined,
        }
    },
    actions: {
        async getUser() {
            if (this.user) return;
            const response = await ApiService.get<CoordimeetUser>("/users/current-user/");
            this.user = response;
        },
        async onLogout() {
            window.location.href = import.meta.env.VITE_LOGOUT_URL;
            await NotificationService.unsubscribe();
            this.user = undefined;
        },
    },
    getters: {
        isLoggedIn: (state) => !!state.user,
    }
})
