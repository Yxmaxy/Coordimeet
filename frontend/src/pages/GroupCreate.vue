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
                    <label class="flex flex-col gap-2">
                        <b class="ml-4 flex gap-2 items-center">
                            Member's email
                            <help-icon class="text-base font-normal">
                                Enter the email address of a member you want to add to the group.
                                If the account does not yet exist, the user will be added to the group when they create an account.
                                <br /><br />
                                You can send them the following link to create an account:
                                <div
                                    class="cursor-pointer font-mono"
                                    @click="copyInviteLink"
                                >
                                    {{ inviteLink }}
                                </div>
                            </help-icon>
                        </b>
                        <div class="flex gap-2">
                            <custom-input
                                type="email"
                                v-model="memberEmail"
                                placeholder="Enter a member's email address"
                                :forceInvalidMessage="memberForceInvalidMessage"
                                :invalidMessage="memberInvalidMessage"
                                @keydown.enter="addMember"
                                @input="memberForceInvalidMessage = false"
                            />
                            <custom-button
                                class="h-11 rounded-xl"
                                :click="addMember"
                            >
                                <custom-icon icon="add" />
                            </custom-button>
                        </div>
                    </label>

                    <div class="flex flex-col gap-4">
                        <div
                            v-for="member in members"
                            class="flex justify-between items-center bg-main-100 px-6 py-4 rounded-2xl shadow-md"
                        >
                            <div class="flex gap-1 items-center">
                                <b class="flex items-center h-8">{{ member.user?.email }}</b>
                                <help-icon class="text-base font-normal text-main-700" icon="info">
                                    This user doesn't exist yet.
                                    <br /><br />
                                    You can send them the following link to create an account:
                                    <div
                                        class="cursor-pointer font-mono"
                                        @click="copyInviteLink"
                                    >
                                        {{ inviteLink }}
                                    </div>
                                </help-icon>
                            </div>    
                            <div class="flex gap-2">
                                <div class="flex items-center gap-1 ml-1" v-if="member.role === Role.OWNER">
                                    Owner <custom-icon icon="shield_person" class="text-base" />
                                </div>
                                <custom-toggle
                                    v-else
                                    v-model="member.role"
                                    :leftValue="Role.MEMBER"
                                    :rightValue="Role.ADMIN"
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
                                    v-if="member.role !== Role.OWNER"
                                    class="h-8 w-8 rounded-full"
                                    :click="() => deleteMember(member)"
                                >
                                    <custom-icon icon="delete" />
                                </custom-button>
                                <custom-button
                                    v-if="!member.id"
                                    class="h-8 w-8 rounded-full !text-base"
                                    :click="() => editMember(member)"
                                >
                                    <custom-icon icon="edit" />
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
import { Member, Group, Role } from "@/types/user";

import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomInput from "@/components/ui/CustomInput.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

interface MemberCreate extends Member {
    exists: boolean;
}

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
    },
    setup() {
        const { user } = useStoreUser();
        const storeMessages = useStoreMessages();
        return {
            user,
            tabs,
            Role,
            storeMessages,
            inviteLink: `${import.meta.env.VITE_FRONTEND_URL}/register`,
        }
    },
    data() {
        return {
            groupName: "",
            
            memberEmail: "",
            memberForceInvalidMessage: false,
            memberInvalidMessage: "",

            members: [] as MemberCreate[],
        }
    },
    computed: {
        isEditing() {
            return this.$route.params.id !== undefined;
        },
    },
    methods: {
        getGroup() {
            ApiService.get(`/users/group/${this.$route.params.id}/`).then((response) => {
                this.groupName = response.data.name;
                this.members = response.data.members;
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
                members: this.members,
            } as Group;

            ApiService.post("/users/group/", data).then((response) => {
                if (response.status !== 201)
                    throw new Error("Failed to create group");
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
                members: this.members,
            } as Group;

            ApiService.put(`/users/group/${this.$route.params.id}/`, data).then((response) => {
                if (response.status !== 200)
                    throw new Error("Failed to update group");
                this.storeMessages.showMessage("Group updated successfully");
                this.$router.push("/group/list");
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to update group");
            });
        },
        addMember() {
            // // check email format
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.memberEmail)) {
                this.memberForceInvalidMessage = true;
                this.memberInvalidMessage = "Invalid email format";
                return;
            }

            // check duplicates
            if (this.members.some(m => m.user?.email === this.memberEmail)) {
                this.memberForceInvalidMessage = true;
                this.memberInvalidMessage = "This member is already added";
                return;
            }

            this.memberForceInvalidMessage = false;
            this.memberInvalidMessage = "";

            ApiService.get(`/users/user/exists/${this.memberEmail}/`).then((response: any) => {
                this.members.push({
                    user: {
                        email: this.memberEmail,
                    },
                    role: Role.MEMBER,
                    exists: response.data.exists,
                });
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to add user to group");
            }).finally(() => {
                this.memberEmail = "";
            });
        },
        deleteMember(member: MemberCreate) {
            this.members = this.members.filter(m => m !== member);
        },
        editMember(member: MemberCreate) {
            this.memberEmail = member.user?.email?.toString() || "";
            this.deleteMember(member);
        },
        async copyInviteLink() {
            navigator.clipboard.writeText(this.inviteLink);
            this.storeMessages.showMessage("Invite link copied to clipboard", 3000);
        }
    },
    mounted() {
        if (this.isEditing) {
            this.getGroup();
        }
    },
}
</script>
