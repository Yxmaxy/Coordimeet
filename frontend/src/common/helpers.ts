export function formatDateDayMonth(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}.`;
}