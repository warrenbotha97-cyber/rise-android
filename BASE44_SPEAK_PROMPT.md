# RISE: "Speak today's challenge" (subscribers only)

Paste the prompt below into the Base44 editor chat for RISE.
Replace the part in [square brackets] with how RISE knows someone is a paying subscriber.

The speaking code runs in the web app, so changing it never needs a new APK.
Inside the Android app it uses the phone's own speech engine through Capacitor;
in Chrome it falls back to the browser's built-in speech.

---

## Prompt to paste into Base44

Add a "Listen" button next to today's daily challenge. When tapped, it reads the
challenge text aloud. Tapping it again stops the speech.

Only paying subscribers can use it: [CONDITION, e.g. "the user's `subscription_status`
is `active`"]. For everyone else, show the same button with a small lock icon;
tapping it shows a short message that speaking is a subscriber feature, with the
existing upgrade/subscribe button. Do not change anything else in the app, and keep
the existing design.

Use this helper for the speaking itself (create it as a utility, don't change it):

```js
// speak.js
export async function speakText(text) {
  const tts = window.Capacitor?.Plugins?.TextToSpeech;   // native engine in the Android app
  if (tts) {
    try { await tts.stop(); } catch (e) {}
    return tts.speak({ text, lang: "en-US", rate: 1.0, pitch: 1.0, volume: 1.0 });
  }
  if ("speechSynthesis" in window) {                      // browser fallback (Chrome etc.)
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    window.speechSynthesis.speak(u);
    return;
  }
  throw new Error("Speech is not supported on this device");
}

export async function stopSpeaking() {
  const tts = window.Capacitor?.Plugins?.TextToSpeech;
  if (tts) { try { await tts.stop(); } catch (e) {} }
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}
```

If speaking fails, show a short friendly error and do not crash the page.
