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

export function formatDateForBackend(date: Date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())} ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:00`;
}

export function initializeDateInput(type: CalendarType, date?: string, padding?: number): string {    
    const now = date === undefined ? removeHoursMinutesFromDate(new Date()) : new Date(date);
    if (padding !== undefined)
        now.setDate(now.getDate() + padding);
    if (type === CalendarType.Date)
        return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}`;
    return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}T${padNumber(now.getHours())}:00`;
}

export function formatDateRange(range: DateRange): string {
    if (range.start_date === range.end_date)
        return formatDateDayMonthYear(range.start_date);
    return `${formatDateDayMonthYear(range.start_date)} - ${formatDateDayMonthYear(range.end_date)}`;
}
