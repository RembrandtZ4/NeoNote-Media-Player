/* neonote-splash.exe – Startfenster des NeoNote-Installers, während die Programmdateien entpackt werden.
   Zeigt ein vorgerendertes Bild (make_splash.py) als halbtransparentes Fenster mit laufendem Fortschrittsbalken.
   Schließt sich, sobald das Qt-Setup-Fenster von NeoNote sichtbar ist, bei WM_CLOSE oder nach 3 Minuten. */
#include <windows.h>
#include <math.h>

typedef struct { int w, h, bx, by, bw, bh, scale; } Head;
static Head hd;
static const BYTE *base;
static BYTE *bits;
static HDC memdc;
static HWND hwnd;
static DWORD t0;
static int closing = 0;
static DWORD tclose = 0;
static int found_setup = 0;

static BOOL CALLBACK find_qt(HWND w, LPARAM lp) {
    char cls[64], title[256];
    if (w == hwnd || !IsWindowVisible(w)) return TRUE;
    GetClassNameA(w, cls, sizeof cls);
    if (strncmp(cls, "Qt", 2) != 0) return TRUE;
    GetWindowTextA(w, title, sizeof title);
    if (strstr(title, "NeoNote")) { *(int *)lp = 1; return FALSE; }
    return TRUE;
}

static void draw(void) {
    DWORD now = GetTickCount() - t0;
    memcpy(bits, base, (size_t)hd.w * hd.h * 4);
    /* unbestimmter Fortschritt: ein Lichtstreifen gleitet durch die Spur */
    double period = 1700.0, ph = fmod(now, period) / period;
    double e = ph < 0.5 ? 2 * ph * ph : 1 - pow(-2 * ph + 2, 2) / 2;      /* weich beschleunigen und bremsen */
    double seg = hd.bw * 0.34, cx = -seg + e * (hd.bw + seg);
    for (int y = hd.by; y < hd.by + hd.bh && y < hd.h; y++) {
        double ry = hd.bh > 1 ? fabs((y - hd.by) - (hd.bh - 1) / 2.0) / (hd.bh / 2.0) : 0;
        double ay = ry > 0.75 ? (1 - ry) * 4 : 1;                           /* runde Kanten oben/unten */
        for (int x = 0; x < hd.bw; x++) {
            double d = (x - cx) / seg;                                       /* 0..1 innerhalb des Streifens */
            if (d < 0 || d > 1) continue;
            double a = sin(d * 3.14159265) * ay;                             /* weiche Enden */
            if (a <= 0) continue;
            BYTE *px = bits + ((size_t)y * hd.w + hd.bx + x) * 4;
            double A = a * 0.95;
            /* Akzentfarbe #3d8fe0 über die Spur legen (vormultipliert, B G R A) */
            px[0] = (BYTE)(224 * A + px[0] * (1 - A));
            px[1] = (BYTE)(143 * A + px[1] * (1 - A));
            px[2] = (BYTE)(61 * A + px[2] * (1 - A));
            px[3] = (BYTE)(255 * A + px[3] * (1 - A));
        }
    }
    int alpha = now < 260 ? (int)(255 * now / 260.0) : 255;
    if (closing) {
        DWORD dt = GetTickCount() - tclose;
        alpha = dt >= 200 ? 0 : (int)(alpha * (1 - dt / 200.0));
    }
    BLENDFUNCTION bf = {AC_SRC_OVER, 0, (BYTE)alpha, AC_SRC_ALPHA};
    POINT zero = {0, 0};
    SIZE sz = {hd.w, hd.h};
    UpdateLayeredWindow(hwnd, NULL, NULL, &sz, memdc, &zero, 0, &bf, ULW_ALPHA);
}

static LRESULT CALLBACK proc(HWND w, UINT m, WPARAM wp, LPARAM lp) {
    switch (m) {
    case WM_TIMER: {
        DWORD now = GetTickCount() - t0;
        if (!closing) {
            int f = 0;
            if (now > 400 && (now / 200) % 2 == 0) EnumWindows(find_qt, (LPARAM)&f);
            if (f || now > 180000) { closing = 1; tclose = GetTickCount(); }
        }
        draw();
        if (closing && GetTickCount() - tclose >= 220) DestroyWindow(w);
        return 0;
    }
    case WM_CLOSE:
        if (!closing) { closing = 1; tclose = GetTickCount(); }
        return 0;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    case WM_NCHITTEST:
        return HTCAPTION;                                                    /* lässt sich verschieben */
    }
    return DefWindowProcW(w, m, wp, lp);
}

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, PWSTR cmd, int show) {
    (void)prev; (void)cmd; (void)show;
    SetProcessDPIAware();
    HDC sdc = GetDC(NULL);
    int dpi = GetDeviceCaps(sdc, LOGPIXELSX);
    ReleaseDC(NULL, sdc);
    int want = dpi * 100 / 96, scales[4] = {100, 125, 150, 200}, pick = 0;
    for (int i = 0; i < 4; i++)
        if (abs(scales[i] - want) < abs(scales[pick] - want)) pick = i;
    int german = PRIMARYLANGID(GetUserDefaultUILanguage()) == LANG_GERMAN;
    HRSRC r = FindResourceW(inst, MAKEINTRESOURCEW(101 + (german ? 0 : 4) + pick), (LPCWSTR)RT_RCDATA);
    if (!r) return 1;
    const BYTE *res = LockResource(LoadResource(inst, r));
    memcpy(&hd, res, sizeof hd);
    base = res + sizeof hd;

    WNDCLASSW wc = {0};
    wc.lpfnWndProc = proc; wc.hInstance = inst; wc.lpszClassName = L"NeoNoteSplash";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hIcon = LoadIcon(inst, MAKEINTRESOURCE(1));
    RegisterClassW(&wc);
    /* mittig auf dem Bildschirm mit dem Mauszeiger (Arbeitsbereich ohne Taskleiste) */
    POINT cp; GetCursorPos(&cp);
    MONITORINFO mi = {sizeof mi};
    GetMonitorInfoW(MonitorFromPoint(cp, MONITOR_DEFAULTTOPRIMARY), &mi);
    int x = (mi.rcWork.left + mi.rcWork.right - hd.w) / 2, y = (mi.rcWork.top + mi.rcWork.bottom - hd.h) / 2;
    hwnd = CreateWindowExW(WS_EX_LAYERED | WS_EX_TOOLWINDOW, L"NeoNoteSplash", L"NeoNote Setup",
                           WS_POPUP, x, y, hd.w, hd.h, NULL, NULL, inst, NULL);
    BITMAPINFO bi = {0};
    bi.bmiHeader.biSize = sizeof bi.bmiHeader; bi.bmiHeader.biWidth = hd.w; bi.bmiHeader.biHeight = -hd.h;
    bi.bmiHeader.biPlanes = 1; bi.bmiHeader.biBitCount = 32; bi.bmiHeader.biCompression = BI_RGB;
    memdc = CreateCompatibleDC(NULL);
    HBITMAP bmp = CreateDIBSection(memdc, &bi, DIB_RGB_COLORS, (void **)&bits, NULL, 0);
    SelectObject(memdc, bmp);
    t0 = GetTickCount();
    POINT pos = {x, y};
    BLENDFUNCTION bf = {AC_SRC_OVER, 0, 0, AC_SRC_ALPHA};
    POINT zero = {0, 0};
    SIZE sz = {hd.w, hd.h};
    memcpy(bits, base, (size_t)hd.w * hd.h * 4);
    UpdateLayeredWindow(hwnd, NULL, &pos, &sz, memdc, &zero, 0, &bf, ULW_ALPHA);
    ShowWindow(hwnd, SW_SHOWNOACTIVATE);
    SetTimer(hwnd, 1, 16, NULL);
    MSG msg;
    while (GetMessageW(&msg, NULL, 0, 0) > 0) { TranslateMessage(&msg); DispatchMessageW(&msg); }
    return 0;
}
