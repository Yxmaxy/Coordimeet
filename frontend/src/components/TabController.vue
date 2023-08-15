<template>
    <div>
        <!-- Header -->
        <div v-if="isMobile" class="flex">
            <div
                v-for="(slotName, index) of Object.keys($slots)" :key="index"
                :class="[{
                    'bg-main-400 text-main-100': activeTab !== index,
                    'bg-main-200 text-main-700': activeTab === index,
                }, 'flex-1 text-center py-2 cursor-pointer transition-colors select-none border-r-2 border-main-200']"
                @click="$emit('update:activeTab', index)"
            >
                {{ tabName[slotName] }}
            </div>
        </div>
        <!-- Content -->
        <div v-for="(slot, index) of Object.keys($slots)" class="flex" :key="index">
            <slot
                v-if="!isMobile || activeTab === index"
                :name="slot"
            ></slot>
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
