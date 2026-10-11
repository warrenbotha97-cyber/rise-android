# Prompts to paste into the Base44 editor chat for RISE

Each prompt below is one message. Paste them one at a time, and test after each.
Each message uses some Base44 credits. Do not paste keys or passwords into any chat.

The Android app (this repo) is a wrapper around the live RISE web app, so every
change below goes into Base44 and never needs a new APK, except the first time
a native plugin is added.

---

## 1. Already pasted: credit, subscriber flag, Listen button

(Kept as a record.) "Built by Warren" line and About entry, the `is_subscriber` flag
on UserProgress (admin-only), and a locked Listen button that reads the mission aloud
using `window.Capacitor.Plugins.TextToSpeech` with a `speechSynthesis` fallback.

---

## 2. Intro: resume where the user stopped

```
When a logged-in user replays the intro, never send them to the login screen. Replaying the intro must stay inside the app and resume exactly where they last stopped: the same step or slide, and if the intro is a video, the same playback time. Save that position on the user's device under a key specific to that user (so two accounts on one phone don't mix), update it as they move through the intro, and clear it when they finish. Add a small "Start over" option. If the user is not logged in, keep today's behaviour. Keep the existing design and don't change anything else.
```

---

## 3. Daily reminder on the phone itself (no server, no Firebase)

Needs the new APK (it has the local-notifications plugin). Replaces the push-based
reminder, which can't reach this APK.

```
Change the subscriber daily reminder so it works on the phone itself instead of through server push notifications. Keep the existing "Daily reminder" time picker on the Profile screen, subscriber-only, with an Off option. When a subscriber saves a time (or on each app start, to keep it in sync), do this: if window.Capacitor?.Plugins?.LocalNotifications exists, ask for notification permission, cancel the previous RISE reminder (id 1001), and, unless the time is Off or the user is not a subscriber, schedule a repeating daily local notification at the chosen hour and minute with the title "RISE" and the body "Your daily mission is ready. Rise up." (use schedule: { on: { hour, minute }, allowWhileIdle: true }). If permission is denied, show a short friendly message. If the plugin isn't available (for example in a normal browser), do nothing and don't show an error. Stop relying on the sendDailyMissionReminders server function and the push notification call; leave them unused. Don't change anything else.
```

---

## 4. PayFast subscription (R50 per month), sandbox only first

See the prompt that was given in the chat. Do not go live until a sandbox test payment
has switched `is_subscriber` on for a test user.
