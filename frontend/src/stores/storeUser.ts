import { defineStore } from 'pinia';
import { User } from '@/types/user';
import ApiService from "@/utils/ApiService";
import { saveTokens, retrieveUserID, removeTokens } from "@/utils/tokens";

export const useStoreUser = defineStore("storeUser", {
    state: () => {
        return {
            user: undefined as User | undefined,
        }
    },
    getters: {
        isLoggedIn: (state) => state.user !== undefined,
    },
    actions: {
        async retrieveUser(): Promise<User|undefined> {
            // return the user if it's already retrieved
            if (this.user)
                return this.user;
            // retrieve user information from the API
            const userID = retrieveUserID();
            if (!userID)
                return undefined;
            const userResponse = await ApiService.get(`/users/user/${userID}/`);
            if (userResponse.status === 200) {
                this.user = userResponse.data;
                return this.user;
            }
            return undefined;
        },
        async onLogin(email: string, password: string): Promise<boolean> {
            // retrieve access token
            const response = await ApiService.post("/users/token/", {
                email, password
            });
            if (response.status === 200) {
                saveTokens(response.data.token, response.data.id);
                return await this.retrieveUser() !== undefined;
            }
            return false;
        },
        onLogout() {
            removeTokens();
            this.user = undefined;
        }
    }
})
