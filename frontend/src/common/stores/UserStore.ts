import { defineStore } from 'pinia';
import { developmentMode } from '../globals';
import { IUser } from '../interfaces';

export const useUserStore = defineStore("UserStore", {
    state: () => {
        if (developmentMode)
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
    }
})
