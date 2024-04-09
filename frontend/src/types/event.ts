import { CalendarType, DateRange } from "@/types/calendar";
import { User } from "@/types/user";

enum EventTypeChoices {
    // same as in apps.events.models
    Public = 1,
    Closed = 2,
    Private = 3,
}

export enum EventType {
    Public = 1,
    Closed = 2,
    Group = 3,
}

export interface EventAvailabilityOption extends DateRange {
    pk?: number,
    event?: Event,
}

export interface Event {
    pk?: number,

    title: string,
    event_uuid?: string,
    event_calendar_type: CalendarType,

    organiser?: User,
    // TODO: organiser_group

    description?: string,
    event_length: number,
    event_type: EventTypeChoices,
    deadline: Date,

    selected_start_date: Date | null,
    selected_end_date: Date | null,

    created_at: Date,
    updated_at: Date,

    event_availability_options: EventAvailabilityOption[],
}

export enum EventPageType {
    NonConfirmed = 0,   // invitee sees just basic event data, confirm decline button
    Invitee = 1,        // calendar and all event data
    Organiser = 2,      // data about user responses, ending data
    Finished = 3,       // Event has finished, show only the simplest information
}

export interface EventParticipant {
    GoogleID: string,
    FirstName: string,
    LastName: string,
    Dates: DateRange[],

    isSelected: boolean,
}
