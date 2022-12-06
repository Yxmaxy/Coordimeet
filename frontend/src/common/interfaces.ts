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
    Date = 0,
    DateTime = 1,
}

// Event data
export interface IEvent {
    CalendarType: CalendarType,
    Config: Object,
    EventDates: IDateRange[],
    Length: number,
    Name: string,
    Organiser: {
        FirstName: string,
        LastName: string,
        Email: string,
    },
    UrlJoinLink: string,
}
