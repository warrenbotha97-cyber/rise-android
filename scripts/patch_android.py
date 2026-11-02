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

JAVA = """package com.rise.dailypeak;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    private static final String APP_URL = "%s";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        openReturnLink(getIntent());
    }

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
}
""" % APP_URL


def main():
    s = open(MANIFEST).read()
    if 'android:scheme="riseapp"' not in s:
        idx = s.find("</activity>")
        if idx < 0:
            sys.exit("MainActivity </activity> not found in manifest")
        s = s[:idx] + FILTER + "        " + s[idx:]
        open(MANIFEST, "w").write(s)
    open(ACTIVITY, "w").write(JAVA)
    print("patched manifest and MainActivity")


if __name__ == "__main__":
    main()
