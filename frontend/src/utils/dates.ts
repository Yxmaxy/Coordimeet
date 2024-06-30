import { CalendarType, DateRange } from "@/types/calendar";

function padNumber(number: number, places: number = 2): string {
    return number.toString().padStart(places, '0');
}

export function formatDateYMD(date: Date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())}`;
}

export function formatDateTimeYMD(date: Date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())} ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`;
}

export function formatDateDayMonthYear(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
}

export function formatDateDayMonth(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}.`;
}

export function formatDateDayMonthHour(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}. ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`;
}

export function formatDateHour(date: Date) {
    return `${padNumber(date.getHours())}:00`;
}

export function removeHoursMinutesFromDate(date: Date): Date {
    date.setHours(0, 0);
    return date;
}

export function initializeDateInput(type: CalendarType, date?: string, padding?: number): string {    
    const now = date === undefined ? removeHoursMinutesFromDate(new Date()) : new Date(date);
    if (padding !== undefined)
        now.setDate(now.getDate() + padding);
    if (type === CalendarType.Date)
        return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}`;
    return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}T${padNumber(now.getHours())}:00`;
}

export function formatDateRange(range: DateRange, calendarType: CalendarType, addToDateHour: boolean = true): string {
    const formatDate = calendarType === CalendarType.Date ? formatDateDayMonth : formatDateDayMonthHour;

    if (addToDateHour && calendarType === CalendarType.DateHour) {
        range = {
            start_date: new Date(range.start_date),
            end_date: addUnitsToDate(new Date(range.end_date), CalendarType.DateHour, 1)
        };
    } else {
        range = {
            start_date: new Date(range.start_date),
            end_date: new Date(range.end_date)
        };
    }

    const formattedStart = formatDate(range.start_date);
    const formattedEnd = formatDate(range.end_date);

    if (formattedStart === formattedEnd)
        return formattedStart;
    return `${formattedStart} - ${formattedEnd}`;
}

export function formatDateByCalendarType(date: Date, calendarType: CalendarType): string {
    const formatDate = calendarType === CalendarType.Date ? formatDateDayMonthYear : formatDateDayMonthHour;
    return formatDate(date);
}

export function addUnitsToDate(date: Date, calendarType: CalendarType, units: number) {
    if (calendarType === CalendarType.Date)
        date.setDate(date.getDate() + units);
    else if (calendarType === CalendarType.DateHour)
        date.setHours(date.getHours() + units);
    return date;
}
