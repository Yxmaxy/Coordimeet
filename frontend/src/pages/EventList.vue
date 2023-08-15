<template>
    <div class="relative">
        <TabController v-model:activeTab="activeTab">
            <template v-slot:events_invited>
                <event-list-component :events="eventsInvited" />
            </template>
            <template v-slot:events_created>
                <event-list-component :events="eventsCreated" :userIsOrganiser="true" />
            </template>
        </TabController>
        <button
            class="btn right-4 bottom-4 absolute !p-3 !rounded-2xl"
            @click="$router.push('/event/new')"
        >
            <span class="text-xl text-white">+</span>
            New event
        </button>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useUserStore } from "@/stores/UserStore";

import { Event } from "@/types/event";

import EventListComponent from "@/components/EventListComponent.vue";
import TabController from "@/components/TabController.vue";

export default {
    name: "EventList",
    components: {
        EventListComponent,
        TabController,
    },
    setup() {
        const { user } = useUserStore();
        return {
            user,
        }
    },
    data() {
        return {
            eventsInvited: [] as Event[],
            eventsCreated: [] as Event[],
            activeTab: 0 as number,
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
