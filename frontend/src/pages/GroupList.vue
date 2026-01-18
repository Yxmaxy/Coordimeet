<template>
    <div class="bg-main-000">
        <tab-controller :tabs="tabs" :breakpoint="750">
            <template v-slot:groups>
                <div class="flex flex-col mt-2">
                    <div
                        v-for="group in groups"
                        :class="[{
                            'cursor-pointer transition-all hover:-translate-y-1 hover:bg-main-200': isAdmin(group) || isOwner(group),
                        }, 'flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl shadow-md']"
                        @click="() => storeOnline.isOnline && editGroup(group)"
                    >
                        <b class="flex items-center">{{ group.name }}</b>
                        <div
                            v-if="storeOnline.isOnline"
                            class="flex gap-2 items-center"
                        >
                            <custom-button
                                v-if="isOwner(group)"
                                class="h-8 w-8 rounded-full"
                                :click="() => deleteGroup(group)"
                            >
                                <custom-icon icon="delete" />
                            </custom-button>
                            <custom-button
                                v-if="!isOwner(group)"
                                class="h-8 w-8 rounded-full !text-base"
                                :click="() => leaveGroup(group)"
                            >
                                <custom-icon icon="logout" />
                            </custom-button>
                        </div>
                    </div>
                </div>
            </template>
        </tab-controller>
        <custom-button
            v-if="storeOnline.isOnline"
            class="right-4 bottom-4 fixed !p-3 !rounded-2xl shadow-md"
            :click="() => $router.push('/group/new')"
        >
            <custom-icon icon="add"/> New Group
        </custom-button>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useStoreUser } from "@/stores/storeUser";
import { useStoreMessages } from "@/stores/storeMessages";
import { useStoreOnline } from "@/stores/storeOnline";

import { CoordimeetGroup, CoordimeetMemberRole } from "@/types/user";
import { Tab } from "@/types/tabs";

import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

const tabs = [
    {
        name: "Groups",
        slot_name: "groups",
        icon: "groups",
    },
] as Tab[];

export default {
    name: "GroupList",
    components: {
        TabController,
        CustomButton,
        CustomIcon,
    },
    setup() {
        const { user } = useStoreUser();
        const storeMessages = useStoreMessages();
        const storeOnline = useStoreOnline();
        return {
            user,
            tabs,

            storeMessages,
            storeOnline,
        }
    },
    data() {
        return {
            groups: [] as CoordimeetGroup[],
        
        }
    },
    methods: {
        getGroups() {
            ApiService.get<CoordimeetGroup[]>("/users/group/").then((response) => {
                this.groups = response;
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to fetch user's groups.");
            });
        },
        isRole(group: CoordimeetGroup, role: CoordimeetMemberRole) {
            return group.coordimeet_members.find((member) => member.coordimeet_user?.id === this.user?.id)?.role === role;
        },
        isOwner(group: CoordimeetGroup) {
            return this.isRole(group, CoordimeetMemberRole.OWNER);
        },
        isAdmin(group: CoordimeetGroup) {
            return this.isRole(group, CoordimeetMemberRole.ADMIN);
        },
        leaveGroup(group: CoordimeetGroup) {
            ApiService.post(`/users/group/leave/${group.id}/`).then(() => {
                this.storeMessages.showMessage("Successfully left the group.");
                this.getGroups();
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to leave group.");
            });
        },
        deleteGroup(group: CoordimeetGroup) {
            ApiService.delete(`/users/group/delete/${group.id}/`).then(() => {
                this.storeMessages.showMessage("Group successfully deleted.");
                this.getGroups();
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to delete group.");
            });
        },
        editGroup(group: CoordimeetGroup) {
            if (this.isAdmin(group) || this.isOwner(group)) {
                this.$router.push(`/group/edit/${group.id}`);
            }
        }
    },
    mounted() {
        this.getGroups();
    }
}
</script>
