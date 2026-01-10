import { defineStore } from "pinia";
import { CoordimeetUser } from "@/types/user";

import ApiService from "@/utils/ApiService";

import { useStoreMessages } from "@/stores/storeMessages";

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
        async onLogin(email: string, password: string): Promise<boolean> {
            const storeMessages = useStoreMessages();

            if (!email || !password) {
                storeMessages.showMessageError("Please fill in all fields!");
                return false;
            }
            
            // retrieve access token
            try {
                const response: any = await ApiService.post("/users/token/", {
                    email, password
                });
                
                if (response.status !== 200) {
                    return false;
                }

                // await saveTokens(response.data.access, response.data.refresh);
                await this.getUser();
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
                const response: any = await ApiService.post("/users/user/", {
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
            // await removeTokens();
            const registration = await navigator.serviceWorker.ready;
            registration.active?.postMessage({
                type: "UNSUBSCRIBE_NOTIFICATIONS",
            });
            this.user = undefined;
        },
        async onCreateAnonymousUser(): Promise<boolean> {
            // create a new anonymous user
            try {
                const response: any = await ApiService.post("/users/anonymous/");
                if (response.status === 201) {
                    // await saveTokens(response.data.access, response.data.refresh);
                    await this.getUser();
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
    },
    getters: {
        isLoggedIn: (state) => !!state.user,
    }
})
