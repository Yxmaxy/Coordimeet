<template>
    <div>
        <div class="flex">
            <div
                v-for="(tab, index) in tabs" :key="index"
                :class="[{
                    'bg-main-400 text-main-100': activeTab !== index,
                    'bg-main-200 text-main-700': activeTab === index,
                }, 'flex-1 text-center py-2 cursor-pointer transition-colors select-none border-r-2 border-main-200']"
                @click="activeTab = index"
            >
                {{ tab.name }}
            </div>
        </div>
        <div class="flex">
            <div
                v-if="showAllTabs"
                v-for="(tab, index) in tabs" :key="index"
                class="flex-1"
            >
                <slot :tab="tab" name="tab"></slot>
            </div>
            <div v-else class="flex-1">
                <slot :tab="tabs[activeTab]" name="tab"></slot>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
export default {
    name: "TabController",
    props: {
        tabs: {
            type: Array as any,
            required: true,
        },
        showAllTabs: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            activeTab: 0 as number,
        }
    },
}
</script>
