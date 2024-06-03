<template>
    <div class="bg-main-000 h-full">
        <!-- NotLoggedIn -->
        <div
            v-if="pageTypeIn(EventPageType.NotLoggedIn) && eventData"
            class="flex justify-center items-center min-h-[calc(100vh-3.5rem)]"
        >
            <div class="bg-main-100 px-16 py-10 rounded-lg shadow-lg">
                <div class="text-xl font-bold">You've been invited to:</div>
                <div class="text-2xl font-bold">{{ eventData.title }}</div>
                <div class="mt-3">
                    It seems like you are not logged in. You can choose to:
                    <ul>
                        <li class="ml-5 list-disc">Decline the invitation</li>
                        <li class="ml-5 list-disc">Log in or Sign up</li>
                        <li class="ml-5 list-disc">
                            <div class="flex items-center gap-1.5">
                                Submit anonymously
                                <help-icon>
                                    If you choose to submit an anonymous response, a temporary account will be created for you.
                                    <br />
                                    If you try to access the same event from another browser, you will not be able to see your previous response.
                                </help-icon>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="flex justify-center gap-4 mt-4">
                    <custom-button @click="$router.push('/')">Decline</custom-button>
                    <custom-button @click="onLoginOrSignup">Log in or Sign up</custom-button>
                    <custom-button @click="onSubmitAnon">Submit anonymously</custom-button>
                </div>
            </div>
        </div>

        <!-- NonConfirmed and Finished -->
        <div
            v-else-if="pageTypeIn(EventPageType.NonConfirmed, EventPageType.Finished)"
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
                        The selected date is: {{ eventData.selected_start_date }}
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
                                v-if="pageTypeIn(EventPageType.Organiser)"
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
                            v-if="pageTypeIn(EventPageType.Organiser)"
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
                        v-if="pageTypeIn(EventPageType.Organiser) && isOrganiserMode"
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
                        :disabled="gettingParticipantData"
                    >
                        <template v-if="!isSelectedDateRangesSet">
                            Submit as unavailable
                        </template>
                        <template v-else>
                            Submit
                        </template>
                        <custom-icon class="text-base" icon="event" />
                    </custom-button>
                </div>
                <!-- Calendar -->
                <calendar
                    v-if="eventData"
                    v-model:selectedDateRanges="selectedDateRanges"
                    :roughEventDateRange="roughEventDateRange"
                    :selectableDateRanges="eventData.event_availability_options"
                    :heatmapDateRanges="selectedEventParticipantDateRanges"
                    :calendarType="eventData.event_calendar_type"
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
import { useStoreMessages } from "@/stores/storeMessages";

import { CalendarType, DateRange } from "@/types/calendar";
import { Event, EventPageType, EventParticipant } from "@/types/event";
import { Tab } from "@/types/tabs";

import { formatDateDayMonthYear, formatDateDayMonthHour } from "@/utils/dates";

import EventData from "@/components/EventData.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

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
        HelpIcon,
    },
    setup() {
        const storeUser = useStoreUser();
        const storeMessages = useStoreMessages();

        return {
            storeUser,
            tabs,

            storeMessages,

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
                start_date: new Date(this.eventData.event_availability_options.reduce(
                    (prev, min) => prev.start_date < min.start_date ? prev : min).start_date
                ),
                end_date: new Date(this.eventData.event_availability_options.reduce(
                    (prev, max) => prev.end_date > max.end_date ? prev : max).end_date
                ),
            }
        },
        isSelectedDateRangesSet(): boolean {
            return this.selectedDateRanges.length !== 0
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
        // event
        getEventData() {
            // gets the event data and sets page type
            ApiService.get(`events/event/${this.$route.params.uuid}/`)
            .then(res => {
                // parse all dates
                const parseDate = (date: string) => new Date(date);
                const parseDateNull = (date: string) => date ? parseDate(date) : null;
                
                const eventData = {
                    ...res.data,
                    deadline: parseDate(res.data.deadline),
                    selected_start_date: parseDateNull(res.data.selected_start_date),
                    selected_end_date: parseDateNull(res.data.selected_end_date),
                    event_availability_options: res.data.event_availability_options.map(
                        (dateRange: any) => ({
                            start_date: parseDate(dateRange.start_date),
                            end_date: parseDate(dateRange.end_date),
                        })
                    ),
                } as Event;

                // the event has finished
                if (eventData.selected_start_date !== null) {
                    this.eventPageType = EventPageType.Finished;
                // the current user is the organiser
                } else if (this.storeUser.user?.id === eventData.organiser?.id) {
                    this.eventPageType = EventPageType.Organiser;
                }
                this.eventData = eventData;
            })
        },
        getPreviousSelectedDateRanges() {
            // gets the user's selected date ranges if they exist
            // also "upgrades" the user to invitee if needed
            ApiService.get(`/events/event/participants/${this.$route.params.uuid}/`)
                .then((response: AxiosResponse) => {
                    if (response.data.error) {
                        this.storeMessages.showMessageError(`An error occured while fetching your previous selection: ${response.data.error}`)
                        return;
                    }
                    // empty response
                    if (response.data.length === 0)
                        return;
                    
                    if (response.data.selected_ranges.length !== 0) {
                        // "upgrade" user to invitee if the data was submitted
                        if (this.eventPageType === EventPageType.NonConfirmed)
                            this.eventPageType = EventPageType.Invitee;

                        // update selectedDateRanges with previous response
                        this.previousSelectedDateRanges = response.data.selected_ranges.map((range: DateRange) => ({
                            start_date: new Date(range.start_date),
                            end_date: new Date(range.end_date),
                        }));

                        // intialize the selected date ranges
                        this.selectedDateRanges = this.previousSelectedDateRanges;
                    }
                });
        },
        // getParticipants() {
        //     this.gettingParticipantData = true;
        //     ApiService.get("eventUser.php", {
        //         params: {
        //             IDEvent: this.$route.params.uuid,
        //         }
        //     }).then(res => {
        //         if (res.data.error) {
        //             this.storeMessages.showMessageError(`An error occured while fetching the participants: ${res.data.error}`)
        //             return;
        //         }
        //         if (res.data.length === 0)
        //             return;

        //         // set the participants array
        //         this.eventParticipants = res.data.map((participant: any) => {
        //             return {
        //                 ...participant,
        //                 Dates: convertDateRangesFromBackend(participant.Dates),
        //                 isSelected: true,
        //             } as EventParticipant
        //         })
        //     }).finally(() => {
        //         this.gettingParticipantData = false;
        //     })
        // },

        // submit event
        submitSelection() {
            // submit as an invitee
            const data = !this.isSelectedDateRangesSet ? {not_comming: true} : {
                selected_ranges: this.selectedDateRanges.map(range => ({
                    start_date: range.start_date.toISOString(),
                    end_date: range.end_date.toISOString(),
                }))
            }

            // handler if the event succeedes
            ApiService.post(`/events/event/participants/${this.$route.params.uuid}/`, data)
                .then((response: AxiosResponse) => {
                    if (response.status !== 200)
                        return;
                    this.previousSelectedDateRanges = this.selectedDateRanges;
                    this.storeMessages.showMessage("Your response has been submitted");
                })
            
        },
        finishEvent() {
            // finish the event as the organiser
            if (!this.isSelectedDateRangesSet || this.selectedDateRanges.length !== 1)
                return;
            
            const selectedDateRange = this.selectedDateRanges[0];  // get the selected date range
            ApiService.put(`eventDate.php?IDEvent=${this.$route.params.uuid}`, {
                SelectedDate: this.displayDateRange(selectedDateRange)
            }).then(() => {
                this.storeMessages.showMessage("Event date successfully selected!\nYou will now be returned to the event list");
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
            navigator.clipboard.writeText(`${import.meta.env.VITE_FRONTEND_URL}/event/${this.$route.params.uuid}`);
        },
        displayDateRange(range: DateRange): string {
            // converts date range to a readable format
            const convertFunc = this.eventData?.event_calendar_type === CalendarType.Date ?
                formatDateDayMonthYear : formatDateDayMonthHour;
            if (convertFunc(range.start_date) === convertFunc(range.end_date))
                return convertFunc(range.start_date);
            return `${convertFunc(range.start_date)} - ${convertFunc(range.end_date)}`;
        },

        // not logged in actions
        onLoginOrSignup() {
            this.storeUser.redirectAfterLogin = this.$route.fullPath;
            this.$router.push("/login");
        },
        onSubmitAnon() {
            console.log("submit anonymously")
            // TODO:
            // - make an API point for creating an anonymous user which sets the token
        },
    },
    mounted() {
        if (!this.storeUser.user) {
            this.eventPageType = EventPageType.NotLoggedIn;
        }

        this.getEventData();
        this.getPreviousSelectedDateRanges();
        // this.getParticipants();
    },
    watch: {
        isOrganiserMode(isOrganiser: boolean) {
            if (isOrganiser) {
                // get participant data
                // this.getParticipants();
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
