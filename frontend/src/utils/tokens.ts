const ACCESS_TOKEN = "accessToken";
const REFRESH_TOKEN = "refreshToken";
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

export async function saveTokens(accessToken: string, refreshToken: string) {
    await saveToDB(ACCESS_TOKEN, accessToken);
    await saveToDB(REFRESH_TOKEN, refreshToken);
}

export async function saveAccessToken(accessToken: string) {
    await saveToDB(ACCESS_TOKEN, accessToken);
}

export async function retrieveTokens(): Promise<{accessToken: string|null, refreshToken: string|null}> {
    const accessToken = await getFromDB(ACCESS_TOKEN) as string|null;
    const refreshToken = await getFromDB(REFRESH_TOKEN)as string|null;
    return { accessToken, refreshToken };
}

export async function removeTokens() {
    await removeFromDB(ACCESS_TOKEN);
    await removeFromDB(REFRESH_TOKEN);
}
