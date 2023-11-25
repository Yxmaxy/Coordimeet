<template>
    <div class="bg-main-000">
        <tab-controller :tabs="tabs">
            <template v-slot:events_invited>
                <event-list-component :events="eventsInvited" />
            </template>
            <template v-slot:events_created>
                <event-list-component :events="eventsCreated" :userIsOrganiser="true" />
            </template>
        </tab-controller>
        <custom-button
            class="right-4 bottom-4 fixed !p-3 !rounded-2xl shadow-md"
            :click="() => $router.push('/event/new')"
        >
            + New event
        </custom-button>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useUserStore } from "@/stores/UserStore";

import { Event } from "@/types/event";
import { Tab } from "@/types/tabs";

import EventListComponent from "@/components/EventListComponent.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

const tabs = [
    {
        name: "Events I'm invited to",
        slot_name: "events_invited",
    },
    {
        name: "Events I've created",
        slot_name: "events_created",
    }
] as Tab[];

export default {
    name: "EventList",
    components: {
        EventListComponent,
        TabController,
        CustomButton,
    },
    setup() {
        const { user } = useUserStore();
        return {
            user,
            tabs,
        }
    },
    data() {
        return {
            eventsInvited: [] as Event[],
            eventsCreated: [] as Event[],
        }
    },
    methods: {
        getEvents() {
            ApiService.get("eventUser.php", {
                params: {
                    IDUser: this.user!.GoogleID,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    this.$router.push("/");
                    return;
                }
                this.eventsInvited = res.data.Invited;
                this.eventsCreated = res.data.Created;
            });
        },
    },
    mounted() {
        this.getEvents();
    },
}
</script>
