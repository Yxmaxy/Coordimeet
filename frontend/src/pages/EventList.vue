<template>
    <div>
        <TabController :tabs="[
            {
                name: 'Events I\'m invited to',
                events: eventsCreated,
                userIsOrganiser: false,
            },
            {
                name: 'Events I\'ve created',
                events: eventsCreated,
                userIsOrganiser: true,
            },
            {
                name: 'Something else',
                events: eventsCreated,
                userIsOrganiser: true,
            }
        ]">
            <template v-slot:tab="{ tab }">
                <event-list-component :events="tab?.events" :userIsOrganiser="tab?.userIsOrganiser" />
            </template>
        </TabController>
        <!-- <div>
            <h1>Events I'm invited to</h1>
            <div>
                <list-component :events="eventsInvited" />
            </div>
        </div>
        <div>
            <h1>
                <div>Events I've created</div>
                <button @click="$router.push('/event/new')">New event</button>
            </h1>
            <div>
                <list-component :events="eventsCreated" :userIsOrganiser="true" />
            </div>
        </div> -->
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
