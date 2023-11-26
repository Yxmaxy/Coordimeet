export enum Theme {
    BLUE = "blue",
    GREEN = "green",
    DARK = "dark",
    PINK = "pink",
}

function getTheme(): Theme {
    const theme = localStorage.getItem('theme') as Theme;
    return theme || Theme.BLUE;
}

export function setTheme(theme: Theme) {
    localStorage.setItem('theme', theme);
    updateAppTheme();
}

function updateMetaTheme() {
    const meta = document.querySelector('meta[name="theme-color"]') as HTMLElement;
    const color = getComputedStyle(meta).getPropertyValue("--main-200");
    meta.setAttribute("content", color);
}

export function updateAppTheme() {
    const root = document.querySelector(":root") as HTMLElement;
    root.dataset.theme = getTheme();

    updateMetaTheme();
}
