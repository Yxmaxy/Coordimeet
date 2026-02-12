import { defineStore } from "pinia";
import { CoordimeetUser } from "@/types/user";

import { useStoreMessages } from "@/stores/storeMessages";

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
        async checkIfLoggedIn() {
            const response = await ApiService.get<{is_logged_in: boolean}>("/users/is-logged-in/");
            return response.is_logged_in;
        },
        async getUser() {
            if (this.user) return;
            const response = await ApiService.get<CoordimeetUser>("/users/current-user/");
            this.user = response;
            if (this.user?.is_anonymous) {
                const storeMessages = useStoreMessages();
                storeMessages.showMessage("You are logged in as an anonymous user");
            }
        },
        async onLogout() {
            await NotificationService.unsubscribe();
            window.location.href = import.meta.env.VITE_LOGOUT_URL;
            this.user = undefined;
        },
    },
    getters: {
        isLoggedIn: (state) => !!state.user,
    }
})
