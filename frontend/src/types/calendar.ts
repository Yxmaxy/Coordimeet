export interface DateRange {
    from: Date,
    to: Date,
}

export enum CalendarType {
    DateTime = 0,
    Date = 1,
}

export interface CalendarDate {
    date: Date,
    heatmap: number,  // number of "hits"
}
