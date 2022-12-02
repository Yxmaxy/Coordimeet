<template>
    <div class="wrapper">
        <aside>
            <div>
                <h2>Event name</h2>
                <p>Lorem ipsum dolor sit amet consectetur, adipisicing elit. Officia beatae exercitationem.</p>
            </div>
            <div>
                Responses
            </div>
        </aside>
        <main>
            <label>
                Select unavailable dates
                <input v-model="selectUnavailable" type="checkbox" />
            </label>
            <calendar
                :dateRange="dateRange"
                :selectUnavailable="selectUnavailable"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { IDateRange } from '../common/interfaces';

export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            dateRange: {
                from: new Date(2022, 11, 11),
                to: new Date(2022, 11, 19)
            } as IDateRange,
            selectUnavailable: false,
        }
    }
}
</script>

<style lang="scss" scoped>
.wrapper {
    flex: 1;
    display: flex;
    flex-direction: row;
}
aside {
    flex: 1;
}
main {
    flex: 3;
    display: flex;
    flex-direction: column;
}
</style>