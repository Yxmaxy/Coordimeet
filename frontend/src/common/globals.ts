export const developmentMode = process.env.NODE_ENV === "development";
export const apiServer = developmentMode ? "http://127.0.0.1:8080" : "https://coordimeet.eu/backend";
export const eventServer = developmentMode ? "http://127.0.0.1:3000/#/event" : "https://coordimeet.eu/#/event";
