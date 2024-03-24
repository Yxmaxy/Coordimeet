<template>
    <div class="bg-main-000">
        <tab-controller :tabs="tabs" :breakpoint="750">
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
            <custom-icon icon="add"/> New event
        </custom-button>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useStoreUser } from "@/stores/storeUser";

import { Event } from "@/types/event";
import { Tab } from "@/types/tabs";

import EventListComponent from "@/components/EventListComponent.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

const tabs = [
    {
        name: "Events I'm invited to",
        slot_name: "events_invited",
        icon: "group",
    },
    {
        name: "Events I've created",
        slot_name: "events_created",
        icon: "engineering",
    }
] as Tab[];

export default {
    name: "EventList",
    components: {
        EventListComponent,
        TabController,
        CustomButton,
        CustomIcon,
    },
    setup() {
        const { user } = useStoreUser();
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
            ApiService.get("/events/event/")
            .then(res => {
                this.eventsInvited = res.data.filter((event: Event) => event.organiser?.id !== this.user?.id);
                this.eventsCreated = res.data.filter((event: Event) => event.organiser?.id === this.user?.id);
            })
            .catch(() => {
                alert(`Pri pridobivanju podatkov je prišlo do napake.`)
            });
        },
    },
    mounted() {
        this.getEvents();
    },
}
</script>
