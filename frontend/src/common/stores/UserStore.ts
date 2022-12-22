import { defineStore } from 'pinia';
import { IUser } from '../interfaces';

export const useUserStore = defineStore("UserStore", {
    state: () => {
        return {
            isLoggedIn: false,
            user: {} as IUser,
        }
    }
})
