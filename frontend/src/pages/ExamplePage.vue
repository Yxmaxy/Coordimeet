<template>
    <div class="page">
        <calendar />
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';

export default {
    components: {
        "calendar": Calendar,
    }
}
</script>
