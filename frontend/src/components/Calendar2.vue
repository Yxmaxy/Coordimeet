<template>
    <div class="mx-2">
        <!-- Controls -->
        <div
            class="flex py-2 justify-between"
        >
            <div>
                <!-- TODO: Other controls -->
            </div>
            <div
                v-if="calendarType === CalendarType.DateTime"
                class="flex gap-2 items-center"
            >
                Selected week: {{ selectedWeek + 1 }} / {{ numberOfAllWeeks + 1 }}
                <div class="flex gap-1">
                    <custom-button @click="prevWeek">Prev</custom-button>
                    <custom-button @click="nextWeek">Next</custom-button>
                </div>
            </div>
        </div>

        <!-- Header -->
        <div class="flex">
            <div
                v-for="header in getCalendarHeader"
                class="w-full text-main-000 bg-main-500 text-center font-bold py-2"
                v-html="header"
            ></div>
        </div>

        {{ selectedDateRanges }}

        <!-- Calendar -->
        <div :class="[{
            'grid-cols-7': calendarType === CalendarType.Date,
            'grid-flow-col grid-rows-24': calendarType === CalendarType.DateTime,
        }, 'grid']">
            <div
                v-for="date in getCalendarDates"
                class="p-[0.075rem] h-full"
                @mousedown="onDateMouseDown(date)"
                @mouseup="onDateMouseUp(date)"
                @mouseenter="event => onDateMouseEnter(event, date)"
                @mouseleave="onDateMouseLeave"
            >
                <div
                    :class="[{
                        '!bg-calendar-available': isDateInSelectedDateRanges(date) ||
                            (fromMode === 'add' && creatingDateRange && isDateInDateRange(date, creatingDateRange)),  // date is being selected
                        '!bg-calendar-unavailable': (fromMode === 'delete' && creatingDateRange && isDateInDateRange(date, creatingDateRange)),
                        '!bg-calendar-disabled !cursor-not-allowed': !isDateInSelectableDateRanges(date),  // date is in selectable date ranges
                    }, 'bg-calendar-default transition-colors duration-75',
                    'h-full py-2 flex items-center justify-center select-none cursor-pointer']"
                >
                    {{ dateDisplayFunction(date) }}
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";

import { formatDateDayMonthYear, formatDateDayMonth, formatDateDayMonthHour, formatDateHour, formatDateForBackend } from "@/utils/dates";
import { CalendarType, CalendarDate, DateRange, CalendarMode } from "@/types/calendar";

import CustomButton from "./ui/CustomButton.vue";

export default {
    name: "Calendar2",
    setup() {
        return {
            CalendarType,
        }
    },
    components: {
        CustomButton,
    },
    emits: [ "update:selectedDateRanges" ],
    props: {
        // rough event duration for calculating pages
        roughEventDateRange: {
            type: Object as PropType<DateRange>,
            required: true,
        },
        // selected date ranges shown in green
        selectedDateRanges: {
            type: Array as PropType<DateRange[]>,
            required: true,
        },
        // selectable date ranges shown which the user can choose
        selectableDateRanges: {
            type: Array as PropType<DateRange[]>,
            default: [],
        },
        // calendar type
        calendarType: {
            type: Number as PropType<CalendarType>,
            required: true,
        },
    },
    data() {
        return {
            fromDate: null as null | Date,  // set on from date select
            fromMode: "add" as "add" | "delete",  // mode when selecting from date
            toDate: null as null | Date,  // changed on date enter

            selectedWeek: 0,  // current selected week
        }
    },
    computed: {
        getCalendarDates(): Date[] {
            // gets dates to display on the calendar
            if (!this.roughEventDateRange)
                return [];
            const dates: Date[] = [];
            const datePadding = 7;  // how many days to add to the calendar
            const datesLimit = this.calendarType === CalendarType.Date ? 371 : 24 * 7;
            
            const rangeConversion = {
                [CalendarType.Date]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        newDate.setDate(newDate.getDate() - datePadding);
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        newDate.setDate(newDate.getDate() + datePadding);
                        return newDate;
                    },
                },
                [CalendarType.DateTime]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        newDate.setDate(newDate.getDate() + this.selectedWeek * 7);
                        newDate.setHours(0, 0);
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        newDate.setDate(newDate.getDate() + this.selectedWeek * 7);
                        newDate.setHours(23, 59);
                        return newDate;
                    },
                },
            }

            const { from: roughFrom, to: roughTo } = this.roughEventDateRange;
            const from = rangeConversion[this.calendarType].from(roughFrom);
            const to = rangeConversion[this.calendarType].to(roughTo);

            const date = new Date(from);
            for (let i = 0; date <= to && i < datesLimit; i++) {
                dates.push(new Date(date));
                this.addUnitsToDate(date, this.calendarType, 1)
            }
            return dates;
        },
        getCalendarHeader(): string[] {
            const days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            if (this.calendarType === CalendarType.Date)
                return days;
            return this.getCalendarDates
                .filter((_, index) => index % 24 === 0)
                .map((date, index) => `${days[index]}<br/>${formatDateDayMonth(date)}`);
        },
        dateDisplayFunction() {
            if (this.calendarType === CalendarType.DateTime)
                return formatDateHour;
            return formatDateDayMonth;
        },
        isPrevWeekEnabled(): boolean {
            return this.selectedWeek > 0;
        },
        isNextWeekEnabled(): boolean {
            return this.selectedWeek < this.numberOfAllWeeks;
        },
        numberOfAllWeeks(): number {
            const { from, to } = this.roughEventDateRange;
            return Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24 * 7));
        },
        creatingDateRange(): DateRange | null {
            if (!this.fromDate || !this.toDate)
                return null;
            // switch dates if necessary
            const from = this.fromDate < this.toDate ? this.fromDate : this.toDate;
            const to = this.fromDate > this.toDate ? this.fromDate : this.toDate;
            return {
                from: from,
                to: to,
            } as DateRange;
        },
    },
    methods: {
        // imported methods
        formatDateDayMonth,
        formatDateDayMonthYear,

        onDateMouseDown(date: Date) {
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            this.fromDate = date;
            this.toDate = date;
            this.fromMode = this.isDateInSelectedDateRanges(date) ? "delete" : "add";
        },
        onDateMouseUp(date: Date) {
            if (!this.fromDate)  // this is always set, only here for typescript
                return;
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            const from = this.fromDate < date ? this.fromDate : date;
            const to = this.fromDate > date ? this.fromDate : date;

            const newDateRange = {
                from: from,
                to: to,
            } as DateRange;

            let updateSelectedDateRanges = this.selectedDateRanges;

            if (this.fromMode === "delete") {  // date range started on a selected date
                // remove "eaten up" ranges
                updateSelectedDateRanges = updateSelectedDateRanges.filter(x => {
                    return !(x.from >= newDateRange.from && x.to <= newDateRange.to);
                });
                
                for (const dateRange of updateSelectedDateRanges) {
                    if (dateRange.from <= newDateRange.from && newDateRange.to <= dateRange.to) {
                        // selection splits existing range
                        if (newDateRange.from > dateRange.from && newDateRange.to < dateRange.to) {
                            // add current selection to date range
                            const newDateFrom = new Date(newDateRange.from);
                            const newDateTo = new Date(newDateRange.to);
                            // add padding
                            this.addUnitsToDate(newDateFrom, this.calendarType, -1);
                            this.addUnitsToDate(newDateTo, this.calendarType, 1);

                            // create new date range for last part
                            updateSelectedDateRanges.push({
                                from: newDateTo,
                                to: dateRange.to,
                            });
                            // update current range for first part
                            dateRange.to = new Date(newDateFrom);
                            return;
                        }
                        // remove from start
                        if (newDateRange.from.getTime() === dateRange.from.getTime()) {
                            const newDateTo = new Date(newDateRange.to);
                            // add padding
                            this.addUnitsToDate(newDateTo, this.calendarType, 1)

                            dateRange.from = newDateTo;
                        }
                        // remove from end
                        if (newDateRange.to.getTime() === dateRange.to.getTime()) {
                            const newDateFrom = new Date(newDateRange.from);
                            // add padding
                            this.addUnitsToDate(newDateFrom, this.calendarType, -1)

                            dateRange.to = newDateFrom;
                        }
                    }
                }
                
            } else if (this.fromMode === "add") {  // date range started on a non-selected date
                // remove "eaten up" ranges
                updateSelectedDateRanges = updateSelectedDateRanges.filter(x => {
                    return !(x.from >= newDateRange.from && x.to <= newDateRange.to);
                });
                // check for new gaps in selectableDateRanges
                if (this.selectableDateRanges) {
                    for (let i = 0; i < this.selectableDateRanges.length - 1; i++) {
                        const selectableDateRange = this.selectableDateRanges[i];
                        const nextSelctableDateRange = this.selectableDateRanges[i + 1];
                        // new date range from is inside a selected date range and to is outside
                        if (this.isDateInDateRange(newDateRange.from, selectableDateRange) && newDateRange.to > selectableDateRange.to) {
                            // insert a date range for the first selectable part
                            const previousDateRange = {
                                from: newDateRange.from,
                                to: selectableDateRange.to
                            } as DateRange
                            // modify the new date range to start on the next selectable date range
                            newDateRange.from = nextSelctableDateRange.from;
                            updateSelectedDateRanges.push(previousDateRange);
                        }
                    }
                }
                // append new date range
                updateSelectedDateRanges.push(newDateRange);
                // sort date ranges
                updateSelectedDateRanges = updateSelectedDateRanges.sort((a, b) => a.from.getTime() - b.from.getTime());
                // cleanup - join ranges
                for (const dateRange of updateSelectedDateRanges) {
                    for (const siblingDateRange of updateSelectedDateRanges) {
                        // skip duplicates; dateRange is always smaller than siblingDateRange
                        if (dateRange.from >= siblingDateRange.from)
                            continue;
                        // join sibling ranges
                        const nextDate = new Date(dateRange.to);
                        this.addUnitsToDate(nextDate, this.calendarType, 1);
                        if (nextDate.getTime() === siblingDateRange.from.getTime()) {
                            dateRange.to = siblingDateRange.to;
                            updateSelectedDateRanges = updateSelectedDateRanges.filter(x => x !== siblingDateRange);
                        }
                    }
                }
            }
            // emit the changes
            this.$emit("update:selectedDateRanges", updateSelectedDateRanges);
            this.fromDate = null;
        },
        onDateMouseEnter(event: MouseEvent, date: Date) {
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            if (event.buttons !== 1)
                return;
            this.toDate = date;
        },
        onDateMouseLeave() {
            this.toDate = null;
        },

        // dates
        isDateInSelectedDateRanges(date: Date): boolean {
            return this.selectedDateRanges
                .some(dateRange => this.isDateInDateRange(date, dateRange));
        },
        isDateInDateRange(date: Date, dateRange: DateRange) {
            return date >= dateRange.from && date <= dateRange.to;
        },
        isDateInSelectableDateRanges(date: Date): boolean {
            if (this.selectableDateRanges.length === 0)
                return true;
            return this.selectableDateRanges
                .some(dateRange => this.isDateInDateRange(date, dateRange));
        },
        addUnitsToDate(date: Date, calendarType: CalendarType, units: number) {
            if (calendarType === CalendarType.Date)
                date.setDate(date.getDate() + units);
            else if (calendarType === CalendarType.DateTime)
                date.setHours(date.getHours() + units);
            return date;
        },

        // weeks
        prevWeek() {
            if (this.isPrevWeekEnabled)
                this.selectedWeek--;
        },
        nextWeek() {
            if (this.isNextWeekEnabled)
                this.selectedWeek++;
        },
    },
}
</script>
