<template>
    <div v-if="!insertMode" class="controls">
        <label>
            Select unavailable dates
            <input v-model="selectUnavailable" type="checkbox" />
        </label>
        <label>
            <button @click="invertDates">Invert dates</button>
        </label>
        <label>
            <button @click="resetDates">Reset dates</button>
        </label>
        <label v-if="(type === 0)">
            Selected week: {{(selectedWeek + 1)}} / {{(numOfWeeks + 1)}}
            <button @click="changeSelectedWeek(false)">Prev</button>
            <button @click="changeSelectedWeek(true)">Next</button>
        </label>
    </div>
    <div v-if="insertMode" class="controls">
        <label>
            <button @click="resetDates">Reset dates</button>
        </label>
        <label v-if="(type === 0)">
            Selected week: {{(selectedWeek + 1)}} / {{(numOfWeeks + 1)}}
            <button @click="changeSelectedWeek(false)">Prev</button>
            <button @click="changeSelectedWeek(true)">Next</button>
        </label>
    </div>
    <div class="calendar-header">
        <div v-for="day in calendarHeader">
            {{ day }}
        </div>
    </div>
    <div :class="['calendar-component', {'type-datetime': type === 0}]">
        <template v-for="(day, index) in days">
            <div
                v-if="type === 1 || (index >= selectedWeek * 24 * 7 && index < (1 + selectedWeek) * 24 * 7)"
                :class="{
                    'in-range': day.isInRange && !insertMode,
                    'in-range-insert': insertMode,
                    'available': day.isAvailable && !selectUnavailable,
                    'unavailable': day.isInRange && selectUnavailable && !day.isAvailable,
                }"
                @mousedown="(event) => onMouseDown(event, day)"
                @mouseenter="(event) => onMouseEnter(event, day)"
                @mouseup="onMouseUp"
                @mouseleave="(event) => onMouseLeave(event, day)"
                @touchstart="(event) => onTouchStart(event, day)"
                @touchend="(event) => onTouchEnd(event, day)"
            >
                {{day.display}}
            </div>
        </template>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateDayMonth, formatDateHour } from "../common/helpers";
import { IDateRange, ICalendarDate, CalendarType } from '../common/interfaces';
const longpressTimeout = 475;

export default {
    name: "calendar",
    props: {
        dateRanges: {
            type: Array as PropType<IDateRange[]>,
            default: [],
        },
        type: {
            type: Number,
            default: CalendarType.Date,
        },
        days: {
            type: Array as PropType<ICalendarDate[]>,
            default: [],
        },
        insertMode: {  // if all selected are in range
            type: Boolean,
            default: false,
        }
    },
    data() {
        return {
            touchStart: undefined as ICalendarDate|undefined,
            timeoutObj: undefined as number|undefined,
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
            if (this.type === CalendarType.Date)
                return days;
            for (let i = 0; i < days.length; i++) {
                days[i] = `${days[i]} ${formatDateDayMonth(this.days[i * 24 + this.selectedWeek * 24 * 7].date)}`;
            }
            return days;
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
        // increment date by hour or day
        incrementDate(date: Date): Date {
            if (this.type === CalendarType.Date)
                return new Date(date.setDate(date.getDate() + 1));
            return new Date(date.setHours(date.getHours() + 1));
        },
        // calculate dates to display on calendar
        calculateShownDates() {
            // get from and to dates
            let from: undefined|Date = undefined
            let to: undefined|Date = undefined
            for (const range of (this.dateRanges as IDateRange[])) {
                if (from === undefined || range.from < from)
                    from = new Date(new Date(range.from).setHours(0));
                if (to === undefined || range.to > to)
                    to = new Date(new Date(range.to).setHours(0));
            }
            if (from === undefined || to === undefined)  // setting failed
                return;
            if (this.type === CalendarType.DateTime) {  // set to full day
                from.setHours(0);
                to.setHours(23);
            }
            from = this.getBufferedDate(from, 0);
            to = this.getBufferedDate(to, 0, true);
            
            this.days.length = 0;  // reset array
            for (let d = new Date(from); d <= to; d = this.incrementDate(d)) {  // loop through all dates
                let isInRange = false || this.insertMode;
                for (const range of (this.dateRanges as IDateRange[])) {  // loop through selection
                    if (d >= range.from && d <= range.to) {
                        isInRange = true;
                        break;
                    }
                }
                this.days.push({
                    display: (this.type === CalendarType.Date) ?
                        formatDateDayMonth(d) : formatDateHour(d),
                    date: new Date(d),
                    isInRange: isInRange,
                });
            }
        },
        selectDateFromTo(start: ICalendarDate, end: ICalendarDate, setAvailable: boolean = true) {
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
        onMouseDown(event: MouseEvent, day: ICalendarDate) {
            if (!day.isInRange)
                return;
            this.touchStart = day;
            day.isAvailable = !day.isAvailable;
        },
        onMouseEnter(event: MouseEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        onMouseUp() {
            this.touchStart = undefined;
        },
        onMouseLeave(event: MouseEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        // methods for mobile devices
        onTouchStart(event: TouchEvent, day: ICalendarDate) {
            event.preventDefault();
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
        onTouchEnd(event: TouchEvent, day: ICalendarDate) {
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
        }
    },
    mounted() {
        this.calculateShownDates();
    },
};
</script>
<style lang="scss" scoped>
@import "../styles/colors";

.calendar-component {
    box-sizing: border-box;
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;

    &.type-datetime {
        grid-template-rows: repeat(24, 1fr);
        grid-auto-flow: column;
        grid-template-columns: unset !important;
    }

    // td
    & > div {
        display: flex;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
        user-select: none;
    }
    .in-range {
        background-color: lightgoldenrodyellow;
        cursor: pointer;
    }
    .in-range-insert {
        cursor: pointer;
    }
    .available {
        background-color: lightgreen;
    }
    .unavailable {
        background-color: lightcoral;
    }
}
.calendar-header {
    display: flex;
    div {
        font-weight: bold;
        color: $color-background;
        background-color: $color-main;

        text-align: center;
        flex: 1;
    }
}
</style>
