const ACCESS_TOKEN = "accessToken";
const USER_ID = "userID";
const DB_NAME = "tokenDatabase";
const STORE_NAME = "tokens";

function openDatabase(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME);
        request.onupgradeneeded = function() {
            const db = request.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME);
            }
        };
        request.onsuccess = function() {
            resolve(request.result);
        };
        request.onerror = function() {
            reject(request.error);
        };
    });
}

async function getFromDB(key: string): Promise<string|number|null> {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME);
        const store = transaction.objectStore(STORE_NAME);
        const request = store.get(key);
        request.onsuccess = function() {
            resolve(request.result);
        };
        request.onerror = function() {
            reject(request.error);
        };
    });
}

async function saveToDB(key: string, value: string|number) {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readwrite");
        const store = transaction.objectStore(STORE_NAME);
        const request = store.put(value, key);
        request.onsuccess = function() {
            resolve(request.result);
        };
        request.onerror = function() {
            reject(request.error);
        };
    });
}

async function removeFromDB(key: string) {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readwrite");
        const store = transaction.objectStore(STORE_NAME);
        const request = store.delete(key);
        request.onsuccess = function() {
            resolve(request.result);
        };
        request.onerror = function() {
            reject(request.error);
        };
    });
}

export async function saveTokens(accessToken: string, userID: number) {
    await saveToDB(ACCESS_TOKEN, accessToken);
    await saveToDB(USER_ID, userID.toString());
}

export async function retrieveAccessToken(): Promise<string|null> {
    const token = await getFromDB(ACCESS_TOKEN);
    return token ? token.toString() : null;
}

export async function retrieveUserID(): Promise<number|null> {
    const id = await getFromDB(USER_ID);
    return id ? parseInt(id.toString()) : null;
}

export async function removeTokens() {
    await removeFromDB(ACCESS_TOKEN);
    await removeFromDB(USER_ID);
}
