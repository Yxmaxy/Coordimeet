<template>
    <div class="bg-main-000 h-full">

        <!-- NonConfirmed and Finished -->
        <div
            v-if="pageTypeIn(EventPageType.NonConfirmed, EventPageType.Finished)"
            class="flex justify-center items-center min-h-[calc(100vh-3.5rem)]"
        >
            <event-data
                v-if="eventData"
                class="bg-main-100 px-16 py-10 rounded-lg shadow-lg"
                :event="eventData"
            >
                <template v-slot:before>
                    <div class="text-xl font-bold">
                        <template v-if="pageTypeIn(EventPageType.NonConfirmed)">
                            You've been invited to:
                        </template>
                        <template v-else>
                            This event has finished!
                        </template>
                    </div>
                </template>
                <template v-slot:after>
                    <div
                        v-if="pageTypeIn(EventPageType.NonConfirmed)"
                        class="flex justify-center gap-4 mt-4"
                    >
                        <custom-button
                            :negative="true"
                            :click="() => $router.push('/event/list')"
                        >
                            Decline
                        </custom-button>
                        <custom-button
                            :click="() => eventPageType = EventPageType.Invitee"
                        >
                            Accept
                        </custom-button>
                    </div>
                    <div
                        v-if="pageTypeIn(EventPageType.Finished)"
                        class="text-lg font-bold mt-4"
                    >
                        The selected date is: {{ eventData.SelectedDate }}
                    </div>
                </template>
            </event-data>
        </div>

        <!-- Content -->
        <tab-controller
            v-else
            :tabs="tabs"
        >
            <template v-slot:event>
                <div class="h-full bg-main-100 p-4">
                    <event-data
                        v-if="eventData"
                        :event="eventData"
                    >
                        <template v-slot:after>
                            <custom-button
                                v-if="pageTypeIn(EventPageType.Organizer)"
                                class="mt-5"
                                :small="true"
                                @click="copyLink"
                            >
                                Copy invite link to clipboard
                            </custom-button>
                        </template>
                    </event-data>
                </div>
            </template>

            <template v-slot:responses>
                <div
                    v-if="pageTypeIn(EventPageType.Invitee, EventPageType.Organizer)"
                >
                    <div v-for="participant in eventParticipants" class="list-element">
                        <div>{{ participant }}</div>
                    </div>
                </div>
            </template>

            <template v-slot:calendar>
                <calendar
                    v-if="eventData"
                    v-model:selectedDateRanges="selectedDateRanges"
                    :roughEventDateRange="roughEventDateRange"
                    :selectableDateRanges="eventData.EventDates"
                    :calendarType="eventData.CalendarType"
                />
            </template>
        </tab-controller>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useUserStore } from "@/stores/UserStore";

import { CalendarType, DateRange } from "@/types/calendar";
import { Event, EventPageType } from "@/types/event";
import { Tab } from "@/types/tabs";

import { formatDateDayMonth, formatDateDayMonthYear, formatDateDayMonthHour, getSelectedDatesOnCalendar } from "@/utils/dates";

import EventData from "@/components/EventData.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

const tabs = [
    {
        name: "Event",
        slot_name: "event",
        narrow: "sm",
    },
    {
        name: "Responses",
        slot_name: "responses",
        narrow: "sm",
    },
    {
        name: "Calendar",
        slot_name: "calendar",
    },
] as Tab[];

export default {
    components: {
        Calendar,
        TabController,
        CustomButton,
        EventData,
    },
    setup() {
        const { user } = useUserStore();

        return {
            user,
            tabs,

            EventPageType,
            CalendarType,
        }
    },
    data() {
        return {
            dates: [] as any[],
            eventData: null as null | Event,
            eventParticipants: [] as string[],
            eventPageType: EventPageType.NonConfirmed as EventPageType,

            initialIsAvailable: [] as DateRange[],
            selectableDates: [] as DateRange[],
            selectedDate: undefined as number|undefined,

            // new variables
            selectedDateRanges: [] as DateRange[],
        }
    },
    computed: {
        selectedDates(): DateRange[] {
            return getSelectedDatesOnCalendar(this.dates)
        },
        roughEventDateRange(): DateRange {
            if (this.eventData === null)
                return {} as DateRange
            return {
                from: new Date(this.eventData.EventDates.reduce(
                    (prev, min) => prev.from < min.from ? prev : min).from
                ),
                to: new Date(this.eventData.EventDates.reduce(
                    (prev, max) => prev.to > max.to ? prev : max).to
                ),
            }
        },
    },
    methods: {
        getEventData() {
            // gets the event data and sets page type
            ApiService.get("event.php", {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                // convert
                const eventData = {
                    ...res.data,
                    EventDates: res.data.EventDates.map((eventDate: any) => {
                        return {
                            from: new Date(eventDate.StartDate),
                            to: new Date(eventDate.EndDate)
                        } as DateRange
                    })
                } as Event

                // the event has finished
                if (eventData.SelectedDate !== null) {
                    this.eventPageType = EventPageType.Finished;
                // the current user is the organizer
                } else if (this.user!.GoogleID === eventData.Organizer.GoogleID) {
                    this.eventPageType = EventPageType.Organizer;
                    // TODO: re-add this
                    // this.getSelectableDates();
                }
                this.eventData = eventData;
            })
        },
        getEventParticipants() {
            ApiService.get("eventUser.php", {
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
            })
        },
        getSelectedDates() {
            ApiService.get("eventUser.php", {
                params: {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
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
            ApiService.get("eventDate.php", {
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
                ApiService.post("eventUser.php", {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
                    AvailabilityDates: this.selectedDates,
                })
                .then(res => {
                    if (res.status !== 201)
                        return
                    this.getSelectableDates();
                    alert("Your response has been submitted");
                })
            } else {  // update date that was selected before
                ApiService.put(`eventUser.php?IDEvent=${this.$route.params.id}&IDUser=${this.user!.GoogleID}`, {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
                    AvailabilityDates: this.selectedDates,
                }).then(res => {
                    if (res.status !== 201)
                        return
                    this.getSelectableDates();
                    alert("Your response has been submitted");
                })
            }
        },
        finishEvent() {
            ApiService.put(`eventDate.php?IDEvent=${this.$route.params.id}`, {
                SelectedDate: this.displayDateRange(this.selectableDates[this.selectedDate ?? 0])
            }).then(() => {
                alert("Event date successfully selected!\nYou will now be returned to the event list");
                this.$router.push("/event/list");
            })
        },
        pageTypeIn(...types: EventPageType[]): boolean {
            return types.includes(this.eventPageType);
        },
        copyLink() {
            navigator.clipboard.writeText(`${import.meta.env.VITE_FRONTEND_URL}/#/event/${this.$route.params.id}`);
        },
        displayDateRange(range: DateRange): string {
            const convertFunc = this.eventData?.CalendarType === CalendarType.Date ? formatDateDayMonthYear : formatDateDayMonthHour;
            if (convertFunc(range.from) === convertFunc(range.to))
                return convertFunc(range.from);
            return `${convertFunc(range.from)} - ${convertFunc(range.to)}`;
        },
        formatDateDayMonth,
        formatDateDayMonthYear,
    },
    mounted() {
        this.getEventData();
        // this.getEventParticipants();
        // this.getSelectedDates();
    },
}
</script>

<!-- <style lang="scss" scoped>
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
    &.basic-view {
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

        button {
            position: fixed;
            bottom: $sectionPadding + 2rem;
            margin: $sectionPadding;
            width: calc(min(20rem, 30vw) - 2 * $sectionPadding);
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

        &.basic-view {
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
</style> -->
