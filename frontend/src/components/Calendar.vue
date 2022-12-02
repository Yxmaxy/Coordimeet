<template>
    <div class="calendar">
        <div
            v-for="day in days"
            :class="{
                'in-range': day.isInRange,
                'available': day.isAvailable && !selectUnavailable,
                'unavailable': day.isInRange && selectUnavailable && !day.isAvailable,
            }"
            @pointerdown="(event) => onPointerDown(event, day)"
            @pointerenter="(event) => onPointerEnter(event, day)"
            @pointerup="onPoinerUp"
            @pointerleave="(event) => onPointerLeave(event, day)"
        >
            {{day.display}}
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { IDateRange, ICalendarDate } from '../common/interfaces';

export default defineComponent({
    name: "calendar",
    props: {
        dateRange: {
            type: Object,
            default: {
                from: new Date(),
                to: new Date()
            } as IDateRange
        },
        selectUnavailable: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            days: [] as ICalendarDate[],
            touchStart: undefined as ICalendarDate|undefined,
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
                new Date(d.setDate(d.getDate() + dayOfWeek)) :
                new Date(d.setDate(d.getDate() - dayOfWeek));
            
        },
        // calculate dates to display on calendar
        calculateShownDates() {
            const range = this.dateRange as IDateRange;
            const from = this.getBufferedDate(range.from, 0);
            const to = this.getBufferedDate(range.to, 0, true);

            for (let d = new Date(from); d <= to; d = new Date(d.setDate(d.getDate() + 1))) {
                this.days.push({
                    display: d.getDate(),
                    date: new Date(d),
                    isInRange: d >= range.from && d <= range.to,
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
        // methods for selecting available
        onPointerDown(event: PointerEvent, day: ICalendarDate) {
            if (!day.isInRange)
                return;
            this.touchStart = day;
            day.isAvailable = !day.isAvailable;
        },
        onPointerEnter(event: PointerEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        onPoinerUp() {
            this.touchStart = undefined;
        },
        onPointerLeave(event: PointerEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
    },
    mounted() {
        this.calculateShownDates();
    },
});
</script>
<style lang="scss" scoped>
.calendar {
    $border-width: 1px;
    $border-color: black;

    box-sizing: border-box;
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border: {
        width: calc($border-width / 2);
        style: solid;
        color: $border-color;
    };

    // td
    & > div {
        display: flex;
        justify-content: center;
        align-items: center;
        border: {
            width: $border-width;
            style: solid;
            color: $border-color;
        };
        box-sizing: border-box;
        cursor: pointer;
        user-select: none;
    }
    .in-range {
        background-color: lightgoldenrodyellow;
    }
    .available {
        background-color: lightgreen;
    }
    .unavailable {
        background-color: lightcoral;
    }
}
</style>