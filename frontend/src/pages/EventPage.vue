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
            <div>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Ut sint aliquam fugit esse beatae, earum quas fugiat qui. Minus quae distinctio corrupti assumenda harum quod ab, perferendis id amet saepe?</div>
            <calendar
                :dateRange="dateRange"
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
                from: new Date("12-7-2022"),
                to: new Date("12-23-2022")
            } as IDateRange
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