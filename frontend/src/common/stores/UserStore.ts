import { defineStore } from 'pinia';
import axios from 'axios';
import { apiServer } from '../globals';
import { IUser } from '../interfaces';

export const useUserStore = defineStore("UserStore", {
    state: () => {
        return {
            isLoggedIn: false,
            user: {} as IUser,
        }
    },
    actions: {
        async loginUser(): Promise<boolean> {
            if (this.isLoggedIn)
                return true;
            const res = await axios.get(`${apiServer}/googleLogin.php`);
            if ("googleLoginURL" in res.data)
                return false;
            this.isLoggedIn = true;
            this.user = res.data;
            return true;
        }
    }
})
