<template>
    <div class="event" v-for="event in events" @click="$router.push(`/event/${event.IDEvent}`)">
        <div>
            <b>{{ event.Name }}</b> - 
            <abbr title="Organizer">{{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}</abbr>
        </div>
        <div>
            <abbr title="Event deadline">{{ formatDateDayMonthYear(new Date(event.Deadline)) }}</abbr>
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
            default: [],
            required: true,
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
}
</style>