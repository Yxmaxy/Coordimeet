import { defineStore } from 'pinia';
import { jwtDecode } from "jwt-decode";
import { User } from '@/types/user';

import ApiService from "@/utils/ApiService";
import { retrieveTokens, saveTokens, removeTokens } from "@/utils/tokens";

import { useStoreMessages } from "@/stores/storeMessages";

export const useStoreUser = defineStore("storeUser", {
    state: () => {
        return {
            user: undefined as User|undefined,
            redirectAfterLogin: undefined as string|undefined,
        }
    },
    actions: {
        async isLoggedIn() {
            await this.getUserFromToken();
            return this.user !== undefined
        },
        async getUserFromToken() {
            // retrieve user from token
            const { refreshToken } = await retrieveTokens();
            if (refreshToken) {
                const userData = jwtDecode(refreshToken) as any;
                this.user = {
                    id: userData.user_id,
                    email: userData.email,
                    first_name: userData.first_name,
                    last_name: userData.last_name,
                } as User;
            }
        },
        async onLogin(email: string, password: string): Promise<boolean> {
            // retrieve access token
            try {
                const response = await ApiService.post("/users/token/", {
                    email, password
                });
                
                if (response.status !== 200) {
                    return false;
                }

                await saveTokens(response.data.access, response.data.refresh);
                await this.getUserFromToken();

                // register user to notifications
                if ("serviceWorker" in navigator) {
                    // retrieve notification permissions
                    const notificationPermission = await Notification.requestPermission();
                    if (notificationPermission === "granted") {
                        // send message to service worker to register user to notifications
                        const registration = await navigator.serviceWorker.ready;
                        registration.active?.postMessage({
                            user_id: this.user?.id,  // TODO: this could be read from the JWT
                            type: "REGISTER_NOTIFICATIONS",
                        });
                    }
                }
                return true;
            } catch (error: any) {
                const storeMessages = useStoreMessages();
                storeMessages.showMessageError(error.response.data.error);
            }
            return false;
        },
        async onSignup(email: string, password: string): Promise<boolean> {
            // create a new user
            try {
                const response = await ApiService.post("/users/user/", {
                    email, password
                });
                if (response.status === 201) {
                    return await this.onLogin(email, password);
                }
            } catch (error: any) {
                const storeMessages = useStoreMessages();
                storeMessages.showMessageError("A user with this email already exists!");
            }
            return false;
        },
        async onLogout() {
            await removeTokens();
            this.user = undefined;
        }
    }
})
