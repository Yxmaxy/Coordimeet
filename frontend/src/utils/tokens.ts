const ACCESS_TOKEN = "accessToken";
const USER_ID = "userID";

export function saveTokens(accessToken: string, userID: number) {
    localStorage.setItem(ACCESS_TOKEN, accessToken);
    localStorage.setItem(USER_ID, userID.toString());
}

export function retrieveAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN);
}

export function retrieveUserID(): number | null {
    const item = localStorage.getItem(USER_ID);
    return item ? parseInt(item) : null;
}

export function removeTokens() {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(USER_ID);
}
