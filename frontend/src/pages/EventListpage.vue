<template>
    <div class="event-list-page">
        <div>
            <h1>Events I'm invited to</h1>
            <div>
                <div class="event" v-for="event in eventsInvited">
                    <div><b>{{ event.Name }}</b></div>
                    <div>
                        <div>{{ formatDateDayMonthYear(new Date(event.Deadline)) }}</div>
                        <div>{{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}</div>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <h1>
                <div>Events I've created</div>
                <button @click="$router.push('/event/new')">New event</button>
            </h1>
        <div>
            <div class="event" v-for="event in eventsCreated">
                <div><b>{{ event.Name }}</b></div>
                    <div>
                        <div>{{ formatDateDayMonthYear(new Date(event.Deadline)) }}</div>
                        <div>{{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import axios from "axios";
import { IEvent } from "../common/interfaces";
import { formatDateDayMonthYear } from '../common/helpers';
import { apiServer } from "../common/globals";

export default {
    data() {
        return {
            eventsInvited: [] as IEvent[],
            eventsCreated: [] as IEvent[],
        }
    },
    methods: {
        getEventsInvited() {
            axios.get(`${apiServer}/eventUser.php`, {
                params: {
                    IDUser: 1234, // TODO: Change static user id to GoogleID of logged in user (returned in googleLogin.php call)
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    this.$router.push("/");
                    return;
                }
                this.eventsInvited = res.data;
            });
        },
        getEventsCreated() {
            axios.get(`${apiServer}/eventUser.php`, {
                params: {
                    IDOrganizer: 1234, // TODO: Change static organizer id to GoogleID of logged in user (returned in googleLogin.php call)
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    this.$router.push("/");
                    return;
                }
                this.eventsCreated = res.data;
            });
        },
        formatDateDayMonthYear,
    },
    mounted() {
        this.getEventsInvited();
        this.getEventsCreated();
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

        .event {
            background-color: $color-background-3;
            margin: 0.75rem;
            padding: 1.25rem;
            border-radius: 20px;
            display: flex;
            justify-content: space-between;
            cursor: pointer;
            transition: 200ms;

            &:hover {
                background-color: $color-top-bottom;
                transform: translateY(-0.1rem);
            }

            & > div {
                display: flex;
                gap: 0.75rem;
            }
        }
    }
}
</style>
