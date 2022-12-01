// Calendar date range
export interface IDateRange {
    from: Date,
    to: Date,
}

// Single calendar date
export interface ICalendarDate {
    date: number,
    isInRange: boolean,
}