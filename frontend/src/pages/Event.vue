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
                                    If you try to access the same event again, you will not be able to see your previous response.
                                </help-icon>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="flex justify-center gap-4 mt-4">
                    <custom-button @click="() => $router.push('/')">Decline</custom-button>
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
                            :click="declineInvitation"
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
            :breakpoint="1290"
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
                    }, 'cursor-pointer hover:bg-main-100',
                    'p-[1.1rem] font-bold border-b-2 border-b-main-200 transition-colors',
                    'flex justify-between items-center']"
                    @click="toggleParticipant(participant)"
                >
                    {{ participant.user.email }}
                    <custom-icon v-if="participant.not_comming" icon="event_busy"/>
                    <custom-icon v-if="!participant.not_comming" icon="event_available"/>
                </div>
            </template>

            <template v-slot:date_choices>
                <div
                    v-for="dateRange in getBestDateRanges"
                    :class="[
                        'cursor-pointer hover:bg-main-100', 'p-[1.1rem] font-bold border-b-2 border-b-main-200 transition-colors',
                    'flex justify-between items-center']"
                >
                    <div>{{ formatDateRange(dateRange.range) }}</div>
                    <div>{{ dateRange.hits }}</div>
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

import { formatDateDayMonthYear, formatDateDayMonthHour, formatDateRange } from "@/utils/dates";

import EventData from "@/components/EventData.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

interface DateChoice {
    range: DateRange;
    hits: number;
}

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

            storeMessages,

            EventPageType,
            CalendarType,
        }
    },
    data() {
        return {
            eventData: null as null|Event,
            eventPageType: EventPageType.NonConfirmed as EventPageType,
            eventParticipants: [] as EventParticipant[],

            selectedDateRanges: [] as DateRange[],  // the current calendar selection
            previousSelectedDateRanges: [] as DateRange[],  // set if the invitee submitted before

            isOrganiserMode: true,  // organiser mode toggle
            gettingParticipantData: false,  // for fetching event participants

            tabs: [] as Tab[],
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
            if (!this.isOrganiserMode || !this.eventParticipants)
                return [];
            const participantDates = this.eventParticipants
                .filter(participant => participant.isSelected)
                .flatMap((participant: EventParticipant) => 
                    participant.participant_availabilities.map(availability => ({
                        start_date: new Date(availability.start_date),
                        end_date: new Date(availability.end_date),
                    }))
                ) as DateRange[];
            return participantDates;
        },
        getBestDateRanges(): DateChoice[] {
            // Loop through all date ranges in selectedEventParticipantDateRanges.
            // Move through each date range by using the addUnitsToDate helper
            // The calendarType parameter is provided by eventData.event_calendar_type
            // Add each unit to a map with the number of times it appears.

            if (!this.isOrganiserMode || this.eventData === null )
                return []

            // create a map for each possible date with the number of "hits"
            const dateCountMap = new Map<string, number>();
            const calendarType = this.eventData.event_calendar_type;

            this.selectedEventParticipantDateRanges.forEach(range => {
                let currentDate = new Date(range.start_date);
                const endDate = new Date(range.end_date);

                while (currentDate <= endDate) {
                    const dateString = currentDate.toISOString();
                    dateCountMap.set(dateString, (dateCountMap.get(dateString) || 0) + 1);
                    currentDate = this.addUnitsToDate(currentDate, calendarType, 1);
                }
            });

            // Join all adjacent dates in dateCountMap into date ranges
            // with the length of this.eventDate.length
            // Sum the number of "hits" for each date range
            // Return an ordered list of date ranges with the highest "hits"

            const dateRangesWithHits: DateChoice[] = [];
            let currentRange: DateRange | null = null;
            let currentHits = 0;

            Array.from(dateCountMap.keys()).sort().forEach(dateString => {
                const date = new Date(dateString);
                const hits = dateCountMap.get(dateString) || 0;

                if (currentRange && this.addUnitsToDate(new Date(currentRange.end_date), calendarType, 1).toISOString() === dateString) {
                    // The date is adjacent to the current range, extend the current range and add the hits
                    currentRange.end_date = date;
                    currentHits += hits;
                } else {
                    // The date is not adjacent to the current range, save the current range and start a new one
                    if (currentRange) {
                        dateRangesWithHits.push({ range: currentRange, hits: currentHits });
                    }
                    currentRange = { start_date: date, end_date: date };
                    currentHits = hits;
                }
            });

            // Save the last range
            if (currentRange) {
                dateRangesWithHits.push({ range: currentRange, hits: currentHits });
            }

            // Sort the date ranges by hits in descending order
            dateRangesWithHits.sort((a, b) => b.hits - a.hits);

            // Return the sorted date ranges
            return dateRangesWithHits;
        },
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
                    this.getParticipants();
                    this.tabs =  [
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
                            name: "Date choices",
                            slot_name: "date_choices",
                            narrow: "sm",
                            icon: "calendar_clock",
                        },
                        {
                            name: "Calendar",
                            slot_name: "calendar",
                            icon: "calendar_today",
                        },
                    ]
                } else {
                    this.tabs =  [
                        {
                            name: "Event",
                            slot_name: "event",
                            narrow: "md",
                            icon: "description",
                        },
                        {
                            name: "Calendar",
                            slot_name: "calendar",
                            icon: "calendar_today",
                        },
                    ]
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

                    if (response.data.participant_availabilities.length !== 0 || response.data.not_comming) {
                        // "upgrade" user to invitee if the data was submitted
                        if (this.eventPageType === EventPageType.NonConfirmed)
                            this.eventPageType = EventPageType.Invitee;

                        // update selectedDateRanges with previous response
                        this.previousSelectedDateRanges = response.data.participant_availabilities.map((range: DateRange) => ({
                            start_date: new Date(range.start_date),
                            end_date: new Date(range.end_date),
                        }));

                        // intialize the selected date ranges
                        this.selectedDateRanges = this.previousSelectedDateRanges;
                    }
                });
        },
        getParticipants() {
            this.gettingParticipantData = true;
            ApiService.get(`/events/event/organiser/${this.$route.params.uuid}/`)
                .then(res => {
                    if (res.data.error) {
                        this.storeMessages.showMessageError(`An error occured while fetching the participants: ${res.data.error}`)
                        return;
                    }
                    if (res.data.length === 0)
                        return;

                    // set the participants array
                    this.eventParticipants = res.data.map((participant: any) => {
                        return {
                            ...participant,
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
            const data = !this.isSelectedDateRangesSet ? {not_comming: true} : {
                participant_availabilities: this.selectedDateRanges.map(range => ({
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
                    if (this.storeUser.user!.id === this.eventData?.organiser?.id)
                        this.getParticipants();
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
        declineInvitation() {
            ApiService.post(`/events/event/participants/${this.$route.params.uuid}/`, {not_comming: true})
            .then((response: AxiosResponse) => {
                if (response.status !== 200)
                    return;
                this.storeMessages.showMessage("You have declined the invitation");
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
            this.storeMessages.showMessage("Link copied to clipboard", 1000);
        },
        displayDateRange(range: DateRange): string {
            // converts date range to a readable format
            const convertFunc = this.eventData?.event_calendar_type === CalendarType.Date ?
                formatDateDayMonthYear : formatDateDayMonthHour;
            if (convertFunc(range.start_date) === convertFunc(range.end_date))
                return convertFunc(range.start_date);
            return `${convertFunc(range.start_date)} - ${convertFunc(range.end_date)}`;
        },
        addUnitsToDate(date: Date, calendarType: CalendarType, units: number) {
            if (calendarType === CalendarType.Date)
                date.setDate(date.getDate() + units);
            else if (calendarType === CalendarType.DateHour)
                date.setHours(date.getHours() + units);
            return date;
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
        formatDateRange,
    },
    mounted() {
        this.getEventData();
        if (!this.storeUser.user) {
            this.eventPageType = EventPageType.NotLoggedIn;
        } else {
            this.getPreviousSelectedDateRanges();
        }

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
