import { defineStore } from 'pinia';
import axios from 'axios';
import { developmentMode } from '../globals';
import { IUser } from '../interfaces';

export const useUserStore = defineStore("UserStore", {
    state: () => {
        if (!developmentMode)
            return {
                isLoggedIn: true,
                user: {
                    Email: "vrecer.marko@gmail.com",
                    FirstName: "Marko",
                    GoogleID: "110672583056965135304",
                    LastName: "Vrečer",
                    ProfilePhoto: "https://lh3.googleusercontent.com/a/AEdFTp6jLmYJg8rLt26Dm2F9SbDq0tc2HI_qTZwA2knwYw=s96-c"
                } as IUser,
            }
        else
            return {
                isLoggedIn: false,
                user: {} as IUser,
            }
    },
    actions: {
        async loginUser() {
            if (this.isLoggedIn)
                return;
            const res = await axios.get("https://coordimeet.eu/backend/googleLogin.php");
            if ("googleLoginURL" in res.data)
                return;
            this.isLoggedIn = true;
            this.user = res.data;
        }
    }
})
