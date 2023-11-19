<template>
    <div class="mx-2 mb-2">
        <!-- Controls -->
        <div
            class="flex py-2 justify-between"
        >
            <div class="flex gap-1 items-center">
                <custom-button
                    @click="resetSelectedDateRanges"
                    :small="true"
                >
                    Reset selection
                </custom-button>
                <custom-button
                    @click="invertSelectedDateRanges"
                    :small="true"
                >
                    Invert selection
                </custom-button>
                <label class="text-sm flex gap-1">
                    <span>Unavailable dates</span>
                    <input v-model="selectUnavailable" type="checkbox" />
                </label>
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
                @touchstart.prevent="onDateTouchStart(date)"
                @touchend="onDateTouchEnd(date)"
            >
                <div
                    :class="[{
                        '!bg-calendar-available': isDateAvailable(date) && !selectUnavailable,
                        '!bg-calendar-unavailable': isDateUnavailable(date) || selectUnavailable && !isDateAvailable(date) && !isDateDisabled(date),
                        '!bg-calendar-disabled !cursor-not-allowed': isDateDisabled(date),
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

            selectUnavailable: false,  // is user selecting unavailable dates
            longpressTimeout: null as null | ReturnType<typeof setTimeout>,

            selectedWeek: 0,  // current selected week
        }
    },
    computed: {
        // calendar
        getCalendarDates(): Date[] {
            // gets dates to display on the calendar
            if (!this.roughEventDateRange)
                return [];
            const dates: Date[] = [];
            const datePadding = 7;  // how many days to add to the calendar
            const datesLimit = this.calendarType === CalendarType.Date ? 371 : 24 * 7;
            
            // functions for calculating the correct padding for from and to dates
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

        // weeks
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

        // dates
        dateDisplayFunction() {
            if (this.calendarType === CalendarType.DateTime)
                return formatDateHour;
            return formatDateDayMonth;
        },
        creatingDateRange(): DateRange | null {
            // used when the user is interacting with the calendar
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
        defaultDateRanges(): DateRange[] {
            // used when reseting the selection
            if (this.selectableDateRanges.length !== 0)
                return this.selectableDateRanges;
            if (this.getCalendarDates.length > 0) {
                const firstDate = this.getCalendarDates[0];
                const lastDate = this.getCalendarDates[this.getCalendarDates.length - 1];
                return [{
                    from: new Date(firstDate),
                    to: new Date(lastDate)
                } as DateRange]
            }

            return []
        },
    },
    methods: {
        // imported methods
        formatDateDayMonth,
        formatDateDayMonthYear,

        // event handlers
        onDateMouseDown(date: Date) {
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            this.fromDate = date;
            this.toDate = date;
            this.fromMode = this.isDateInSelectedDateRanges(date) ? "delete" : "add";
        },
        onDateMouseUp(date: Date) {
            if (!this.fromDate)  // this should always be set
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
                updateSelectedDateRanges = this.deleteDateRangeFromDateRanges(newDateRange, updateSelectedDateRanges);
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
        onDateTouchStart(date: Date) {
            if (this.fromDate === null) {  // start user selection
                this.longpressTimeout = setTimeout(() => {
                    window.navigator.vibrate(200);
                    this.onDateMouseDown(date);
                }, 350)
            } else {  // end user selection
                this.onDateMouseUp(date);
                this.longpressTimeout = null;
            }
        },
        onDateTouchEnd(date: Date) {
            // long press was canceled on same date
            if (this.fromDate?.getTime() === date.getTime() || this.longpressTimeout === null)
                return;
            clearInterval(this.longpressTimeout);
            this.longpressTimeout = null;
            // select the current date
            this.onDateMouseDown(date);
            this.onDateMouseUp(date);
        },

        // interaction handlers
        deleteDateRangeFromDateRanges(deleteDateRange: DateRange, dateRanges: DateRange[]): DateRange[] {
            // remove "eaten up" ranges
            dateRanges = dateRanges.filter(x => {
                return !(x.from >= deleteDateRange.from && x.to <= deleteDateRange.to);
            });
            
            for (const dateRange of dateRanges) {
                if (dateRange.from <= deleteDateRange.from && deleteDateRange.to <= dateRange.to) {
                    // selection splits existing range
                    if (deleteDateRange.from > dateRange.from && deleteDateRange.to < dateRange.to) {
                        // add current selection to date range
                        const newDateFrom = new Date(deleteDateRange.from);
                        const newDateTo = new Date(deleteDateRange.to);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.calendarType, -1);
                        this.addUnitsToDate(newDateTo, this.calendarType, 1);

                        // create new date range for last part
                        dateRanges.push({
                            from: newDateTo,
                            to: dateRange.to,
                        });
                        // update current range for first part
                        dateRange.to = new Date(newDateFrom);
                        continue;
                    }
                    // remove from start
                    if (deleteDateRange.from.getTime() === dateRange.from.getTime()) {
                        const newDateTo = new Date(deleteDateRange.to);
                        // add padding
                        this.addUnitsToDate(newDateTo, this.calendarType, 1)

                        dateRange.from = newDateTo;
                    }
                    // remove from end
                    if (deleteDateRange.to.getTime() === dateRange.to.getTime()) {
                        const newDateFrom = new Date(deleteDateRange.from);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.calendarType, -1)

                        dateRange.to = newDateFrom;
                    }
                }
            }
            return dateRanges;
        },

        // date helpers
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
        deepCopyDateRange(dateRange: DateRange): DateRange {
            return {
                from: new Date(dateRange.from),
                to: new Date(dateRange.to),
            } as DateRange
        },
        invertSelectedDateRanges() {
            let updateSelectedDateRanges = this.defaultDateRanges.map(this.deepCopyDateRange);
            for (const selectedDateRange of this.selectedDateRanges)
                updateSelectedDateRanges = this.deleteDateRangeFromDateRanges(selectedDateRange, updateSelectedDateRanges);
            this.$emit('update:selectedDateRanges', updateSelectedDateRanges);
        },
        resetSelectedDateRanges() {
            // sets the selected date ranges either to full or empty
            const updateSelectedDateRanges = this.selectUnavailable ?
                this.defaultDateRanges.map(this.deepCopyDateRange) : []
            this.$emit('update:selectedDateRanges', updateSelectedDateRanges)
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

        // calendar colors
        isDateAvailable(date: Date): boolean {
            if (this.isDateInSelectedDateRanges(date))
                return true;
            // check if date is currently selected
            return this.fromMode === 'add' &&
                this.creatingDateRange !== null &&
                this.isDateInDateRange(date, this.creatingDateRange)
        },
        isDateUnavailable(date: Date): boolean {
            // is date currently being deleted
            return this.fromMode === 'delete' &&
                this.creatingDateRange !== null &&
                this.isDateInDateRange(date, this.creatingDateRange)
        },
        isDateDisabled(date: Date): boolean {
            return !this.isDateInSelectableDateRanges(date);
        },
    },
    watch: {
        selectUnavailable() {
            // if selected date ranges are empty or completely full, reset whenever the unavailable is switched
            if (this.selectedDateRanges.length === 0 || this.selectedDateRanges.length === this.defaultDateRanges.length) {
                this.resetSelectedDateRanges();
            }
        },
    },
}
</script>
