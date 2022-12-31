<template>
    <div v-if="Object.keys(eventData).length !== 0" :class="['event-page', {
        'non-confirmed': pageTypeIn(EventPageType.NonConfirmed, EventPageType.Finished),
        'organizer': eventPageType === EventPageType.Organizer,
    }]">
        <aside
            v-if="pageTypeIn(EventPageType.Invitee, EventPageType.Organizer)"
            class="responses-area"
        >
            <h1>Responses</h1>
            <div>
                <div v-for="participant in eventParticipants" class="list-element">
                    <div>{{ participant }}</div>
                </div>
            </div>
        </aside>
        <aside v-if="eventPageType === EventPageType.Organizer" class="selectable-area">
            <h1>Selectable dates</h1>
            <div>
                <div
                    v-for="(selectableDate, index) in selectableDates"
                    :class="['list-element', {'selected': index === selectedDate}]"
                    @click="selectedDate = index"
                >
                    {{ displayDateRange(selectableDate) }}
                </div>
            </div>
            <button
                :class="{'disabled': selectedDate === undefined}"
                @click="finishEvent"
            >
                Select date and finish event
            </button>
        </aside>
        <div :class="['details-area', {'non-confirmed': pageTypeIn(EventPageType.NonConfirmed, EventPageType.Finished)}]">
            <div class="container">
                <h2 v-if="eventPageType === EventPageType.NonConfirmed">
                    You've been invited to:
                </h2>
                <h1 class="space-between">
                    {{ eventData.Name }}
                    <button
                        v-if="eventPageType === EventPageType.Organizer"    
                        id="copy-link"
                        @click="copyLink"
                    >
                        Copy invite link to clipboard
                    </button>
                </h1>
                <div class="data">
                    <div>Organizer: {{ eventData.Organizer?.FirstName }} {{ eventData.Organizer?.LastName }}</div>
                    <div>Deadline: {{ formatDateDayMonthYear(new Date(eventData.Deadline)) }}</div>
                    <div>Duration: {{ eventData.Length }} {{ readableCalendarUnits }}</div>
                    <div v-for="value, key in eventData.Config">
                        {{ key }}:
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
                v-if="pageTypeIn(EventPageType.Invitee, EventPageType.Organizer)"
                id="submit-response"
                @click="onSubmitEvent"
                :class="{'disabled': selectedDates.length === 0}"
            >
                Submit response
            </button>
        </div>
        <main
            v-if="pageTypeIn(EventPageType.Invitee, EventPageType.Organizer)"
            class="calendar-area"
        >
            <calendar
                :type="eventData.CalendarType"
                :dateRanges="eventData.EventDates"
                :days="dates"
                :initialIsAvailable="initialIsAvailable"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { useUserStore } from '../common/stores/UserStore';
import { CalendarType, ICalendarDate, IEvent, EventPageType, IDateRange } from '../common/interfaces';
import { apiServer } from '../common/globals';
import { formatDateDayMonth, formatDateDayMonthYear, formatDateDayMonthHour, getSelectedDatesOnCalendar } from '../common/helpers';
import axios from "axios";

export default {
    components: {
        "calendar": Calendar,
    },
    setup() {
        const { user } = useUserStore();
        return {
            user,
        }
    },
    data() {
        return {
            dates: [] as ICalendarDate[],
            eventData: {} as IEvent,
            eventParticipants: [] as string[],
            eventPageType: EventPageType.NonConfirmed as EventPageType,
            initialIsAvailable: [] as IDateRange[],
            selectableDates: [] as IDateRange[],
            selectedDate: undefined as number|undefined,
            EventPageType,
            CalendarType,
        }
    },
    computed: {
        readableCalendarUnits(): string {
            if (this.eventData.CalendarType === CalendarType.Date)
                return "days";
            return "hours";
        },
        selectedDates(): IDateRange[] {
            return getSelectedDatesOnCalendar(this.dates)
        },
    },
    methods: {
        getEventData() {
            axios.get(`${apiServer}/event.php`, {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    this.$router.push("/");
                    return;
                }
                const eventData = {
                    ...res.data,
                    EventDates: res.data.EventDates.map((eventDate: any) => {
                        return {
                            from: new Date(eventDate.StartDate),
                            to: new Date(eventDate.EndDate)
                        }
                    })
                } as IEvent

                this.eventData = eventData;
                if (res.data.SelectedDate !== null) {
                    this.eventPageType = EventPageType.Finished;
                } else if (this.user.GoogleID === eventData.Organizer.GoogleID) {
                    this.eventPageType = EventPageType.Organizer;
                    this.getSelectableDates();
                }
            }).catch(() => this.$router.push("/"))
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
            }).catch(() => this.$router.push("/"))
        },
        getSelectedDates() {
            axios.get(`${apiServer}/eventUser.php`, {
                params: {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user.GoogleID,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    return;
                }
                if (res.data.length === 0)
                    return;
                if (res.data.Dates.length !== 0 && this.eventPageType === EventPageType.NonConfirmed)
                    this.eventPageType = EventPageType.Invitee;
                this.initialIsAvailable = res.data.Dates === undefined ? [] : res.data.Dates.map((range: any) => {
                    return {
                        from: new Date(range.StartDate),
                        to: new Date(range.EndDate),
                    }
                });
            });
        },
        getSelectableDates() {
            if (this.eventPageType !== EventPageType.Organizer)
                return;
            axios.get(`${apiServer}/eventDate.php`, {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`Pri pridobivanju podatkov je prišlo do napake: ${res.data.error}`)
                    return;
                }
                this.selectableDates = res.data === undefined ? [] : res.data.map((range: any) => {
                    return {
                        from: new Date(range.StartDate),
                        to: new Date(range.EndDate),
                    }
                });
            });
        },
        onSubmitEvent() {
            this.selectedDate = undefined;
            if (this.selectedDates.length === 0)
                return;
            if (this.initialIsAvailable.length === 0) {  // a date didn't exist before
                axios.post(`${apiServer}/eventUser.php`, {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user.GoogleID,
                    AvailabilityDates: this.selectedDates,
                })
                .then(res => {
                    if (res.status !== 201)
                        return
                    this.getSelectableDates();
                })
            } else {  // update date that was selected before
                axios.put(`${apiServer}/eventUser.php?IDEvent=${this.$route.params.id}&IDUser=${this.user.GoogleID}`, {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user.GoogleID,
                    AvailabilityDates: this.selectedDates,
                }).then(res => {
                    if (res.status !== 201)
                        return
                    this.getSelectableDates();
                })
            }
        },
        finishEvent() {
            axios.put(`${apiServer}/eventDate.php?IDEvent=${this.$route.params.id}`, {
                SelectedDate: this.displayDateRange(this.selectableDates[this.selectedDate ?? 0])
            }).then(res => {
                console.log(res.data)
            })
        },
        pageTypeIn(...types: EventPageType[]): boolean {
            for (const type of types)
                if (this.eventPageType === type)
                    return true;
            return false;
        },
        copyLink() {
            navigator.clipboard.writeText(`https://coordimeet.eu/#/event/${this.$route.params.id}`);
        },
        displayDateRange(range: IDateRange): string {
            const convertFunc = this.eventData.CalendarType === CalendarType.Date ? formatDateDayMonthYear : formatDateDayMonthHour;
            if (convertFunc(range.from) === convertFunc(range.to))
                return convertFunc(range.from);
            return `${convertFunc(range.from)} - ${convertFunc(range.to)}`;
        },
        formatDateDayMonth,
        formatDateDayMonthYear,
    },
    watch: {
        eventPageType(n) {
            console.log(n)
        }
    },
    mounted() {
        this.getEventData();
        this.getEventParticipants();
        this.getSelectedDates();
    },
}
</script>

<style lang="scss" scoped>
@import "../styles/colors.scss";

$sectionPadding: 1rem;

@mixin aside-mixin {
    background-color: $color-background-3;
    overflow: auto;
    border-right: 2px solid $color-top-bottom;

    h1 {
        background-color: $color-background-3;
        padding: $sectionPadding;
        position: sticky;
        top: 0;
    }
    .list-element {
        display: flex;
        justify-content: space-between;
        padding: {
            left: $sectionPadding;
            right: $sectionPadding;
            top: calc($sectionPadding / 2);
            bottom: calc($sectionPadding / 2);
        };
    }
}

.event-page {
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
    &.organizer {
        grid-template-columns: min(20rem, 30vw) min(20rem, 30vw) 1fr;
        grid-template-areas:
            "responses selectable details"
            "responses selectable calendar";
    }
    .responses-area {
        grid-area: responses;
        @include aside-mixin;
    }
    .selectable-area {
        grid-area: selectable;
        @include aside-mixin;
        position: relative;

        button {
            position: sticky;
            bottom: $sectionPadding;
            margin: $sectionPadding;
            width: calc(100% - 2 * $sectionPadding);
        }

        .list-element {
            transition: 200ms;
            user-select: none;
            cursor: pointer;
            &:hover {
                background-color: $color-background-2;
            }
            &.selected {
                color: $color-background;
                background-color: $color-main;
            }
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
        overflow: auto;

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
