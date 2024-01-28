import { defineStore } from 'pinia';
import { User } from '@/types/user';
import ApiService from "@/utils/ApiService";

export const useUserStore = defineStore("UserStore", {
    state: () => {
        return {
            loginLink: "" as string,
            user: undefined as User | undefined,
        }
    },
    getters: {
        isLoggedIn: (state) => state.user !== undefined,
    },
    actions: {
        async tryToLoginUser(): Promise<boolean> {
            if (this.isLoggedIn)
                return true;
            const res = await ApiService.get("googleLogin.php");
            if (res.status !== 200)
                return false;
            if ("googleLoginURL" in res.data) {
                this.loginLink = res.data.googleLoginURL;
                return false;
            }
            this.user = res.data;
            return true;
        }
    }
})
