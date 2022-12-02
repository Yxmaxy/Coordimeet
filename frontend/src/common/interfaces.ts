// Calendar date range
export interface IDateRange {
    from: Date,
    to: Date,
}

// Single calendar date
export interface ICalendarDate {
    display: number,
    date: Date,
    isInRange: boolean,
    isAvailable?: boolean,
}