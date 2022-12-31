<template>
    <div
        v-for="event in events"
        :class="['event', {'finished': event.SelectedDate !== null}]"
        @click="() => eventClick(event)"
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
        eventClick(event: IEvent) {
            if (event.SelectedDate === null)
                this.$router.push(`/event/${event.IDEvent}`)
            else
                alert(`The organizer had already finished this event. It will take place at: ${event.SelectedDate}`);
        },
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

    &.finished {
        &:hover{
            background-color: $color-background-3;
            transform: none;
            transition: 100ms;
        }
    }

    &:hover {
        background-color: $color-top-bottom;
        transform: translateY(-0.1rem);
    }
    .selected-date {
        font-weight: bold;
    }
}
</style>