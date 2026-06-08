import os
import json
import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube"]
TZ = pytz.timezone("Europe/Zurich")

# --- параметри обкладинки (фон 1280x720) ---
BACKGROUND = "background.jpg"
FONT_PATH = "Montserrat.ttf"     # variable Montserrat
FONT_WEIGHT_VALUE = 380          # вага по осі (Thin=100); товщина штриха ~21px
DATE_CENTER = (1088, 142)        # центр тексту дати
FONT_SIZE = 120                  # px
DATE_COLOR = (0, 0, 0)           # #000000
TRACKING_CANVA = -70             # Canva letter spacing (від'ємний — літери ближче)
SHADOW_RGBA = (0, 0, 0, 30)      # rgba(0,0,0,30) — ледь помітна
SHADOW_OFFSET = (2, 2)           # px
SHADOW_BLUR = 5                  # px
SUPERSAMPLE = 4                  # рендер у 4x і зменшення -> гладкі криві


def get_service():
    creds = Credentials.from_authorized_user_info(
        json.loads(os.environ["YT_TOKEN"]), SCOPES
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def next_saturday():
    now = datetime.datetime.now(TZ)
    days = (5 - now.weekday()) % 7
    if days == 0 and now.hour >= 11:
        days = 7
    return (now + datetime.timedelta(days=days)).replace(
        hour=11, minute=0, second=0, microsecond=0
    )


def _draw_tracked(draw, center, text, font, fill, spacing):
    """Малює текст по центру із заданим трекінгом (може бути від'ємним)."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = center[0] - total / 2
    cy = center[1]
    for ch, w in zip(text, widths):
        draw.text((x, cy), ch, font=font, fill=fill, anchor="lm")
        x += w + spacing


def make_thumbnail(start):
    base = Image.open(BACKGROUND).convert("RGBA").resize((1280, 720))
    W, H = base.size
    ss = SUPERSAMPLE
    text = start.strftime("%d/%m")           # напр. 13/06

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE * ss)
    font.set_variation_by_axes([FONT_WEIGHT_VALUE])
    spacing = TRACKING_CANVA / 1000 * FONT_SIZE * ss
    c = (DATE_CENTER[0] * ss, DATE_CENTER[1] * ss)

    # тінь (окремий шар, з розмиттям)
    shadow = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sc = (c[0] + SHADOW_OFFSET[0] * ss, c[1] + SHADOW_OFFSET[1] * ss)
    _draw_tracked(sd, sc, text, font, SHADOW_RGBA, spacing)
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR * ss))

    # основний текст
    layer = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    td = ImageDraw.Draw(layer)
    _draw_tracked(td, c, text, font, DATE_COLOR + (255,), spacing)

    merged = Image.alpha_composite(shadow, layer)
    merged = merged.resize((W, H), Image.LANCZOS)   # max-quality сглаживание
    base = Image.alpha_composite(base, merged)

    out = "thumb_out.jpg"
    base.convert("RGB").save(out, quality=95)
    return out


def create_broadcast(youtube):
    start = next_saturday()
    start_iso = start.isoformat()

    broadcast = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": f"Богослужіння — {start.strftime('%d.%m.%Y')}",
                "scheduledStartTime": start_iso,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
            "contentDetails": {
                "enableAutoStart": True,
                "enableAutoStop": True,
            },
        },
    ).execute()

    stream = youtube.liveStreams().insert(
        part="snippet,cdn,contentDetails",
        body={
            "snippet": {"title": f"Stream {start.strftime('%d.%m.%Y')}"},
            "cdn": {
                "frameRate": "variable",
                "ingestionType": "rtmp",
                "resolution": "variable",
            },
            "contentDetails": {"isReusable": False},
        },
    ).execute()

    youtube.liveBroadcasts().bind(
        id=broadcast["id"],
        part="id,contentDetails",
        streamId=stream["id"],
    ).execute()

    thumb = make_thumbnail(start)
    youtube.thumbnails().set(
        videoId=broadcast["id"],
        media_body=MediaFileUpload(thumb),
    ).execute()

    rtmp = stream["cdn"]["ingestionInfo"]
    print(f"Broadcast ID: {broadcast['id']}")
    print(f"Watch URL: https://youtube.com/watch?v={broadcast['id']}")
    print(f"RTMP URL: {rtmp['ingestionAddress']}")
    print(f"Stream key: {rtmp['streamName']}")


if __name__ == "__main__":
    create_broadcast(get_service())
