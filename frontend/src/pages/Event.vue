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
                            The event date has been selected!
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
            :breakpoint="1050"
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
                                Copy invite link to clipboard <custom-icon class="text-base" icon="person_add" />
                            </custom-button>
                        </template>
                    </event-data>
                </div>
            </template>

            <template v-slot:responses>
                <div
                    v-for="participant in eventParticipants"
                    :class="[{
                        'text-main-200': !participant.isSelected,
                        'cursor-pointer hover:bg-main-100': isOrganiserMode,
                    }, 'p-4 font-bold border-b-2 border-b-main-200 transition-colors']"
                    @click="toggleParticipant(participant)"
                >
                    {{ participant.FirstName }} {{ participant.LastName }}
                </div>
            </template>

            <template v-slot:calendar>
                <div class="bg-main-100 shadow-md p-3 mb-3 flex justify-between items-center">
                    <!-- Organiser mode toggle -->
                    <div>
                        <custom-toggle
                            v-if="pageTypeIn(EventPageType.Organizer)"
                            v-model="isOrganiserMode"
                        >
                            <template v-slot:left>
                                <span class="flex items-center gap-1 font-bold mr-1">
                                    Invitee <custom-icon class="text-base" icon="person" />
                                </span>
                            </template>
                            <template v-slot:right>
                                <span class="flex items-center gap-1 font-bold ml-1">
                                    Organiser <custom-icon class="text-base" icon="engineering" />
                                </span>
                            </template>
                        </custom-toggle>
                    </div>

                    <!-- Submit buttons -->
                    <custom-button
                        v-if="pageTypeIn(EventPageType.Organizer) && isOrganiserMode"
                        :small="true"
                        :disabled="!isSelectedDateRangesSet || selectedDateRanges.length !== 1"
                        :click="finishEvent"
                    >
                        Submit and finish <custom-icon class="text-base" icon="event_available" />
                    </custom-button>
                    <custom-button
                        v-else
                        :small="true"
                        :click="submitSelection"
                        :disabled="!isSelectedDateRangesSet || gettingParticipantData"
                    >
                        Submit <custom-icon class="text-base" icon="event" />
                    </custom-button>
                </div>
                <!-- Calendar -->
                <calendar
                    v-if="eventData"
                    v-model:selectedDateRanges="selectedDateRanges"
                    :roughEventDateRange="roughEventDateRange"
                    :selectableDateRanges="eventData.EventDates"
                    :heatmapDateRanges="selectedEventParticipantDateRanges"
                    :calendarType="eventData.CalendarType"
                    :enableOptions="!isOrganiserMode"
                />
            </template>
        </tab-controller>
    </div>
</template>

<script lang="ts">
import { AxiosResponse } from "axios";

import ApiService from "@/utils/ApiService";
import { useStoreUser } from "@/stores/storeUser";

import { CalendarType, DateRange } from "@/types/calendar";
import { Event, EventPageType, EventParticipant } from "@/types/event";
import { Tab } from "@/types/tabs";

import {
    formatDateDayMonth,
    formatDateDayMonthYear,
    formatDateDayMonthHour,
    convertDateRangesFromBackend,
    convertDateRangesForBackend } from "@/utils/dates";

import EventData from "@/components/EventData.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

const tabs = [
    {
        name: "Event",
        slot_name: "event",
        narrow: "sm",
        icon: "description",
    },
    {
        name: "Responses",
        slot_name: "responses",
        narrow: "sm",
        icon: "group",
    },
    {
        name: "Calendar",
        slot_name: "calendar",
        icon: "calendar_today",
    },
] as Tab[];

export default {
    components: {
        Calendar,
        TabController,
        EventData,
        CustomButton,
        CustomToggle,
        CustomIcon,
    },
    setup() {
        const { user } = useStoreUser();

        return {
            user,
            tabs,

            EventPageType,
            CalendarType,
        }
    },
    data() {
        return {
            eventData: null as null | Event,
            eventPageType: EventPageType.NonConfirmed as EventPageType,
            eventParticipants: [] as EventParticipant[],

            selectedDateRanges: [] as DateRange[],  // the current calendar selection
            previousSelectedDateRanges: [] as DateRange[],  // set if the invitee submitted before

            isOrganiserMode: false,  // organiser mode toggle
            gettingParticipantData: false,  // for fetching event participants
        }
    },
    computed: {
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
        isSelectedDateRangesSet(): boolean {
            return this.selectedDateRanges.length !== 0
        },
        isPreviousSelectedDateRangesSet(): boolean {
            return this.previousSelectedDateRanges.length !== 0
        },
        selectedEventParticipantDateRanges(): DateRange[] {
            if (!this.isOrganiserMode)
                return [];
            const participantDates = this.eventParticipants
                .filter(participant => participant.isSelected)
                .map(participant => participant.Dates)
            const dateRanges = [] as DateRange[]
            return dateRanges.concat(...participantDates)
        }
    },
    methods: {
        // imported
        formatDateDayMonth,
        formatDateDayMonthYear,

        // event
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
                }
                this.eventData = eventData;
            })
        },
        getPreviousSelectedDateRanges() {
            // gets the user's selected date ranges if they exist
            // also "upgrades" the user to invitee if needed
            ApiService.get("eventUser.php", {
                params: {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`An error occured while fetching your previous selection: ${res.data.error}`)
                    return;
                }
                // empty response
                if (res.data.length === 0)
                    return;
                
                if (res.data.Dates.length !== 0) {
                    // "upgrade" user to invitee if the data was submitted
                    if (this.eventPageType === EventPageType.NonConfirmed)
                        this.eventPageType = EventPageType.Invitee;

                    // update selectedDateRanges with previous response
                    this.previousSelectedDateRanges = convertDateRangesFromBackend(res.data.Dates);

                    // intialize the selected date ranges
                    this.selectedDateRanges = this.previousSelectedDateRanges;
                }
            });
        },
        getParticipants() {
            this.gettingParticipantData = true;
            ApiService.get("eventUser.php", {
                params: {
                    IDEvent: this.$route.params.id,
                }
            }).then(res => {
                if (res.data.error) {
                    alert(`An error occured while fetching the participants: ${res.data.error}`)
                    return;
                }
                if (res.data.length === 0)
                    return;

                // set the participants array
                this.eventParticipants = res.data.map((participant: any) => {
                    return {
                        ...participant,
                        Dates: convertDateRangesFromBackend(participant.Dates),
                        isSelected: true,
                    } as EventParticipant
                })
            }).finally(() => {
                this.gettingParticipantData = false;
            })
        },

        // submit event
        submitSelection() {
            // submit as an invitee
            if (!this.isSelectedDateRangesSet)
                return;

            // handler if the event succeedes
            const handleResponse = (response: AxiosResponse) => {
                if (response.status !== 201)
                    return;
                this.previousSelectedDateRanges = this.selectedDateRanges;
                alert("Your response has been submitted");
            }

            if (!this.isPreviousSelectedDateRangesSet) {
                ApiService.post("eventUser.php", {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
                    AvailabilityDates: convertDateRangesForBackend(this.selectedDateRanges),
                }).then(handleResponse)
            } else {  // update date that was selected before
                ApiService.put(`eventUser.php?IDEvent=${this.$route.params.id}&IDUser=${this.user!.GoogleID}`, {
                    IDEvent: this.$route.params.id,
                    IDUser: this.user!.GoogleID,
                    AvailabilityDates: convertDateRangesForBackend(this.selectedDateRanges),
                }).then(handleResponse)
            }
        },
        finishEvent() {
            // finish the event as the organiser
            if (!this.isSelectedDateRangesSet || this.selectedDateRanges.length !== 1)
                return;
            
            const selectedDateRange = this.selectedDateRanges[0];  // get the selected date range
            ApiService.put(`eventDate.php?IDEvent=${this.$route.params.id}`, {
                SelectedDate: this.displayDateRange(selectedDateRange)
            }).then(() => {
                alert("Event date successfully selected!\nYou will now be returned to the event list");
                this.$router.push("/event/list");
            })
        },

        // interaction
        toggleParticipant(participant: EventParticipant) {
            if (!this.isOrganiserMode)
                return;
            participant.isSelected = !participant.isSelected;
        },

        // helpers
        pageTypeIn(...types: EventPageType[]): boolean {
            return types.includes(this.eventPageType);
        },
        copyLink() {
            navigator.clipboard.writeText(`${import.meta.env.VITE_FRONTEND_URL}/#/event/${this.$route.params.id}`);
        },
        displayDateRange(range: DateRange): string {
            // converts date range to a readable format
            const convertFunc = this.eventData?.CalendarType === CalendarType.Date ?
                formatDateDayMonthYear : formatDateDayMonthHour;
            if (convertFunc(range.from) === convertFunc(range.to))
                return convertFunc(range.from);
            return `${convertFunc(range.from)} - ${convertFunc(range.to)}`;
        },
    },
    mounted() {
        this.getEventData();
        this.getPreviousSelectedDateRanges();
        this.getParticipants();
    },
    watch: {
        isOrganiserMode(isOrganiser: boolean) {
            if (isOrganiser) {
                // get participant data
                this.getParticipants();
                this.selectedDateRanges = [];
            } else {
                // initialize invitee selection to previous selection
                this.selectedDateRanges = this.previousSelectedDateRanges;
                this.eventParticipants.map(participant => participant.isSelected = true);
            }
        },
    }
}
</script>
