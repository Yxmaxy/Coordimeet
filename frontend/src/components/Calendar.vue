<template>
    <!-- Controls -->
    <div
        v-if="mode !== CalendarMode.Disabled"
        class="flex justify-between p-2 my-1"
    >
        <div>
            <custom-button
                @click="resetDates"
                :small="true"
            >
                Reset selection
            </custom-button>
            <custom-button
                v-if="mode === CalendarMode.Select"
                @click="invertDates"
                :small="true"
            >
                Invert selection
            </custom-button>
            <label v-if="mode === CalendarMode.Select">
                Select unavailable dates
                <input v-model="selectUnavailable" type="checkbox" />
            </label>
        </div>
        <div
            v-if="type === CalendarType.DateTime"
            class="flex gap-1 items-center"
        >
            Selected week: {{(selectedWeek + 1)}} / {{(numOfWeeks + 1)}}
            <custom-button
                class="ml-1"
                :click="changeSelectedWeek(false)"
                :disabled="selectedWeek === 0"
                :small="true"
            >
                Prev
            </custom-button>
            <custom-button
                :click="changeSelectedWeek(true)"
                :disabled="selectedWeek === numOfWeeks"
                :small="true"
            >
                Next
            </custom-button>
        </div>
    </div>
    <!-- Header -->
    <div class="flex">
        <div
            v-for="day in calendarHeader"
            class="flex-1 py-1 font-bold text-main-100 bg-main-500 text-center select-none"
            v-html="day"
        />
    </div>
    <div :class="[{
            'grid-cols-7': type === CalendarType.Date,
            'grid-flow-col grid-rows-24': type === CalendarType.DateTime,
        }, 'grid gap-0.5']"
    >
        <!-- TODO: calculate which days are shown beforehand! -->
        <template v-for="(day, index) in days" :key="`day_${index}`">
            <div
                v-if="type === CalendarType.Date || isDayInSelectedWeek(index)"
                :class="[{
                    '!bg-calendar-in-range cursor-pointer': day.isInRange && mode === CalendarMode.Select,
                    '!bg-calendar-available': day.isAvailable && !selectUnavailable,
                    '!bg-calendar-unavailable': day.isInRange && selectUnavailable && !day.isAvailable,
                    'cursor-pointer': mode === CalendarMode.Create,
                }, 'p-1.5 text-center select-none bg-calendar-non-selected']"
                @mousedown="event => onMouseDown(event, day)"
                @mouseenter="event => onMouseEnter(event, day)"
                @mouseup="onMouseUp"
                @mouseleave="event => onMouseLeave(event, day)"
                @touchstart="event => onTouchStart(event, day)"
                @touchend="event => onTouchEnd(event, day)"
            >
                {{ day.display }}
            </div>
        </template>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateDayMonth, formatDateHour, formatDateForBackend } from "@/utils/dates";
import { CalendarType, CalendarDate, DateRange, CalendarMode } from "@/types/calendar";

import CustomButton from "@/components/ui/CustomButton.vue";

const longpressTimeout = 475;

export default {
    name: "Calendar",
    components: {
        CustomButton,
    },
    setup() {
        return {
            CalendarType,
            CalendarMode,
        }
    },
    props: {
        dateRanges: {
            type: Array as PropType<DateRange[]>,
            default: [],
        },
        type: {
            type: Number as PropType<CalendarType>,
            default: CalendarType.Date,
        },
        days: {
            type: Array as PropType<CalendarDate[]>,
            default: [],
        },
        mode: {
            type: Number as PropType<CalendarMode>,
            default: CalendarMode.Select,
        },
        initialIsAvailable: {  // array of days which are initially selected
            type: Array as PropType<DateRange[]>,
            default: [],
        }
    },
    data() {
        return {
            touchStart: undefined as CalendarDate|undefined,
            timeoutObj: undefined as NodeJS.Timeout|undefined,
            selectedWeek: 0,
            selectUnavailable: false,
        }
    },
    computed: {
        numOfWeeks(): number {
            return this.days.length / 24 / 7 - 1;
        },
        calendarHeader(): string[] {
            const days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            // return just days for Date
            if (this.days.length === 0 || this.type === CalendarType.Date)
                return days;
            // append dates to headers on DateTime
            return days.map(
                (day, inx) => `${day}<br/>${formatDateDayMonth(this.days[inx * 24 + this.selectedWeek * 24 * 7].date)}`
            );
        }
    },
    methods: {
        // converts sun-mon to mon-sun
        // mon = 0; sun = 6
        getDayMonToSun(date: Date): number {
            const res = date.getDay() - 1;
            return res < 0 ? 6 : res;
        },
        // method gets date and returns start/end of the week the date is in
        getBufferedDate(date: Date, buffer: number = 0, end: boolean = false): Date {
            const d = new Date(date);  // copy date
            const dayOfWeek = (end ? 6 - this.getDayMonToSun(d) : this.getDayMonToSun(d)) + buffer;
            return end ?
                new Date(new Date(d.setDate(d.getDate() + dayOfWeek)).setHours(23)) :
                new Date(d.setDate(d.getDate() - dayOfWeek));
        },
        // check if date is in date ranges
        isDayInDateRanges(dateRanges: DateRange[], date: Date): boolean {
            for (const range of dateRanges)
                if (range.from <= date && date <= range.to)
                    return true;
            return false;
        },
        // increment date by hour or day
        incrementDate(date: Date): Date {
            if (this.type === CalendarType.Date)
                return new Date(date.setDate(date.getDate() + 1));
            return new Date(date.setHours(date.getHours() + 1));
        },
        isDayInSelectedWeek(index: number): boolean {
            return index >= this.selectedWeek * 24 * 7 && index < (1 + this.selectedWeek) * 24 * 7
        },
        // calculate dates to display on calendar
        calculateShownDates() {
            // TODO: do a proper fix for the recursion...
            const maxNumberOfDates = 24 * 7 * 10;

            if (this.type === CalendarType.DateTime)
                this.selectedWeek = 0;
            
            // get from and to dates
            let from: undefined|Date = undefined
            let to: undefined|Date = undefined
            for (const range of (this.dateRanges as DateRange[])) {
                if (from === undefined || range.from < from)
                    from = new Date(new Date(range.from).setHours(0));
                if (to === undefined || range.to > to)
                    to = new Date(new Date(range.to).setHours(0));
            }
            if (from === undefined || to === undefined)  // setting failed
                return;
            
            from = this.getBufferedDate(from, 0);
            to = this.getBufferedDate(to, 0, true);
            
            let numOfLoops = 0;
            this.days.length = 0;  // reset array
            for (let d = new Date(from); d <= to; d = this.incrementDate(d)) {  // loop through all dates
                let isInRange = false || this.mode === CalendarMode.Create;
                for (const range of (this.dateRanges as DateRange[])) {  // loop through selection
                    if (formatDateForBackend(d) >= formatDateForBackend(range.from) && formatDateForBackend(d) <= formatDateForBackend(range.to)) {
                        isInRange = true;
                        break;
                    }
                }
                this.days.push({
                    display: (this.type === CalendarType.Date) ?
                        formatDateDayMonth(d) : formatDateHour(d),
                    date: new Date(d),
                    isInRange: isInRange,
                    isAvailable: isInRange && this.isDayInDateRanges(this.initialIsAvailable, new Date(d)),
                });
                // condition to stop too long recursion
                numOfLoops++;
                if (numOfLoops > maxNumberOfDates)
                    return;
            }
        },
        selectDateFromTo(start: CalendarDate, end: CalendarDate, setAvailable: boolean = true) {
            const from = start.date < end.date ? start : end;
            const to = start.date < end.date ? end : start;
            for (const day of this.days) {
                if (day.date >= from.date && day.date <= to.date && day.isInRange)
                    day.isAvailable = setAvailable;
            }
        },
        // increment/decrement shown week
        changeSelectedWeek(increment: boolean) {            
            if (increment && this.selectedWeek < this.numOfWeeks) {
                this.selectedWeek++;
                return;
            }
            if (!increment && 0 < this.selectedWeek)
                this.selectedWeek--;
        },
        // inverts all dates from selected to non selected
        invertDates() {
            for (const day of this.days) {
                if (day.isInRange)
                    day.isAvailable = !day.isAvailable;
            }
        },
        // resets all dates to not selected
        resetDates() {
            for (const day of this.days) {
                if (day.isInRange)
                    day.isAvailable = this.selectUnavailable;
            }
        },
        // methods for selecting available
        onMouseDown(event: MouseEvent, day: CalendarDate) {
            if (!day.isInRange || this.mode === CalendarMode.Disabled)
                return;
            this.touchStart = day;
            day.isAvailable = !day.isAvailable;
        },
        onMouseEnter(event: MouseEvent, day: CalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined && this.mode !== CalendarMode.Disabled) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        onMouseUp() {
            this.touchStart = undefined;
        },
        onMouseLeave(event: MouseEvent, day: CalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined && this.mode !== CalendarMode.Disabled) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        // methods for mobile devices
        onTouchStart(event: TouchEvent, day: CalendarDate) {
            event.preventDefault();
            if (this.mode === CalendarMode.Disabled)
                return;
            if (this.touchStart === undefined) {  // press on first date
                this.timeoutObj = setTimeout(() => {  // if event is longpress select multiple
                    // Longpress event
                    window.navigator.vibrate(200);
                    this.touchStart = day;
                    this.timeoutObj = undefined;
                }, longpressTimeout);
            } else {  // press on first date if previous press was longpress
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
                this.touchStart = undefined;
            }
        },
        onTouchEnd(event: TouchEvent, day: CalendarDate) {
            if (this.mode === CalendarMode.Disabled)
                return;
            if (this.timeoutObj !== undefined) {
                // Normal event
                day.isAvailable = !day.isAvailable;
            }
            clearInterval(this.timeoutObj);
            this.timeoutObj = undefined;
        },
    },
    watch: {
        dateRanges() {
            this.calculateShownDates();
        },
        initialIsAvailable() {
            this.calculateShownDates();
        },
        selectUnavailable(n) {
            for (const day of this.days) {
                if (day.isAvailable === n)
                    return;
            }
            this.invertDates();
        }
    },
    mounted() {
        this.calculateShownDates();
    },
};
</script>
