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
            v-if="storeOnline.isOnline && !user?.is_anonymous"
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
import { useStoreMessages } from "@/stores/storeMessages";
import { useStoreOnline } from "@/stores/storeOnline";

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
        const storeMessages = useStoreMessages();
        const storeOnline = useStoreOnline();
        return {
            user,
            tabs,

            storeMessages,
            storeOnline,
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
            ApiService.get<Event[]>("/events/event/list/")
                .then(res => {
                    this.eventsCreated = res;
                })
                .catch(e => {
                    this.storeMessages.showMessageError(`An error occurred while fetching the events.`)
                    throw e;
                });

            ApiService.get<Event[]>("/events/event/invited/")
                .then(res => {
                    this.eventsInvited = res;
                })
                .catch(e => {
                    this.storeMessages.showMessageError(`An error occurred while fetching the invited events.`)
                    throw e;
                });
        },
    },
    mounted() {
        this.getEvents();
    },
}
</script>
