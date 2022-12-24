<template>
    <div class="event" v-for="event in events" @click="$router.push(`/event/${event.IDEvent}`)">
        <div>
            <b>{{ event.Name }}</b>
            <div>{{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}</div>
        </div>
        <div>
            <div>{{ formatDateDayMonthYear(new Date(event.Deadline)) }}</div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from 'vue';
import { formatDateDayMonthYear } from '../common/helpers';
import { IEvent } from '../common/interfaces';

export default {
    props: {
        events: {
            type: Array as PropType<IEvent[]>,
            required: true
        }
    },
    methods: {
        formatDateDayMonthYear,
    },
}
</script>

<style lang="scss" scoped>
@import "../styles/colors.scss";
.event {
    background-color: $color-background-3;
    margin: 0.75rem;
    padding: 1.25rem;
    border-radius: 20px;
    display: flex;
    justify-content: space-between;
    cursor: pointer;
    transition: 200ms;

    &:hover {
        background-color: $color-top-bottom;
        transform: translateY(-0.1rem);
    }

    & > div {
        display: flex;
        gap: 0.75rem;
    }
}
</style>