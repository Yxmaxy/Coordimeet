import { CalendarType, DateRange } from "@/types/calendar";
import { User, Group } from "@/types/user";

export enum EventType {
    Public = 1,
    Group = 2,
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
    event_type: EventType,

    organiser?: User,
    organiser_group?: Group,

    invited_group?: Group,

    description?: string,
    event_length: number,
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
