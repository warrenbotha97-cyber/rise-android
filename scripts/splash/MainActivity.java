package com.rise.dailypeak;

import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.view.animation.DecelerateInterpolator;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.getcapacitor.BridgeActivity;

/**
 * RISE opening animation.
 *
 * A native overlay is drawn on top of the WebView every time the app starts.
 * The live RISE site keeps loading underneath it, so login, loading, the voice
 * coach and notifications are not affected. Whatever happens, the overlay is
 * removed after about 3 seconds, and any error simply skips the animation.
 *
 * Sequence: logo, then the name RISE, then a green underline that draws itself,
 * then the tagline fades in, then the whole screen fades into the app.
 */
public class MainActivity extends BridgeActivity {

    private static final int GREEN = Color.parseColor("#66FF00");
    private static final long FADE_OUT_START_MS = 2600L;
    private static final long FADE_OUT_MS = 400L;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        try {
            showSplash();
        } catch (Throwable ignored) {
            // The animation must never stop the app from opening.
        }
    }

    private void showSplash() {
        final ViewGroup content = (ViewGroup) findViewById(android.R.id.content);
        if (content == null) {
            return;
        }
        final float d = getResources().getDisplayMetrics().density;

        final FrameLayout overlay = new FrameLayout(this);
        overlay.setBackgroundColor(Color.BLACK);
        overlay.setClickable(true); // swallow touches while the animation plays

        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setGravity(Gravity.CENTER_HORIZONTAL);
        FrameLayout.LayoutParams columnParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER);
        overlay.addView(column, columnParams);

        // 1. Logo (the existing green R and arrow)
        ImageView logo = null;
        int logoId = getResources().getIdentifier("rise_logo", "drawable", getPackageName());
        if (logoId != 0) {
            logo = new ImageView(this);
            logo.setImageResource(logoId);
            logo.setAdjustViewBounds(true);
            logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
            column.addView(logo, new LinearLayout.LayoutParams((int) (190 * d), (int) (190 * d)));
            logo.setAlpha(0f);
            logo.setScaleX(0.85f);
            logo.setScaleY(0.85f);
        }

        // 2. Name
        TextView title = new TextView(this);
        title.setText("RISE");
        title.setTextColor(Color.WHITE);
        title.setTextSize(44f);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setLetterSpacing(0.18f);
        title.setGravity(Gravity.CENTER);
        title.setIncludeFontPadding(false);
        LinearLayout.LayoutParams titleParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        titleParams.topMargin = (int) (4 * d);
        column.addView(title, titleParams);
        title.setAlpha(0f);
        title.setTranslationY(16 * d);

        // 3. Green underline that draws itself from left to right
        View underline = new View(this);
        GradientDrawable bar = new GradientDrawable();
        bar.setColor(GREEN);
        bar.setCornerRadius(2 * d);
        underline.setBackground(bar);
        LinearLayout.LayoutParams lineParams = new LinearLayout.LayoutParams(
                (int) (150 * d), Math.max(3, (int) (3 * d)));
        lineParams.topMargin = (int) (10 * d);
        column.addView(underline, lineParams);
        underline.setPivotX(0f);
        underline.setPivotY(0f);
        underline.setScaleX(0f);

        // 4. Tagline
        TextView tagline = new TextView(this);
        tagline.setText("RISE ABOVE YOUR LIMITS");
        tagline.setTextColor(Color.parseColor("#B3FFFFFF"));
        tagline.setTextSize(12f);
        tagline.setLetterSpacing(0.28f);
        tagline.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams tagParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        tagParams.topMargin = (int) (18 * d);
        column.addView(tagline, tagParams);
        tagline.setAlpha(0f);

        content.addView(overlay, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        // Animations
        if (logo != null) {
            logo.animate().alpha(1f).scaleX(1f).scaleY(1f)
                    .setStartDelay(100).setDuration(700)
                    .setInterpolator(new DecelerateInterpolator()).start();
        }
        title.animate().alpha(1f).translationY(0f)
                .setStartDelay(450).setDuration(600)
                .setInterpolator(new DecelerateInterpolator()).start();
        underline.animate().scaleX(1f)
                .setStartDelay(1000).setDuration(700)
                .setInterpolator(new AccelerateDecelerateInterpolator()).start();
        tagline.animate().alpha(1f)
                .setStartDelay(1650).setDuration(600).start();

        // Fade the whole screen into the app, then remove the overlay for good.
        overlay.postDelayed(new Runnable() {
            @Override
            public void run() {
                overlay.animate().alpha(0f).setDuration(FADE_OUT_MS)
                        .withEndAction(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    content.removeView(overlay);
                                } catch (Throwable ignored) {
                                    // already gone
                                }
                            }
                        }).start();
            }
        }, FADE_OUT_START_MS);
    }
}
