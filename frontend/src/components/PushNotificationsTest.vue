<template>
    <div class="flex flex-col gap-2">
        <label>
            Head
            <input type="text" name="head" v-model="head">
        </label>
        <label>
            Body
            <textarea name="body" cols="30" rows="10" v-model="body"></textarea>
        </label>
    </div>
    <custom-button :click="sendPush">Send</custom-button>
    
    <custom-button :click="subscribe">subscribe</custom-button>
    
    <custom-button :click="notify">notification</custom-button>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";

import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "PushNotificationsTest",
    components: {
        CustomButton,
    },
    data() {
        return {
            head: "My head",
            body: "My body",
        }
    },
    methods: {
        async sendPush() {
            ApiService.post("notifications/send/", {
                head: this.head,
                body: this.body,
                group_id: 4,
            });
        },
        subscribe() {
            // fetch("http://127.0.0.1:8080/subscribe", {
            //     method: "POST",
            //     headers: {
            //         "Content-Type": "application/json",
            //     },
            // });
        },
        notify() {
            Notification.requestPermission().then((permission) => {
                if (permission === "granted") {
                    new Notification("Hello, world!");
                }
            });
        }
    }
}
</script>
