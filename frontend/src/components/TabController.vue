<template>
    <div>
        <!-- Header -->
        <div class="flex">
            <!-- Tab design -->
            <div
                v-if="isMobile"
                v-for="(slotName, index) of Object.keys($slots)" :key="index"
                :class="[{
                    'bg-main-300 text-main-100': activeTab !== index,
                    'bg-main-200 text-main-700': activeTab === index,
                },
                'flex-1 flex items-center justify-center cursor-pointer select-none h-14',
                'transition-colors border-r-2 last:border-r-0 border-main-200']"
                @click="$emit('update:activeTab', index)"
            >
                {{ tabName[slotName] }}
            </div>
            <!-- Normal design -->
            <div
                v-else
                v-for="(slotName, index) of Object.keys($slots)" :key="`${index}_else`"
                class="flex-1 flex items-center h-14
                bg-main-100 border-r-2 last:border-r-0 border-main-200
                font-bold text-xl px-4"
            >
                {{ tabName[slotName] }}
            </div>
        </div>
        <!-- Content -->
        <div class="flex flex-row h-full">
            <div
                v-for="(slot, index) of Object.keys($slots)"
                :key="index"
                :class="[{
                    'flex-1 border-r-2 border-main-200 last:border-r-0': !isMobile,
                }, 'h-[calc(100%-1.5rem)]']"
            >
                <div v-if="!isMobile || activeTab === index">
                    <slot :name="slot"></slot>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
import { tabName } from '@/utils/tabs';

export default {
    name: "TabController",
    setup() {
        return {
            tabName: tabName as any,
        }
    },
    props: {
        activeTab: {
            type: Number,
            default: 0,
        },
    },
    data() {
        return {
            isMobile: false,
        }
    },
    methods: {
        checkIsMobile() {
            this.isMobile = window.innerWidth <= 768;
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
