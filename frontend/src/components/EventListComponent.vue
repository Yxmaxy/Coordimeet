<template>
    <div
        v-for="event in events"
        class="event"
        @click="$router.push(`/event/${event.IDEvent}`)"
    >
        <div>
            <b>{{ event.Name }}</b>
            <abbr v-if="!userIsOrganiser" title="Organizer">
                - {{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}
            </abbr>
        </div>
        <div>
            <abbr v-if="userIsOrganiser && event.SelectedDate === null" title="Event deadline">
                {{ formatDateDayMonthYear(new Date(event.Deadline)) }}
            </abbr>
            <abbr
                v-else
                class="selected-date"
                title="Selected date"
            >
                {{ event.SelectedDate }}
            </abbr>
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
        },
        userIsOrganiser: {
            type: Boolean,
            default: false,
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
    .selected-date {
        font-weight: bold;
    }
}
</style>