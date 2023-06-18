import { defineStore } from 'pinia';
import { User } from '@/types/user';
import ApiService from "@/utils/ApiService";

export const useUserStore = defineStore("UserStore", {
    state: () => {
        return {
            isLoggedIn: false,
            user: {} as User,
        }
    },
    actions: {
        async loginUser(): Promise<boolean> {
            if (this.isLoggedIn)
                return true;
            const res = await ApiService.get("googleLogin.php");
            if ("googleLoginURL" in res.data)
                return false;
            this.isLoggedIn = true;
            this.user = res.data;
            return true;
        }
    }
})
