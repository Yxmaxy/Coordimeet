<template>
    <div class="event-page">
        <aside class="responses-area">
            <h1>Responses</h1>
            <div>
                <div v-for="participant in eventParticipants" class="response">
                    <div>{{ participant }}</div>
                </div>
            </div>
        </aside>
        <div class="details-area">
            <h1>{{ eventData.Name }}</h1>
            <div>Deadline: 3. 12. 2022</div>
            <div>From 11. 12. 2022 to 19. 12. 2022</div>
            <div>Duration: {{ eventData.Length }} {{ readableCalendarUnits }}</div>

            <button
                id="submit-response"
                @click="onSubmitEvent"
            >
                Submit response
            </button>
        </div>
        <main class="calendar-area">
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
import { CalendarType, ICalendarDate, IEvent } from '../common/interfaces';
import { apiServer } from '../common/globals';
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
            axios.post(`${apiServer}/event.php`, {
                IDEvent: 1,
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
                            from: new Date(
                                eventDate.StartDate.Year,
                                eventDate.StartDate.Month - 1,
                                eventDate.StartDate.Day,
                                eventDate.StartDate.Hour,
                                eventDate.StartDate.Minute,
                            ),
                            to: new Date(
                                eventDate.EndDate.Year,
                                eventDate.EndDate.Month - 1,
                                eventDate.EndDate.Day,
                                eventDate.EndDate.Hour,
                                eventDate.EndDate.Minute,
                            )   
                        }
                    })
                } as IEvent
            });
        },
        getEventParticipants() {
            axios.post(`${apiServer}/usersOnEvent.php`, {
                IDEvent: 1,
            }).then(res => {
                if (res.data.error) {
                   console.log(res.data.error);
                    return;
                }
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
        }
    },
    mounted() {
        this.getEventData();
        this.getEventParticipants();
    },
}
</script>

<style lang="scss" scoped>
.event-page {
    $sectionPadding: 0.5rem;

    flex: 1;
    display: grid;
    grid-template-rows: min(15rem, 30vh) 1fr;
    grid-template-columns: min(20rem, 30vw) 1fr;
    grid-template-areas:
        "responses details"
        "responses calendar";

    .responses-area {
        grid-area: responses;
        background-color: lightcoral;
        overflow: auto;

        h1 {
            background-color: lightcoral;
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
        background-color: lightcyan;
        display: flex;
        flex-direction: column;
        padding: $sectionPadding;
        overflow: auto;
    }
    .details-area {
        grid-area: details;
        background-color: lightsalmon;
        padding: $sectionPadding;
        position: relative;

        #submit-response {
            position: absolute;
            right: 0;
            bottom: 0;
        }
    }
}
</style>
