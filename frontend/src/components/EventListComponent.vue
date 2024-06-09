<template>
    <div class="flex flex-col mt-2 pb-20">
        <div
            v-for="event in events"
            class="flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl
            cursor-pointer shadow-md transition-all hover:-translate-y-1 hover:bg-main-200"
            @click="() => $router.push(`/event/${event.event_uuid}`)"
        >
            <div class="flex justify-between w-full">
                <div>
                    <b>{{ event.title }}</b>
                    <div class="flex align-middle gap-1 text-sm">
                        <template v-if="event.is_group_organiser">
                            <custom-icon class="text-sm" icon="group" />
                            {{ event.invited_group?.name }}
                        </template>
                        <template v-else>
                            <custom-icon class="text-sm" icon="person" />
                            {{ event.organiser?.email }}
                        </template>
                    </div>
                </div>
                <div class="flex gap-2 items-center">
                    <template v-if="true">
                        <custom-button
                            class="h-8 w-8 rounded-full !text-base"
                            @click.stop="() => $router.push(`/event/${event.event_uuid}`)"
                        >
                            <custom-icon icon="calendar_today" />
                        </custom-button>
                        <custom-button
                            class="h-8 w-8 rounded-full !text-base"
                            @click.stop="() => $router.push(`/event/edit/${event.event_uuid}`)"
                        >
                            <custom-icon icon="edit" />
                        </custom-button>
                    </template>
                    <template v-else>
                        <custom-button class="h-8 w-8 rounded-full !text-base">
                            <custom-icon icon="event_available" />
                        </custom-button>
                        <custom-button class="h-8 w-8 rounded-full !text-base">
                            <custom-icon icon="event_repeat" />
                        </custom-button>
                    </template>
                    
                </div>
            </div>
            <div>
                <div
                    v-if="userIsOrganiser && event.selected_start_date && event.selected_end_date"
                    class="flex gap-2"
                >
                    <abbr title="Event deadline">
                        {{ formatDateDayMonthYear(new Date(event.deadline)) }}
                    </abbr>
                    <custom-icon class="text-base" icon="event_upcoming" />
                </div>
                <div
                    v-else-if="event.selected_start_date && event.selected_end_date"
                    class="flex gap-2 font-bold"
                >
                    <abbr title="Selected date">
                        {{ formatDateDayMonthYear(event.selected_start_date) }}
                        <template v-if="event.selected_start_date !== event.selected_end_date">
                            - {{ formatDateDayMonthYear(event.selected_end_date) }}
                        </template>
                    </abbr>
                    <custom-icon class="text-base" icon="event_available" />
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateDayMonthYear } from "@/utils/dates";
import { Event } from "@/types/event";

import CustomIcon from "@/components/ui/CustomIcon.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "EventListComponent",
    components: {
        CustomIcon,
        CustomButton,
    },
    props: {
        events: {
            type: Array as PropType<Event[]>,
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
