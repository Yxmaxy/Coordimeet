<template>
    <div :class="['event-page', {'non-confirmed': eventPageType === EventPageType.NonConfirmed}]">
        <aside
            v-if="eventPageType !== EventPageType.NonConfirmed"
            class="responses-area"
        >
            <h1>Responses</h1>
            <div>
                <div v-for="participant in eventParticipants" class="response">
                    <div>{{ participant }}</div>
                </div>
            </div>
        </aside>
        <div :class="['details-area', {'non-confirmed': eventPageType === EventPageType.NonConfirmed}]">
            <div class="container">
                <h2 v-if="eventPageType === EventPageType.NonConfirmed">
                    You've been invited to:
                </h2>
                <h1>{{ eventData.Name }}</h1>
                <div class="data">
                    <div>Organiser: {{ eventData.Organizer?.FirstName }} {{ eventData.Organizer?.LastName }}</div>
                    <div>Deadline: {{ formatDateDayMonthYear(new Date(eventData.Deadline)) }}</div>
                    <div>Duration: {{ eventData.Length }} {{ readableCalendarUnits }}</div>
                    <div v-for="key, value in eventData.Config">
                        {{ key }}
                        {{ value }}
                    </div>
                </div>
                <div
                    v-if="eventPageType === EventPageType.NonConfirmed"
                    class="accept-decline-buttons"
                >
                    <button class="negative" @click="$router.push('/event/list')">
                        Decline
                    </button>
                    <button @click="eventPageType = EventPageType.Invitee">
                        Accept
                    </button>
                </div>
            </div>

            <button
                v-if="eventPageType !== EventPageType.NonConfirmed"
                id="submit-response"
                @click="onSubmitEvent"
            >
                Submit response
            </button>
        </div>
        <main
            v-if="eventPageType !== EventPageType.NonConfirmed"
            class="calendar-area"
        >
            <calendar
                :type="eventData.CalendarType"
                :dateRanges="eventData.EventDates"
                :days="selectedDates"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { CalendarType, ICalendarDate, IEvent, EventPageType } from '../common/interfaces';
import { apiServer } from '../common/globals';
import { formatDateDayMonthYear } from '../common/helpers';
import axios from "axios";

export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            selectedDates: [] as ICalendarDate[],
            eventData: {} as IEvent,
            eventParticipants: [] as string[],
            eventPageType: EventPageType.NonConfirmed as EventPageType,
            EventPageType,
        }
    },
    computed: {
        readableCalendarUnits(): string {
            if (this.eventData.CalendarType === CalendarType.Date)
                return "days";
            return "hours";
        }
    },
    methods: {
        getEventData() {
            axios.get(`${apiServer}/event.php?`, {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    this.$router.push("/");
                    return;
                }
                this.eventData = {
                    ...res.data,
                    EventDates: res.data.EventDates.map((eventDate: any) => {
                        return {
                            from: new Date(eventDate.StartDate),
                            to: new Date(eventDate.EndDate)
                        }
                    })
                } as IEvent
            });
        },
        getEventParticipants() {
            axios.get(`${apiServer}/eventUser.php`, {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                if (res.data.error) {
                   console.log(res.data.error);
                    return;
                }
                if (res.data.length === 0)
                    return;
                this.eventParticipants = res.data.map((participant: any) => {
                    return `${participant.FirstName} ${participant.LastName}`;
                })
            });
        },
        onSubmitEvent() {
            const dates: any = [];
            let currentStart: Date|undefined = undefined;
            for (let i = 0; i < this.selectedDates.length; i++) {
                const date = this.selectedDates[i];
                if (currentStart === undefined && date.isAvailable)  // set currentStart
                    currentStart = date.date;
                else if (currentStart !== undefined && !date.isAvailable) {  // add prevDate to dates
                    const prevDate = this.selectedDates[i - 1];
                    dates.push({
                        StartDate: new Date(currentStart),
                        EndDate: new Date(prevDate.date),
                    })
                    currentStart = undefined;
                }
            }
            console.log(dates);
        },
        formatDateDayMonthYear,
    },
    mounted() {
        this.getEventData();
        this.getEventParticipants();
    },
}
</script>

<style lang="scss" scoped>
@import "../styles/colors.scss";

.event-page {
    $sectionPadding: 1rem;

    flex: 1;
    display: grid;
    grid-template-rows: min(15rem, 30vh) 1fr;
    grid-template-columns: min(20rem, 30vw) 1fr;
    grid-template-areas:
        "responses details"
        "responses calendar";
    &.non-confirmed {
        grid-template-rows: 1fr;
        grid-template-columns: 1fr;
        grid-template-areas:
            "details";
    }
    .responses-area {
        grid-area: responses;
        background-color: $color-background-3;
        overflow: auto;

        h1 {
            background-color: $color-background-3;
            padding: $sectionPadding;
            position: sticky;
            top: 0;
        }
        .response {
            display: flex;
            justify-content: space-between;
            padding: $sectionPadding;
        }
    }
    .calendar-area {
        grid-area: calendar;
        background-color: $color-background;
        display: flex;
        flex-direction: column;
        padding: $sectionPadding;
        overflow: auto;
    }
    .details-area {
        grid-area: details;
        background-color: $color-background-3;
        padding: $sectionPadding;
        position: relative;

        #submit-response {
            position: absolute;
            right: 0.5rem;
            bottom: 0.5rem;
        }

        &.non-confirmed {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: $color-background;
            h1, h2 {
                text-align: center;
            }
            .container {
                max-width: 25rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 2rem;
                background-color: $color-background;
                border: {
                    radius: 20px;
                    color: $color-main;
                    style: solid;
                    width: 2px;
                }
                .data {
                    margin: {
                        top: 1rem;
                        bottom: 1.5rem;
                    };
                    max-width: 20rem;
                    width: 100%;
                }
            }
            .accept-decline-buttons {
                display: flex;
                justify-content: center;
                gap: 1rem;
            }
        }
    }
}
</style>
