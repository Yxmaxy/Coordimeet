<template>
    <div class="flex flex-col">
        <!-- Header -->
        <div class="flex z-20 sticky top-14 w-full shadow-md">
            <!-- Tab design -->
            <div
                v-if="isMobile"
                v-for="(tab, index) in tabs" :key="`mobile_header_${index}`"
                :class="[{
                    'bg-main-300 text-main-100': activeTab !== index,
                    'bg-main-200': activeTab === index,
                },
                'flex-1 flex items-center justify-center cursor-pointer select-none h-14',
                'transition-colors border-r-2 last:border-r-0 border-main-200']"
                @click="activeTab = index"
            >
                {{ tab.name }}
            </div>
            <!-- Desktop design -->
            <div
                v-else
                v-for="(tab, index) in tabs" :key="`desktop_header_${index}`"
                :class="[{
                    'max-w-[20rem]': !isMobile && tab.narrow === 'sm',
                    'max-w-[25rem]': !isMobile && tab.narrow === 'md',
                }, 'flex-1 flex items-center h-14 bg-main-100 shadow-md',
                   'border-r-2 last:border-r-0 border-main-200',
                   'font-bold text-xl px-4'
                ]"
            >
                {{ tab.name }}
            </div>
        </div>
        <!-- Content -->
        <div class="flex flex-row">
            <div
                v-for="(tab, index) of tabs"
                :key="`tab_content_${index}`"
                :class="[{
                    'max-w-[20rem]': !isMobile && tab.narrow === 'sm',
                    'max-w-[25rem]': !isMobile && tab.narrow === 'md',
                    'hidden': isMobile && index !== activeTab,
                    'border-r-2 last:border-r-0 border-main-200': !isMobile,
                }, 'flex-1 min-h-[calc(100vh-7rem)]']"
            >
                <template v-if="!isMobile || index === activeTab">
                    <slot :name="tab.slot_name"></slot>
                </template>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
import { PropType } from "vue";

import { Tab } from "@/types/tabs";

export default {
    name: "TabController",
    props: {
        tabs: {
            type: Array as PropType<Tab[]>,
            required: true,
        },
        breakpoint: {
            type: Number,
            default: 850,
        },
    },
    data() {
        return {
            isMobile: false,
            activeTab: 0,
        }
    },
    methods: {
        checkIsMobile() {
            this.isMobile = window.innerWidth <= this.breakpoint;
        },
    },
    mounted() {
        window.addEventListener('resize', this.checkIsMobile);
        this.checkIsMobile();
    },
    unmounted() {
        window.removeEventListener('resize', this.checkIsMobile);
    },
}
</script>
