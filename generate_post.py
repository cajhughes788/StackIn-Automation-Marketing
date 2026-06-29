#!/usr/bin/env python3
print("=== VERSION: CLOUDINARY SDK BUILD ===")
import os
import json
import requests
import anthropic
import cloudinary
import cloudinary.utils
from datetime import datetime, timedelta, timezone

INSTAGRAM_CHANNEL_ID = "6a41579a5ab6d2f10680aa6f"
FACEBOOK_CHANNEL_ID = "6a415d125ab6d2f10680bde1"
MCP_URL = "https://mcp.buffer.com/mcp"

cloudinary.config(cloud_name="dkqlevbi", api_key="452196185938819", api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""))

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

STRICT RULES — never break these:
- Never use the green check mark emoji (✅) anywhere in any post
- Never use an em dash (—) anywhere in any post; use a comma or period instead
- The instagram_caption must end with this exact line on its own line: "Create an account online here: https://stackin-app.com, or download on iOS here: https://apps.apple.com/us/app/stack-in/id6764385326"
- Place that CTA line BEFORE the hashtags block

Choose a content theme relevant to today's date and generate the following as valid JSON only — no markdown, no explanation, just the JSON object:

{{
  "heading": "6-10 punchy words in ALL CAPS, scroll-stopping hook",
  "subheading": "2-3 sentences speaking directly to today's audience, conversational, sentence case",
  "instagram_caption": "3-5 sentences, casual and relatable. End with this exact line: Create an account online here: https://stackin-app.com, or download on iOS here: https://apps.apple.com/us/app/stack-in/id6764385326",
  "hashtags": "#StackIn #ServerLife #TipMoney #RestaurantWorkers #FOH #CashTips #HospitalityLife #TattooArtist #HairStylist #Cosmetologist #Freelance #IndependentContractor #KnowYourWorth #CashFlow #SmallBusiness",
  "facebook_post": "3-5 sentences, conversational, strong opening hook. End with: Create an account online here: https://stackin-app.com, or download on iOS here: https://apps.apple.com/us/app/stack-in/id6764385326 — no hashtags"
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
    url, _ = cloudinary.utils.cloudinary_url(
        "stackin_template_blank",
        transformation=[
            {"overlay": {"font_family": "Arial", "font_size": 58, "font_weight": "bold", "text": heading},
             "color": "#ffffff", "gravity": "north", "y": 280, "width": 980, "crop": "fit"},
            {"overlay": {"font_family": "Arial", "font_size": 44, "text": subheading},
             "color": "#c8e6c9", "gravity": "north", "y": 460, "width": 920, "crop": "fit"}
        ],
        format="png"
    )
    return url


def call_buffer_mcp(tool_name, arguments):
    token = os.environ["BUFFER_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    # Initialize MCP session
    init_resp = requests.post(MCP_URL, headers=headers, json={
        "jsonrpc": "2.0", "id": 0, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "stackin-bot", "version": "1.0"}
        }
    })
    print(f"MCP init status: {init_resp.status_code}")
    print(f"MCP init body: {init_resp.text[:400]}")

    session_id = init_resp.headers.get("Mcp-Session-Id")
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    # Notify server that client is initialized
    requests.post(MCP_URL, headers=headers, json={
        "jsonrpc": "2.0", "method": "notifications/initialized"
    })

    # Call the tool
    resp = requests.post(MCP_URL, headers=headers, json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments}
    })
    print(f"MCP tool call status: {resp.status_code}")
    print(f"MCP tool call body: {resp.text[:600]}")

    if not resp.ok:
        raise Exception(f"MCP call failed {resp.status_code}: {resp.text}")

    content_type = resp.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for line in resp.text.splitlines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "result" in data:
                    return data["result"]
        raise Exception(f"No result in SSE stream: {resp.text}")

    data = resp.json()
    if "result" in data:
        return data["result"]
    raise Exception(f"Unexpected MCP response: {data}")


def schedule_buffer_post(channel_id, text, scheduled_at, image_url=None, is_instagram=False):
    if is_instagram:
        scheduling_type = "notification"
        mode = "addToQueue"
    else:
        scheduling_type = "automatic"
        mode = "shareNow"
    args = {
        "channelId": channel_id,
        "text": text,
        "schedulingType": scheduling_type,
        "mode": mode,
    }
    if image_url:
        args["assets"] = [{"image": {"url": image_url}}]
    if is_instagram:
        args["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
    else:
        args["metadata"] = {"facebook": {"type": "post"}}

    return call_buffer_mcp("create_post", args)


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

    print("Posting Instagram now...")
    ig_result = schedule_buffer_post(INSTAGRAM_CHANNEL_ID, instagram_caption, None, image_url, is_instagram=True)
    if ig_result.get("isError"):
        raise Exception(f"Instagram failed: {ig_result}")
    print(f"Instagram queued successfully.")

    print("Posting Facebook now...")
    fb_result = schedule_buffer_post(FACEBOOK_CHANNEL_ID, facebook_post, None, is_instagram=False)
    if fb_result.get("isError"):
        raise Exception(f"Facebook failed: {fb_result}")
    print(f"Facebook posted successfully.")

    print("\nDone! Both posts completed successfully.")


if __name__ == "__main__":
    main()
