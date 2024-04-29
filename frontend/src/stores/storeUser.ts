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
            const userID = await retrieveUserID();
            if (!userID)
                return undefined;
            try {
                const userResponse: any = await ApiService.get(`/users/user/${userID}/`);
                if (userResponse!.status === 200) {
                    this.user = userResponse.data;
                    return this.user;
                }
                return undefined;
            } catch (error) {
                console.error(error);
            }
        },
        async onLogin(email: string, password: string): Promise<boolean> {
            // retrieve access token
            const response = await ApiService.post("/users/token/", {
                email, password
            });
            if (response.status === 200) {
                await saveTokens(response.data.token, response.data.id);
                if ("serviceWorker" in navigator) {
                    // retrieve notification permissions
                    const notificationPermission = await Notification.requestPermission();
                    if (notificationPermission === "granted") {
                        // send message to service worker to register user to notifications
                        const registration = await navigator.serviceWorker.ready;
                        registration.active?.postMessage({
                            user_id: response.data.id,
                            type: "REGISTER_NOTIFICATIONS",
                        });
                    }
                }
                return await this.retrieveUser() !== undefined;
            }
            return false;
        },
        async onLogout() {
            await removeTokens();
            this.user = undefined;
        }
    }
})
