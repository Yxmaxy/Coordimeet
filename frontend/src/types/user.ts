export interface User {
    id?: number,
    email: string,
    first_name?: string,
    last_name?: string,
}

export interface Group {
    id?: number,
    name: string,
    members: Member[],
}

export enum Role {
    ADMIN = 1,
    MEMBER = 2,
    OWNER = 3,
}

export interface Member {
    id?: number,
    role: Role,
    user?: User,
}
