import os
import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

# Final Instagram portrait size, drawn at 2x and scaled down for sharp edges
OUT_W, OUT_H = 1080, 1350
SCALE = 2
W, H = OUT_W * SCALE, OUT_H * SCALE
MARGIN = 110 * SCALE

NAVY_TOP = (9, 16, 38)
NAVY_BOTTOM = (18, 32, 66)
GOLD = (212, 175, 55)
GOLD_SOFT = (232, 205, 120)
WHITE = (245, 245, 240)
MUTED = (150, 162, 190)

BRAND = "THE INDIAN RUPEES"
HASHTAGS = "#TheIndianRupees #PersonalFinance #MoneyTips #InvestingIndia #FinancialFreedom"

# Each topic is one carousel. A different topic is posted each day.
# Slide kinds: cover, point, stat, cta
TOPICS = [
    {
        "caption": "Time is the most powerful ingredient in investing. Start small, start today.",
        "slides": [
            {"kind": "cover", "kicker": "WEALTH BASICS", "title": "The Power of Compounding",
             "body": "Why starting early beats investing more later."},
            {"kind": "stat", "kicker": "₹5,000 A MONTH AT 12%", "title": "₹1.76 Cr",
             "body": "after 30 years. You invest only ₹18 lakh. The rest is growth on growth."},
            {"kind": "point", "kicker": "WAIT 10 YEARS?", "title": "You end with ₹50 lakh",
             "body": "Same ₹5,000 a month, but for 20 years instead of 30. Ten years of delay costs over ₹1.2 crore."},
            {"kind": "point", "kicker": "RULE OF 72", "title": "72 ÷ return = years to double",
             "body": "At 12% a year, money doubles in about 6 years. At 6%, it takes about 12."},
            {"kind": "cta", "kicker": "YOUR NEXT STEP", "title": "Start a SIP this month",
             "body": "Even ₹500 is enough to begin. Increase it every time your salary grows."},
        ],
    },
    {
        "caption": "Before you invest, protect yourself. An emergency fund keeps one bad month from becoming a bad year.",
        "slides": [
            {"kind": "cover", "kicker": "MONEY SAFETY", "title": "Build Your Emergency Fund",
             "body": "The first step before any investment."},
            {"kind": "stat", "kicker": "THE TARGET", "title": "6 months",
             "body": "of essential expenses: rent, EMIs, groceries, bills and insurance premiums."},
            {"kind": "point", "kicker": "WHERE TO KEEP IT", "title": "Safe and easy to reach",
             "body": "A savings account, a sweep-in FD or a liquid fund. Not stocks, not crypto."},
            {"kind": "point", "kicker": "HOW TO BUILD IT", "title": "One month at a time",
             "body": "Set up an auto-transfer on salary day. Reach one month first, then keep going."},
            {"kind": "cta", "kicker": "YOUR NEXT STEP", "title": "Add up your monthly essentials",
             "body": "Multiply by six. That number is your safety net goal."},
        ],
    },
    {
        "caption": "A simple budget that actually works. Pay yourself first.",
        "slides": [
            {"kind": "cover", "kicker": "BUDGETING", "title": "The 50 / 30 / 20 Rule",
             "body": "A simple way to split every salary."},
            {"kind": "stat", "kicker": "NEEDS", "title": "50%",
             "body": "Rent, EMIs, groceries, utilities, insurance. The things you must pay."},
            {"kind": "stat", "kicker": "WANTS", "title": "30%",
             "body": "Eating out, shopping, trips, subscriptions. Enjoy it without guilt."},
            {"kind": "stat", "kicker": "SAVINGS & INVESTMENTS", "title": "20%",
             "body": "SIPs, PPF, emergency fund. Move it on salary day, before you spend."},
            {"kind": "cta", "kicker": "ON A ₹50,000 SALARY", "title": "₹25k · ₹15k · ₹10k",
             "body": "Needs, wants, savings. Adjust the split, but never skip the 20%."},
        ],
    },
]


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), size * SCALE)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight] if name.startswith("Playfair") else [32, weight])
        except Exception:
            pass
    return f


def serif(size, weight=700):
    return font("PlayfairDisplay.ttf", size, weight)


def sans(size, weight=400):
    return font("Inter.ttf", size, weight)


def wrap(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=fnt) <= max_width or not line:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_lines(draw, lines, fnt, x, y, fill, line_height):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def tracked(draw, xy, text, fnt, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing
    return x


def tracked_width(draw, text, fnt, spacing):
    return sum(draw.textlength(ch, font=fnt) for ch in text) + spacing * (len(text) - 1)


def background():
    img = Image.new("RGB", (W, H), NAVY_TOP)
    px = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY_TOP[i] + (NAVY_BOTTOM[i] - NAVY_TOP[i]) * t) for i in range(3))
        px.line([(0, y), (W, y)], fill=c)

    # Soft blue glow in the top right corner
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.45, -H * 0.25, W * 1.35, H * 0.45], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.composite(Image.new("RGB", (W, H), (60, 95, 170)), img, glow)

    # Large faint rupee watermark
    mark = Image.new("L", (W, H), 0)
    mfont = sans(900, 200)
    ImageDraw.Draw(mark).text((W * 0.52, H * 0.42), "₹", font=mfont, fill=22)
    img = Image.composite(Image.new("RGB", (W, H), GOLD), img, mark)
    return img


def draw_frame(draw, index, total, kind):
    m = MARGIN
    # Brand line at the top
    bfont = sans(22, 600)
    tracked(draw, (m, m), BRAND, bfont, GOLD, 6 * SCALE)
    pfont = sans(22, 500)
    page = f"{index:02d} / {total:02d}"
    draw.text((W - m - draw.textlength(page, font=pfont), m), page, font=pfont, fill=MUTED)
    draw.line([(m, m + 70 * SCALE), (W - m, m + 70 * SCALE)], fill=(*GOLD, ), width=SCALE)

    # Footer
    ffont = sans(24, 500)
    y = H - m - 30 * SCALE
    if kind == "cta":
        left = "Save this post  ·  Share with a friend"
    else:
        left = "Swipe for more  →"
    draw.text((m, y), left, font=ffont, fill=GOLD_SOFT if kind != "cta" else WHITE)
    handle = "Follow for daily money lessons"
    if kind == "cta":
        draw.text((W - m - draw.textlength(handle, font=ffont), y), handle, font=ffont, fill=GOLD)


def render_slide(slide, index, total):
    img = background()
    draw = ImageDraw.Draw(img)
    draw_frame(draw, index, total, slide["kind"])
    m = MARGIN
    max_w = W - 2 * m
    kind = slide["kind"]

    kfont = sans(30, 600)
    if kind == "cover":
        tfont, bfont = serif(112, 700), sans(40, 400)
        y = int(H * 0.30)
    elif kind == "stat":
        tfont, bfont = serif(190, 700), sans(42, 400)
        y = int(H * 0.27)
    else:
        tfont, bfont = serif(88, 700), sans(42, 400)
        y = int(H * 0.30)

    # Kicker with a short gold rule before it
    draw.line([(m, y + 20 * SCALE), (m + 60 * SCALE, y + 20 * SCALE)], fill=GOLD, width=3 * SCALE)
    tracked(draw, (m + 84 * SCALE, y), slide["kicker"], kfont, GOLD, 4 * SCALE)
    y += 90 * SCALE

    # Playfair has old-style figures that look uneven in numbers, so titles
    # with digits or the rupee sign use Inter instead
    if any(ch.isdigit() or ch == "₹" for ch in slide["title"]):
        tfont = sans(int(tfont.size / SCALE * 0.92), 700)

    title_lines = wrap(draw, slide["title"], tfont, max_w)
    lh = int(tfont.size * 1.12)
    y = draw_lines(draw, title_lines, tfont, m, y, GOLD if kind == "stat" else WHITE, lh)
    y += 50 * SCALE

    body_lines = wrap(draw, slide["body"], bfont, max_w * 0.92)
    draw_lines(draw, body_lines, bfont, m, y, (210, 216, 230), int(bfont.size * 1.5))

    return img.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)


def todays_topic(day=None):
    day = day or datetime.date.today()
    return TOPICS[day.toordinal() % len(TOPICS)]


def todays_caption(day=None):
    topic = todays_topic(day)
    return f"{topic['caption']}\n\n{HASHTAGS}"


def create_carousel_slides(day=None):
    os.makedirs("slides", exist_ok=True)
    topic = todays_topic(day)
    slides = topic["slides"]

    # Remove slides left over from a longer carousel
    for name in os.listdir("slides"):
        if name.startswith("slide_") and name.endswith(".png"):
            os.remove(os.path.join("slides", name))

    filenames = []
    for i, slide in enumerate(slides, start=1):
        filename = f"slides/slide_{i}.png"
        render_slide(slide, i, len(slides)).save(filename, "PNG", optimize=True)
        filenames.append(filename)

    print(f"Generated {len(filenames)} slides: {slides[0]['title']}")
    return filenames


if __name__ == "__main__":
    create_carousel_slides()
