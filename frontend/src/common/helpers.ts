export function formatDateDayMonth(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}.`;
}

export function formatDateHourDayMonth(date: Date) {
    return `${date.getHours()}:00 - ${date.getDate()}. ${date.getMonth() + 1}`;
}
