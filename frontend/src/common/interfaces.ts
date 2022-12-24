// Calendar date range
export interface IDateRange {
    from: Date,
    to: Date,
}

// Single calendar date
export interface ICalendarDate {
    display: string,
    date: Date,
    isInRange: boolean,
    isAvailable?: boolean,
}

// Calendar type
export enum CalendarType {
    DateTime = 0,
    Date = 1,
}

// Event data
export interface IEvent {
    IDEvent: number,
    CalendarType: CalendarType,
    Config: Object,
    EventDates: IDateRange[],
    Length: number,
    Name: string,
    Deadline: string,
    Organizer: IUser,
    UrlJoinLink: string,
}

// User
export interface IUser {
    FirstName: string,
    LastName: string,
    Email: string,
    GoogleID: string,
    ProfilePhoto: string,
}

// Event page type
export enum EventPageType {
    Invitee = 0,        // calendar and all event data
    Organiser = 1,      // data about user responses, ending data
    NonConfirmed = 2,   // invitee sees just basic event data, confirm decline button
}
