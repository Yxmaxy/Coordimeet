<template>
    <div class="calendar">
        <div v-for="day in days">
            {{day.date.getDate()}}
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
    },
    data() {
        return {
            days: [] as ICalendarDate[],
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
            const from = this.getBufferedDate(range.from, 7);
            const to = this.getBufferedDate(range.to, 7, true);
            
            for (let d = from; d <= to; d.setDate(d.getDate() + 1)) {
                console.log(d.getDate());
                
                this.days.push({
                    date: new Date(d),
                });
            }
        }
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
    }
}
</style>