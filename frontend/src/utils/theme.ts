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

export function updateAppTheme() {
    const root = document.querySelector(":root") as HTMLElement;
    root.dataset.theme = getTheme();
}
