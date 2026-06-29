#!/usr/bin/env python3
import os
import json
import urllib.parse
import requests
import anthropic
from datetime import datetime, timedelta, timezone

INSTAGRAM_CHANNEL_ID = "6a41579a5ab6d2f10680aa6f"
FACEBOOK_CHANNEL_ID = "6a415d125ab6d2f10680bde1"
CLOUDINARY_CLOUD = "dkqlevbi"

PROMPT = """You are the marketing agent for StackIn, an income and expense tracking app built for two specific groups of people who are chronically underserved by existing financial tools.

## WHO STACKIN IS FOR

### W2 Workers (servers, bartenders, restaurant employees)
These are people who make most of their money in tips — often $3/hr base wage — and have zero visibility into their true earnings. They trust their employer to pay them correctly, but have no personal record to verify against. Cash tips especially disappear into thin air with no paper trail.

The real problems they face without StackIn:
- No idea how much cash they make daily, weekly, yearly
- No way to dispute a paycheck discrepancy if hours were shorted
- No record of credit card tips to verify against what was reported
- Tax time is a guess — especially for unreported cash income
- Living paycheck to paycheck with no clear picture of net pay after taxes

### Independent Workers (tattoo artists, hairstylists, cosmetologists, nail techs, freelancers, small LLC owners)
These are self-employed people getting paid through 5 different channels — cash, Venmo, Apple Pay, POS, check — and tracking none of it. When tax season hits, they are scrambling through months of Venmo transactions, bank statements, and guessing how much cash they made. No profit/loss visibility. No expense tracking. Complete chaos.

The real problems they face without StackIn:
- Income scattered across cash, Venmo, Apple Pay, POS, check — never aggregated
- No expense tracking means no deductions at tax time
- No profit/loss visibility month to month
- QuickBooks is too complicated and intimidating for a one-person operation
- Spreadsheets require discipline and financial knowledge they don't have

## WHAT STACKIN DOES

### W2 Mode
- Track hourly pay, credit card tips, and cash tips after every shift
- Configure tax settings to see estimated net pay in real time
- Track hours worked independently to verify against employer payroll
- View earnings by day, pay period, and year
- Auto-generates a pay stub style earnings summary at end of each pay period
- Home screen is formatted like a spreadsheet — clean, familiar, zero learning curve
- Set reminders by time or by location (arriving/leaving work) to log income

### Independent Mode
- Track all income streams in one place: cash, Venmo, Apple Pay, POS, credit card, check
- Track and categorize expenses, upload receipt images
- Auto-generates monthly, quarterly, and yearly profit/loss statements
- Built for small LLC owners who need QuickBooks functionality without QuickBooks complexity
- Set reminders by time or by location (arriving/leaving work) to log income and expenses

### Hybrid Mode
- Full access to both W2 and Independent workspaces under one subscription

## PLATFORMS & PRICING
- iOS app (download from App Store) or web version at the StackIn website
- NOT yet available on Android
- 30-day free trial
- Multiple paid tiers: W2 Mode, Independent Mode, and Hybrid (both)
- Setup takes under 2 minutes

## WHAT MAKES STACKIN DIFFERENT
- Location-based and time-based reminders keep users accountable to log daily
- One simple settings page to configure everything
- The only app that combines W2 tip tracking AND independent income tracking in one place
- Designed so that someone who has never used a financial app can be fully set up in under 2 minutes
- Auto-generated pay stub and profit/loss statements mean tax time is no longer a nightmare

## BRAND VOICE
Authentic, relatable, hustle-aware. The founder is a server. Speak like someone in these industries — not a finance company, not an accountant, not a tech startup. Use casual language. Short sentences. Speak directly to the pain. No corporate tone. No jargon. No "seamless," "leverage," or "empower."

## YOUR TASK

Today's date is {today}. Day of week: {weekday}.

Audience rotation by day:
- Monday: servers/bartenders
- Tuesday: tattoo artists
- Wednesday: hairstylists/cosmetologists
- Thursday: freelancers/small business owners
- Friday: general cash-tip workers
- Saturday: servers/bartenders
- Sunday: tattoo artists

Choose a content theme relevant to today's date and generate the following as valid JSON only — no markdown, no explanation, just the JSON object:

{{
  "heading": "6-10 punchy words in ALL CAPS, scroll-stopping hook",
  "subheading": "2-3 sentences speaking directly to today's audience, conversational, sentence case",
  "instagram_caption": "3-5 sentences, casual and relatable, ends with call to action to download StackIn",
  "hashtags": "#StackIn #ServerLife #TipMoney #RestaurantWorkers #FOH #CashTips #HospitalityLife #TattooArtist #HairStylist #Cosmetologist #Freelance #IndependentContractor #KnowYourWorth #CashFlow #SmallBusiness",
  "facebook_post": "3-5 sentences, conversational, strong opening hook, ends with call to action to download StackIn, no hashtags"
}}
"""


def generate_content():
    today = datetime.now()
    weekday = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT.format(today=date_str, weekday=weekday)}]
    )

    raw = message.content[0].text.strip()
    return json.loads(raw)


def build_cloudinary_url(heading, subheading):
    heading_encoded = urllib.parse.quote(heading, safe='')
    subheading_encoded = urllib.parse.quote(subheading, safe='')
    url = (
        f"http://res.cloudinary.com/{CLOUDINARY_CLOUD}/image/upload/"
        f"c_fit,co_rgb:ffffff,g_north,l_text:Arial_58_bold:{heading_encoded},w_980,y_280/"
        f"c_fit,co_rgb:c8e6c9,g_north,l_text:Arial_44:{subheading_encoded},w_920,y_460/"
        f"stackin_template_blank.png"
    )
    return url


def schedule_buffer_post(channel_id, text, scheduled_at, image_url=None):
    token = os.environ["BUFFER_ACCESS_TOKEN"]
    data = {
        "access_token": token,
        "profile_ids[]": channel_id,
        "text": text,
        "scheduled_at": scheduled_at,
    }
    if image_url:
        data["media[photo]"] = image_url

    response = requests.post(
        "https://api.bufferapp.com/1/updates/create.json",
        data=data
    )
    result = response.json()
    if not response.ok:
        raise Exception(f"Buffer API error: {result}")
    return result


def main():
    print("Generating content...")
    content = generate_content()

    heading = content["heading"]
    subheading = content["subheading"]
    instagram_caption = content["instagram_caption"] + "\n\n" + content["hashtags"]
    facebook_post = content["facebook_post"]

    print(f"Heading: {heading}")
    print(f"Subheading: {subheading}")

    image_url = build_cloudinary_url(heading, subheading)
    print(f"Image URL: {image_url}")

    # Schedule for noon tomorrow UTC
    tomorrow_noon = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=17, minute=0, second=0, microsecond=0
    )
    scheduled_at = tomorrow_noon.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    print(f"Scheduling for: {scheduled_at}")

    print("Scheduling Instagram post...")
    ig_result = schedule_buffer_post(INSTAGRAM_CHANNEL_ID, instagram_caption, scheduled_at, image_url)
    print(f"Instagram scheduled: {ig_result}")

    print("Scheduling Facebook post...")
    fb_result = schedule_buffer_post(FACEBOOK_CHANNEL_ID, facebook_post, scheduled_at)
    print(f"Facebook scheduled: {fb_result}")

    print("\nDone! Both posts scheduled successfully.")


if __name__ == "__main__":
    main()
