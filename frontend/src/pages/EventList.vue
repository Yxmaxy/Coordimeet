<template>
    <div class="event-list-page">
        <div>
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
        </div>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useUserStore } from "@/stores/UserStore";

import { Event } from "@/types/event";

import EventListComponent from "../components/EventListComponent.vue";

export default {
    components: {
        "list-component": EventListComponent,
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
                    IDUser: this.user.GoogleID,
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

<style lang="scss" scoped>
@import "../styles/colors.scss";

.event-list-page {
    $sectionPadding: 1rem;

    display: grid;
    grid-template-columns: 1fr 1fr;

    & > div {
        overflow: auto;

        &:first-child {
            border-right: 2px solid $color-top-bottom;
        }

        h1 {
            position: sticky;
            top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;

            background-color: $color-background-3;
            padding: $sectionPadding;
        }
    }
}
</style>
