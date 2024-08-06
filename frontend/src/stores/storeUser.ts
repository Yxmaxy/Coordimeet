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
            const storeMessages = useStoreMessages();

            if (!email || !password) {
                storeMessages.showMessageError("Please fill in all fields!");
                return false;
            }
            
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
                await this.requestNotifications();
                
                return true;
            } catch (error: any) {
                storeMessages.showMessageError(error.response.data.detail);
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
            const registration = await navigator.serviceWorker.ready;
            registration.active?.postMessage({
                type: "UNSUBSCRIBE_NOTIFICATIONS",
            });
            this.user = undefined;
        },
        async onCreateAnonymousUser(): Promise<boolean> {
            // create a new anonymous user
            try {
                const response = await ApiService.post("/users/anonymous/");
                if (response.status === 201) {
                    await saveTokens(response.data.access, response.data.refresh);
                    await this.getUserFromToken();
                    await this.requestNotifications();

                    return true;
                }
            } catch (error: any) {
                const storeMessages = useStoreMessages();
                storeMessages.showMessageError(error.response.data.error);
            }
            return false;
        },

        // request notifications
        async requestNotifications() {
            // register user to notifications
            if ("serviceWorker" in navigator) {
                // retrieve notification permissions
                const notificationPermission = await Notification.requestPermission();
                if (notificationPermission === "granted") {
                    // send message to service worker to register user to notifications
                    const registration = await navigator.serviceWorker.ready;
                    registration.active?.postMessage({
                        user_id: this.user?.id,
                        type: "REGISTER_NOTIFICATIONS",
                    });
                    return true;
                }
            }
            return false;
        }
    }
})
