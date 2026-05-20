"""
Floating Morse Code converter panel.

Conversion rules
────────────────
  User types text  →  auto-detect Thai/English  →  output Morse
  User types Morse →  output language set by EN/TH button

The EN/TH button only controls the *output* language when decoding Morse.
Input language is always auto-detected from the characters typed.
"""
from __future__ import annotations

import objc
from AppKit import (
    NSPanel, NSTextField, NSTextView, NSScrollView, NSButton, NSApp,
    NSColor, NSFont, NSScreen, NSEvent,
    NSFloatingWindowLevel,
    NSClosableWindowMask, NSTitledWindowMask, NSNonActivatingPanelMask,
    NSBackingStoreBuffered, NSBezelStyleRounded,
    NSTextDidChangeNotification,
)
from Foundation import NSMakeRect, NSObject, NSNotificationCenter

from converter import text_to_morse, morse_to_text, is_morse, detect_lang

W        = 480
H        = 310
PAD      = 14
BTN_W    = 56
BTN_H    = 24
INPUT_H  = 104
OUTPUT_H = 104
_COLLECTION_ALL_SPACES = 1 << 0


class _TextDelegate(NSObject):
    def initWithCallback_(self, callback):
        self = objc.super(_TextDelegate, self).init()
        self._callback = callback
        return self

    @objc.typedSelector(b"v@:@")
    def textDidChange_(self, notification):
        self._callback()


class _ButtonDelegate(NSObject):
    """Separate NSObject target for button actions — avoids underscore-method export issues."""

    def initWithCallback_(self, callback):
        self = objc.super(_ButtonDelegate, self).init()
        self._callback = callback
        return self

    @objc.typedSelector(b"v@:@")
    def clicked_(self, sender):  # noqa: ARG002
        self._callback()


class MorseOverlay(NSObject):
    """Inherits NSObject so Cocoa target-action can reach _toggleLang_:."""

    def init(self):
        self = objc.super(MorseOverlay, self).init()
        if self is None:
            return None
        self._morse_output_lang: str = "en"   # language used when decoding Morse
        self._window        = None
        self._input_view    = None
        self._output_view   = None
        self._lang_btn      = None
        self._status_lbl    = None
        self._delegate      = None
        self._lang_delegate = None   # must be kept alive — Cocoa doesn't retain it
        self._build_window()
        return self

    # ── Window ─────────────────────────────────────────────────────────────────

    def _build_window(self):
        self._window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, W, H),
            NSTitledWindowMask | NSClosableWindowMask | NSNonActivatingPanelMask,
            NSBackingStoreBuffered,
            False,
        )
        self._window.setTitle_("Morse Code Converter")
        self._window.setFloatingPanel_(True)
        self._window.setLevel_(NSFloatingWindowLevel)
        self._window.setCollectionBehavior_(_COLLECTION_ALL_SPACES)
        self._window.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.13, 0.13, 0.13, 1.0)
        )

        cv = self._window.contentView()
        ch = self._window.contentRectForFrameRect_(self._window.frame()).size.height

        # ── Header row: title + Morse-decode language toggle ──────────────────
        btn_y = ch - BTN_H - 10

        # "Morse → [EN]" — clicking [EN] toggles to [TH] and vice-versa
        hint = NSTextField.alloc().initWithFrame_(
            NSMakeRect(W - BTN_W - PAD - 68, btn_y + 5, 64, 14)
        )
        hint.setStringValue_("Morse decode:")
        _style_label(hint, 10, 0.50)
        hint.setAlignment_(2)
        cv.addSubview_(hint)

        self._lang_delegate = _ButtonDelegate.alloc().initWithCallback_(self._onLangToggle)
        self._lang_btn = _make_btn(
            W - BTN_W - PAD, btn_y, BTN_W, BTN_H,
            "EN", self._lang_delegate, "clicked:"
        )
        cv.addSubview_(self._lang_btn)

        # ── Input ──────────────────────────────────────────────────────────────
        in_lbl_y = btn_y - 18
        _add_label(cv, PAD, in_lbl_y, 280, 14,
                   "Input  (text auto-detect  /  type Morse: .- -... -.-.):", 10, 0.55)

        input_y = in_lbl_y - INPUT_H - 2
        input_scroll = _make_scroll(PAD, input_y, W - PAD * 2, INPUT_H)
        self._input_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, W - PAD * 2 - 16, INPUT_H)
        )
        _style_tv(self._input_view, editable=True)
        input_scroll.setDocumentView_(self._input_view)
        cv.addSubview_(input_scroll)

        # ── Status ─────────────────────────────────────────────────────────────
        status_y = input_y - 18
        self._status_lbl = NSTextField.alloc().initWithFrame_(
            NSMakeRect(PAD, status_y + 2, W - PAD * 2, 14)
        )
        self._status_lbl.setStringValue_("type text or Morse code above")
        _style_label(self._status_lbl, 10, 0.40)
        self._status_lbl.setAlignment_(2)
        cv.addSubview_(self._status_lbl)

        # ── Output ─────────────────────────────────────────────────────────────
        out_lbl_y = status_y - 18
        _add_label(cv, PAD, out_lbl_y, 60, 14, "Output:", 10, 0.55)

        output_y = out_lbl_y - OUTPUT_H - 2
        output_scroll = _make_scroll(PAD, output_y, W - PAD * 2, OUTPUT_H)
        self._output_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, W - PAD * 2 - 16, OUTPUT_H)
        )
        _style_tv(self._output_view, editable=False)
        output_scroll.setDocumentView_(self._output_view)
        cv.addSubview_(output_scroll)

        # ── Footer ─────────────────────────────────────────────────────────────
        footer = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 4, W, 12))
        footer.setStringValue_("Morse words separated by /   ·   Option+M toggle")
        _style_label(footer, 9, 0.25)
        footer.setAlignment_(2)
        cv.addSubview_(footer)

        # ── Delegate ───────────────────────────────────────────────────────────
        self._delegate = _TextDelegate.alloc().initWithCallback_(self._convert)
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self._delegate,
            "textDidChange:",
            NSTextDidChangeNotification,
            self._input_view,
        )

        self._reposition()

    # ── EN/TH toggle (output language for Morse decoding) ─────────────────────

    def _onLangToggle(self):
        """Called by _ButtonDelegate when the EN/TH button is clicked."""
        self._morse_output_lang = "th" if self._morse_output_lang == "en" else "en"
        self._lang_btn.setTitle_("TH" if self._morse_output_lang == "th" else "EN")
        self._convert()

    # ── Conversion ─────────────────────────────────────────────────────────────

    def _convert(self):
        raw = self._input_view.string() if self._input_view else ""

        if not raw.strip():
            self._output_view.setString_("")
            self._status_lbl.setStringValue_("type text or Morse code above")
            return

        if is_morse(raw):
            # Morse → text: output language from EN/TH button
            lang = self._morse_output_lang
            result = morse_to_text(raw, lang)
            lang_name = "Thai" if lang == "th" else "English"
            self._status_lbl.setStringValue_("Morse  →  %s" % lang_name)
        else:
            # Text → Morse: auto-detect input language
            lang = detect_lang(raw)
            result = text_to_morse(raw, lang)
            lang_name = "Thai" if lang == "th" else "English"
            self._status_lbl.setStringValue_("%s (auto)  →  Morse" % lang_name)

        if self._output_view:
            self._output_view.setString_(result)

    # ── Positioning / visibility ───────────────────────────────────────────────

    def _reposition(self):
        try:
            pt = NSEvent.mouseLocation()
            screen = next(
                (s for s in NSScreen.screens()
                 if s.frame().origin.x <= pt.x
                 <= s.frame().origin.x + s.frame().size.width),
                NSScreen.mainScreen(),
            )
        except Exception:
            screen = NSScreen.mainScreen()
        sf = screen.frame()
        self._window.setFrameOrigin_((
            sf.origin.x + (sf.size.width  - W) / 2,
            sf.origin.y + (sf.size.height - H) / 2,
        ))

    def show(self):
        self._reposition()
        self._window.makeKeyAndOrderFront_(None)
        self._window.makeFirstResponder_(self._input_view)

    def hide(self):
        if self._window:
            self._window.orderOut_(None)

    def toggle(self):
        if self._window and self._window.isVisible():
            self.hide()
        else:
            self.show()


# ── Layout helpers ─────────────────────────────────────────────────────────────

def _make_btn(x, y, w, h, title, target, action):
    btn = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    btn.setTitle_(title)
    btn.setBezelStyle_(NSBezelStyleRounded)
    btn.setFont_(NSFont.boldSystemFontOfSize_(11))
    btn.setTarget_(target)
    btn.setAction_(action)
    return btn


def _make_scroll(x, y, w, h):
    sv = NSScrollView.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    sv.setBorderType_(2)
    sv.setHasVerticalScroller_(True)
    sv.setAutohidesScrollers_(True)
    return sv


def _add_label(parent, x, y, w, h, text, size, alpha):
    lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    lbl.setStringValue_(text)
    _style_label(lbl, size, alpha)
    parent.addSubview_(lbl)
    return lbl


def _style_label(field, size, alpha):
    field.setBezeled_(False)
    field.setDrawsBackground_(False)
    field.setEditable_(False)
    field.setSelectable_(False)
    field.setTextColor_(NSColor.colorWithWhite_alpha_(alpha, 1.0))
    field.setFont_(NSFont.systemFontOfSize_(size))


def _style_tv(view, editable):
    view.setFont_(NSFont.monospacedSystemFontOfSize_weight_(13, 0))
    view.setInsertionPointColor_(NSColor.whiteColor())
    view.setRichText_(False)
    view.setAllowsUndo_(True)
    view.setEditable_(editable)
    view.setSelectable_(True)
    if editable:
        view.setAutomaticDashSubstitutionEnabled_(False)
        view.setAutomaticQuoteSubstitutionEnabled_(False)
        view.setAutomaticSpellingCorrectionEnabled_(False)
        view.setSmartInsertDeleteEnabled_(False)
        view.setTextColor_(NSColor.whiteColor())
        view.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.18, 0.18, 0.18, 1.0)
        )
    else:
        view.setTextColor_(NSColor.colorWithWhite_alpha_(0.85, 1.0))
        view.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.13, 0.13, 0.13, 1.0)
        )
