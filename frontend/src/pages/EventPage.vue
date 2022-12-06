<template>
    <div class="event-page">
        <aside class="responses-area">
            <h1>Responses</h1>
            <div>
                <div v-for="index in 50" class="response">
                    <div>Name</div>
                    <div>Responded</div>
                </div>
            </div>
        </aside>
        <div class="details-area">
            <h1>{{ eventData.Name }}</h1>
            <div>Deadline: 3. 12. 2022</div>
            <div>From 11. 12. 2022 to 19. 12. 2022</div>
            <div>Duration: {{ eventData.Length }}</div>
        </div>
        <main class="calendar-area">
            <calendar
                :type="1"
                :dateRanges="eventData.EventDates"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { CalendarType, IEvent } from '../common/interfaces';
import { apiServer } from '../common/globals';
import axios from "axios";

export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            calendarType: CalendarType.Date,
            eventData: {} as IEvent,
        }
    },
    mounted() {
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
        .controls {
            position: sticky;
            top: 0;
        }
    }
    .details-area {
        grid-area: details;
        background-color: lightsalmon;
        padding: $sectionPadding;
    }
}
</style>
