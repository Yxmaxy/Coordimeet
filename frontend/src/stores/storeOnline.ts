import { defineStore } from "pinia";

export const useStoreOnline = defineStore("storeOnline", {
    state: () => {
        return {
            isOnline: navigator.onLine,
        }
    },
});
