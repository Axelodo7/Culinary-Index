"""
gui_compat.py - GUI compatibility layer for The Culinary Index.
Desktop: CustomTkinter (dark theme, modern widgets).
Android/Pydroid 3: Standard tkinter with manual dark palette.
"""

import platform
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
ANDROID = platform.system() == "Linux" and "android" in platform.platform().lower()

try:
    import android  # Pydroid 3 exposes this module
    ANDROID = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Desktop: try CustomTkinter
# ---------------------------------------------------------------------------
USE_CTK = False
ctk = None

if not ANDROID:
    try:
        import customtkinter as ctk
        USE_CTK = True
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Dark palette
# ---------------------------------------------------------------------------
BG_DARK = "#1e1e2e"
BG_CARD = "#2b2b3d"
BG_INPUT = "#3a3a4d"
BORDER_COLOR = "#4a4a5d"
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#888888"
TEXT_DIM = "#5a6a7a"
ACCENT = "#4a6fa5"
ACCENT_HOVER = "#5a8fc5"
ACCENT_ACTIVE = "#3a5f95"
DANGER = "#666666"
DANGER_HOVER = "#888888"
GREEN = "#4CAF50"
RED = "#F44336"
ENTRY_BG = "#333345"

DARK_FONT = ("Segoe UI", 11)
DARK_FONT_BOLD = ("Segoe UI", 11, "bold")
DARK_FONT_SM = ("Segoe UI", 10)
DARK_FONT_LG = ("Segoe UI", 16, "bold")
DARK_FONT_TITLE = ("Segoe UI", 22, "bold")


# ===================================================================
# StringVar / BooleanVar  (identical API)
# ===================================================================
StringVar = tk.StringVar
BooleanVar = tk.BooleanVar


# ===================================================================
# Root window
# ===================================================================
class AppRoot(tk.Tk if not USE_CTK else ctk.CTk):
    """Main application window."""
    pass


# ===================================================================
# Frame
# ===================================================================
if USE_CTK:
    class AppFrame(ctk.CTkFrame):
        pass
else:
    class AppFrame(tk.Frame):
        def __init__(self, master, fg_color=None, corner_radius=None,
                     border_width=0, border_color=None, height=None, **kw):
            kw.pop("fg_color", None)
            kw.pop("corner_radius", None)
            bg = kw.pop("bg", BG_CARD if border_width else BG_DARK)
            if border_width and border_color:
                kw["highlightthickness"] = border_width
                kw["highlightbackground"] = border_color
            if height:
                kw["height"] = height
            super().__init__(master, bg=bg, **kw)


# ===================================================================
# Label
# ===================================================================
if USE_CTK:
    class AppLabel(ctk.CTkLabel):
        pass
else:
    class AppLabel(tk.Label):
        def __init__(self, master, text_color=None, font=None, anchor="w", **kw):
            kw.pop("text_color", None)
            fg = text_color or TEXT_PRIMARY
            f = _resolve_font(font)
            super().__init__(master, fg=fg, font=f, anchor=anchor,
                             bg=BG_DARK, **kw)

        def configure(self, cnf=None, **kw):
            if "text_color" in kw:
                kw["fg"] = kw.pop("text_color")
            if "font" in kw:
                kw["font"] = _resolve_font(kw["font"])
            return super().configure(cnf, **kw)


# ===================================================================
# Entry
# ===================================================================
if USE_CTK:
    class AppEntry(ctk.CTkEntry):
        pass
else:
    class AppEntry(tk.Entry):
        def __init__(self, master, placeholder_text=None, corner_radius=None, **kw):
            kw.pop("placeholder_text", None)
            kw.pop("corner_radius", None)
            self._placeholder = placeholder_text
            self._has_placeholder = False
            sv = kw.get("textvariable")
            super().__init__(master, bg=ENTRY_BG, fg=TEXT_PRIMARY,
                             insertbackground=TEXT_PRIMARY,
                             relief="flat", font=DARK_FONT,
                             highlightthickness=1,
                             highlightbackground=BORDER_COLOR,
                             highlightcolor=ACCENT, **kw)
            if self._placeholder:
                self._show_ph()
                self.bind("<FocusIn>", self._focus_in)
                self.bind("<FocusOut>", self._focus_out)

        def _show_ph(self):
            if not self.get():
                self._has_placeholder = True
                self.insert(0, self._placeholder)
                self.configure(fg=TEXT_SECONDARY)

        def _focus_in(self, _):
            if self._has_placeholder:
                self.delete(0, tk.END)
                self.configure(fg=TEXT_PRIMARY)
                self._has_placeholder = False

        def _focus_out(self, _):
            self._show_ph()


# ===================================================================
# Button
# ===================================================================
if USE_CTK:
    class AppButton(ctk.CTkButton):
        pass
else:
    class AppButton(tk.Button):
        def __init__(self, master, fg_color=ACCENT, hover_color=None,
                     corner_radius=None, **kw):
            kw.pop("hover_color", None)
            kw.pop("corner_radius", None)
            kw.pop("width", None)  # tk uses char width, ignore px
            super().__init__(master, bg=fg_color, fg="white",
                             activebackground=ACCENT_HOVER,
                             activeforeground="white",
                             relief="flat", font=DARK_FONT_BOLD,
                             cursor="hand2", **kw)


# ===================================================================
# Checkbutton
# ===================================================================
if USE_CTK:
    class AppCheckBox(ctk.CTkCheckBox):
        pass
else:
    class AppCheckBox(tk.Checkbutton):
        def __init__(self, master, checkbox_width=None, checkbox_height=None, **kw):
            kw.pop("checkbox_width", None)
            kw.pop("checkbox_height", None)
            super().__init__(master, bg=BG_DARK, fg=TEXT_PRIMARY,
                             selectcolor=BG_INPUT,
                             activebackground=BG_DARK,
                             activeforeground=TEXT_PRIMARY,
                             font=DARK_FONT, **kw)


# ===================================================================
# Radiobutton
# ===================================================================
if USE_CTK:
    class AppRadioButton(ctk.CTkRadioButton):
        pass
else:
    class AppRadioButton(tk.Radiobutton):
        def __init__(self, master, **kw):
            super().__init__(master, bg=BG_DARK, fg=TEXT_PRIMARY,
                             selectcolor=BG_INPUT,
                             activebackground=BG_DARK,
                             activeforeground=TEXT_PRIMARY,
                             font=DARK_FONT, **kw)


# ===================================================================
# Textbox (multi-line)
# ===================================================================
if USE_CTK:
    class AppTextbox(ctk.CTkTextbox):
        pass
else:
    class AppTextbox(tk.Text):
        def __init__(self, master, corner_radius=None, font=None, **kw):
            kw.pop("corner_radius", None)
            f = _resolve_font(font)
            super().__init__(master, bg=ENTRY_BG, fg=TEXT_PRIMARY,
                             insertbackground=TEXT_PRIMARY,
                             relief="flat", font=f,
                             highlightthickness=1,
                             highlightbackground=BORDER_COLOR,
                             wrap="none", **kw)


# ===================================================================
# Progress bar
# ===================================================================
if USE_CTK:
    class AppProgressBar(ctk.CTkProgressBar):
        pass
else:
    class AppProgressBar(ttk.Progressbar):
        def __init__(self, master, **kw):
            super().__init__(master, mode="determinate", **kw)

        def set(self, val):
            self["value"] = val * 100

        def configure(self, cnf=None, **kw):
            if "mode" in kw:
                kw["mode"] = kw["mode"]
            return super().configure(cnf, **kw)

        def start(self, interval=None):
            self.configure(mode="indeterminate")
            super().start(interval or 50)

        def stop(self):
            super().stop()
            self.configure(mode="determinate")
            self["value"] = 0


# ===================================================================
# Scrollable frame
# ===================================================================
if USE_CTK:
    AppScrollableFrame = ctk.CTkScrollableFrame
else:
    class AppScrollableFrame(tk.Frame):
        def __init__(self, master, **kw):
            kw.pop("corner_radius", None)
            kw.pop("fg_color", None)
            super().__init__(master, bg=BG_DARK)

            self._canvas = tk.Canvas(self, bg=BG_DARK,
                                     highlightthickness=0)
            self._vsb = ttk.Scrollbar(self, orient="vertical",
                                       command=self._canvas.yview)
            self._inner = tk.Frame(self._canvas, bg=BG_DARK)

            self._inner.bind("<Configure>",
                             lambda e: self._canvas.configure(
                                 scrollregion=self._canvas.bbox("all")))
            self._win = self._canvas.create_window(
                (0, 0), window=self._inner, anchor="nw")
            self._canvas.configure(yscrollcommand=self._vsb.set)

            self._vsb.pack(side="right", fill="y")
            self._canvas.pack(side="left", fill="both", expand=True)

            self._canvas.bind("<Configure>", self._resize_inner)

            # Mouse-wheel (desktop)
            self._inner.bind("<Enter>",
                             lambda e: self._canvas.bind_all(
                                 "<MouseWheel>", self._on_wheel))
            self._inner.bind("<Leave>",
                             lambda e: self._canvas.unbind_all("<MouseWheel>"))

        def _resize_inner(self, event):
            self._canvas.itemconfig(self._win, width=event.width)

        def _on_wheel(self, event):
            self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def grid_columnconfigure(self, col, **kw):
            self._inner.grid_columnconfigure(col, **kw)

        # Children are placed inside the inner frame
        def _get_child_master(self):
            return self._inner


# ===================================================================
# Tab view
# ===================================================================
if USE_CTK:
    AppTabView = ctk.CTkTabview
else:
    class AppTabView(ttk.Notebook):
        def __init__(self, master, corner_radius=None, **kw):
            kw.pop("corner_radius", None)
            super().__init__(master, **kw)
            self._tabs = {}

        def add(self, name):
            frame = tk.Frame(self, bg=BG_DARK)
            self.add(frame, text=name)
            self._tabs[name] = frame
            return frame

        # Override to match CTkTabview naming
        def _add_tab(self, name):
            frame = tk.Frame(self, bg=BG_DARK)
            ttk.Notebook.add(self, frame, text=name)
            self._tabs[name] = frame
            return frame

        # Expose same API as CTkTabview
        def __getattr__(self, name):
            if name in self._tabs:
                return self._tabs[name]
            raise AttributeError(name)


# ===================================================================
# Toplevel (dialog)
# ===================================================================
if USE_CTK:
    AppToplevel = ctk.CTkToplevel
else:
    class AppToplevel(tk.Toplevel):
        pass


# ===================================================================
# Helpers
# ===================================================================
def _resolve_font(font):
    """Convert CTkFont or size tuple to tkinter font tuple."""
    if font is None:
        return DARK_FONT
    if isinstance(font, (tuple, list)):
        if len(font) == 1:
            return ("Segoe UI", font[0])
        if len(font) == 2:
            if font[1] == "bold":
                return ("Segoe UI", font[0], "bold")
            return ("Segoe UI", font[0], font[1])
        return tuple(font)
    if isinstance(font, dict):
        size = font.get("size", 11)
        weight = font.get("weight", "normal")
        family = font.get("family", "Segoe UI")
        if weight == "bold":
            return (family, size, "bold")
        return (family, size)
    # CTkFont object
    try:
        return font.cget("family"), font.cget("size")
    except Exception:
        return DARK_FONT


def apply_dark_theme(root):
    """Apply dark ttk theme on Android fallback."""
    if USE_CTK:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        return
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TProgressbar", troughcolor=BG_INPUT,
                     background=ACCENT, thickness=10)
    style.configure("TNotebook", background=BG_DARK)
    style.configure("TNotebook.Tab", background=BG_CARD,
                     foreground=TEXT_PRIMARY, padding=[10, 4])
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])


def app_geometry(root, geom):
    """Set window geometry (no-op on Android)."""
    if not ANDROID:
        try:
            root.geometry(geom)
        except Exception:
            pass


def app_minsize(root, w, h):
    """Set minimum window size (no-op on Android)."""
    if not ANDROID:
        try:
            root.minsize(w, h)
        except Exception:
            pass


def app_set_icon(root, icon_path):
    """Set window icon (no-op on Android)."""
    if not ANDROID and icon_path:
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass


def app_set_taskbar_id():
    """Set Windows AppUserModelID for taskbar icon (no-op elsewhere)."""
    if not ANDROID:
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "culinaryindex.app.1")
        except Exception:
            pass


def make_font(size, weight="normal", family="Segoe UI"):
    """Create a font specification compatible with both backends."""
    if USE_CTK:
        try:
            return ctk.CTkFont(size=size, weight=weight, family=family)
        except Exception:
            pass
    if weight == "bold":
        return (family, size, "bold")
    return (family, size)
