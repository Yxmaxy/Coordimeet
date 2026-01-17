export interface User {
    id?: number,
    email: string,
}

export interface CoordimeetUser {
    id?: number,
    user: User | number,
    email: string,
    is_anonymous?: boolean,
}

export interface CoordimeetGroup {
    id?: number,
    name: string,
    coordimeet_members: CoordimeetMember[],
}

export enum CoordimeetMemberRole {
    ADMIN = 1,
    MEMBER = 2,
    OWNER = 3,
}

export interface CoordimeetMember {
    id?: number,
    role: CoordimeetMemberRole,
    coordimeet_user?: CoordimeetUser,
}
