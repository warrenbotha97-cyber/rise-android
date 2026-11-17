#!/usr/bin/env python3
"""Adds the riseapp:// return link to the generated Android project.

After PayFast (paying or cancelling) the web page hands the person back to the app with
riseapp://open/profile?payment=received|cancelled. MainActivity turns that into the live
RISE profile URL and loads it inside the app, so nobody is left in Chrome.
"""
import re
import sys

APP_URL = "https://petite-rise-daily-peak.base44.app"
MANIFEST = "android/app/src/main/AndroidManifest.xml"
ACTIVITY = "android/app/src/main/java/com/rise/dailypeak/MainActivity.java"

FILTER = """
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="riseapp" android:host="open" />
            </intent-filter>
"""

IMPORTS = "import android.content.Intent;\nimport android.net.Uri;\n"

APP_URL_FIELD = """
    private static final String APP_URL = "%s";
""" % APP_URL

METHODS = """
    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        openReturnLink(intent);
    }

    private void openReturnLink(Intent intent) {
        if (intent == null) return;
        Uri uri = intent.getData();
        if (uri == null || !"riseapp".equals(uri.getScheme())) return;
        String payment = uri.getQueryParameter("payment");
        if (!"received".equals(payment)) payment = "cancelled";
        final String url = APP_URL + "/profile?payment=" + payment;
        if (getBridge() != null && getBridge().getWebView() != null) {
            getBridge().getWebView().post(() -> getBridge().getWebView().loadUrl(url));
        }
    }
"""


def patch_activity():
    """Add the return link to the EXISTING MainActivity (the one with the opening animation).

    Never overwrite the file: other build steps (make_splash.py) put their own code in it.
    Anything unexpected stops the build, so a clash is loud instead of silently dropping a feature.
    """
    s = open(ACTIVITY).read()
    if "openReturnLink" in s:
        return
    if "showSplash" not in s:
        sys.exit("MainActivity has no opening animation - run make_splash.py before patch_android.py")
    anchor = "import com.getcapacitor.BridgeActivity;"
    if anchor not in s:
        sys.exit("BridgeActivity import not found in MainActivity")
    s = s.replace(anchor, IMPORTS + anchor, 1)
    cls = re.search(r"public class MainActivity extends BridgeActivity \{", s)
    if not cls:
        sys.exit("MainActivity class declaration not found")
    s = s[:cls.end()] + APP_URL_FIELD + s[cls.end():]
    call = "super.onCreate(savedInstanceState);"
    if call not in s:
        sys.exit("onCreate super call not found in MainActivity")
    s = s.replace(call, call + "\n        openReturnLink(getIntent());", 1)
    end = s.rstrip().rfind("}")
    s = s[:end] + METHODS + "}\n"
    open(ACTIVITY, "w").write(s)
    if "showSplash" not in s or "openReturnLink" not in s:
        sys.exit("MainActivity lost a feature while patching")


def main():
    s = open(MANIFEST).read()
    if 'android:scheme="riseapp"' not in s:
        idx = s.find("</activity>")
        if idx < 0:
            sys.exit("MainActivity </activity> not found in manifest")
        s = s[:idx] + FILTER + "        " + s[idx:]
        open(MANIFEST, "w").write(s)
    patch_activity()
    print("patched manifest and MainActivity")


if __name__ == "__main__":
    main()
