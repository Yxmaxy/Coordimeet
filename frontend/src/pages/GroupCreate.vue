<template>
    <div class="bg-main-000 h-full">
        <tab-controller :tabs="tabs" :breakpoint="750">
            <template v-slot:create_group>
                <div
                    class="flex flex-col gap-4 px-4 pt-4 h-full
                    bg-main-100 min-h-[calc(100vh-7rem)]"
                >
                    <label class="flex flex-col gap-2">
                        <b class="ml-4">Group name</b>
                        <custom-input
                            type="text"
                            v-model="groupName"
                            placeholder="Enter a name for your group"
                        />
                    </label>
                    <custom-button
                        v-if="isEditing"
                        class="mt-3 mb-6"
                        @click="editGroup"
                    >
                        Edit group <custom-icon class="text-base" icon="edit" />
                    </custom-button>
                    <custom-button
                        v-else
                        class="mt-3 mb-6"
                        @click="createGroup"
                    >
                        Create new group <custom-icon class="text-base" icon="group_add" />
                    </custom-button>
                </div>
            </template>
            <template v-slot:members>
                <div
                    class="flex flex-col gap-4 px-4 pt-4 h-full min-h-[calc(100vh-7rem)]"
                >
                    <div class="flex flex-col gap-2">
                        <b class="ml-4 flex gap-2 items-baseline justify-between">
                            Available users

                            <custom-button
                                :small="true"
                                @click="openManageFriends"
                            >
                                Manage available users <custom-icon class="text-base" icon="group_add" />
                            </custom-button>
                        </b>
                        <div>
                            <custom-select
                                v-model="userSearch"
                                :options="displayedAvailableUsers"
                                @confirmedOption="addMember"
                            />
                        </div>
                    </div>

                    <div class="flex flex-col gap-4">
                        <div
                            v-for="member in members"
                            class="flex justify-between items-center bg-main-100 px-6 py-4 rounded-2xl shadow-md"
                        >
                            <div class="flex gap-1 items-center">
                                <b class="flex items-center h-8">{{ member.coordimeet_user?.email }}</b>
                            </div>    
                            <div class="flex gap-2">
                                <div class="flex items-center gap-1 ml-1" v-if="member.role === CoordimeetMemberRole.OWNER">
                                    Owner <custom-icon icon="shield_person" class="text-base" />
                                </div>
                                <custom-toggle
                                    v-if="isCurrentUserOwner && member.coordimeet_user?.id !== user?.id"
                                    v-model="member.role"
                                    :leftValue="CoordimeetMemberRole.MEMBER"
                                    :rightValue="CoordimeetMemberRole.ADMIN"
                                >
                                    <template v-slot:left>
                                        <div class="flex items-center gap-1 mr-1">
                                            Member <custom-icon icon="person" class="text-base" />
                                        </div>
                                    </template>
                                    <template v-slot:right>
                                        <div class="flex items-center gap-1 ml-1">
                                            Admin <custom-icon icon="supervisor_account" class="text-base" />
                                        </div>
                                    </template>
                                </custom-toggle>
                                <custom-button
                                    v-if="member.role !== CoordimeetMemberRole.OWNER && member.coordimeet_user?.id !== user?.id"
                                    class="h-8 w-8 rounded-full"
                                    :click="() => deleteMember(member)"
                                >
                                    <custom-icon icon="delete" />
                                </custom-button>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </tab-controller>
    </div>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import { useStoreUser } from "@/stores/storeUser";
import { useStoreMessages } from "@/stores/storeMessages";

import { Tab } from "@/types/tabs";
import {
    User,
    CoordimeetMember,
    CoordimeetGroup,
    CoordimeetMemberRole,
} from "@/types/user";
import { SelectOption } from "@/types/ui";

import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomInput from "@/components/ui/CustomInput.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import CustomSelect from "@/components/ui/CustomSelect.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

const tabs = [
    {
        name: "Group information",
        slot_name: "create_group",
        narrow: "md",
        icon: "groups",
    },
    {
        name: "Group members",
        slot_name: "members",
        icon: "manage_accounts",
    },
] as Tab[];

export default {
    name: "GroupList",
    components: {
        TabController,
        CustomButton,
        CustomInput,
        CustomToggle,
        CustomIcon,
        HelpIcon,
        CustomSelect,
    },
    setup() {
        const { user } = useStoreUser();
        const storeMessages = useStoreMessages();
        return {
            user,
            tabs,
            CoordimeetMemberRole,
            storeMessages,
        }
    },
    data() {
        return {
            groupName: "",
            
            memberForceInvalidMessage: false,
            memberInvalidMessage: "",
            members: [] as CoordimeetMember[],

            userSearch: "",
            availableUsers: [] as SelectOption<User>[],
        }
    },
    computed: {
        isEditing() {
            return this.$route.params.id !== undefined;
        },
        isCurrentUserOwner() {
            return this.members.find((member) => member.coordimeet_user?.id === this.user?.id)?.role === CoordimeetMemberRole.OWNER;
        },
        // available users
        displayedAvailableUsers() {
            return this.availableUsers
                .filter(user => !this.members.some(member =>
                    member.coordimeet_user?.user === user.value.id ||    
                    member.coordimeet_user?.user.id === user.value.id
                ));
        },
    },
    methods: {
        // available users
        getAvailableUsers() {
            ApiService.get<User[]>(`/friends/list/`).then((response) => {
                this.availableUsers = response.map(user => ({
                    value: user,
                    text: user.email,
                }));
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to fetch available users");
            });
        },
        openManageFriends() {
            window.location.href = import.meta.env.VITE_FRIENDS_MANAGE_URL;
        },

        // group
        getGroup() {
            ApiService.get<CoordimeetGroup>(`/users/group/${this.$route.params.id}/`).then((response) => {
                this.groupName = response.name;
                this.members = response.coordimeet_members.map((member: CoordimeetMember) => ({
                    ...member,
                }));
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to fetch group information");
            });
        },
        validateData() {
            if (this.groupName.length === 0) {
                this.storeMessages.showMessageError("You must enter a group name");
                return false;
            }
            return true;
        },
        createGroup() {
            if (!this.validateData())
                return;

            const data = {
                name: this.groupName,
                coordimeet_members: this.members.map((member: CoordimeetMember) => ({
                    coordimeet_user: member.coordimeet_user,
                    role: member.role,
                })),
            } as CoordimeetGroup;

            ApiService.post("/users/group/", data)
                .then(() => {
                    this.storeMessages.showMessage("Group created successfully");
                    this.$router.push("/group/list");
                }).catch(() => {
                    this.storeMessages.showMessageError("Failed to create group");
                });
        },
        editGroup() {
            if (!this.validateData())
                return;

            const data = {
                name: this.groupName,
                coordimeet_members: this.members,
            } as CoordimeetGroup;

            ApiService.put(`/users/group/${this.$route.params.id}/`, data)
                .then(() => {
                    this.storeMessages.showMessage("Group updated successfully");
                    this.$router.push("/group/list");
                }).catch(() => {
                    this.storeMessages.showMessageError("Failed to update group");
                });
        },
        addMember(option: SelectOption<User>) {
            this.members.push({
                role: CoordimeetMemberRole.MEMBER,
                coordimeet_user: {
                    user: option.value?.id,  // ID instead of User!
                    email: option.value?.email,
                },
            } as any);
            this.userSearch = "";
        },
        deleteMember(member: CoordimeetMember) {
            this.members = this.members.filter(m => m !== member);
        },
    },
    mounted() {
        this.getAvailableUsers();
        if (this.isEditing) {
            this.getGroup();
        }
    },
}
</script>
