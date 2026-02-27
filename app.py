import streamlit as st
import base64
import io
import zipfile
import asyncio
import tempfile
import os
import json
import requests
from pathlib import Path

# ─── Page Config ───
st.set_page_config(
    page_title="AdRoll Creative Studio — Edstellar",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Fraunces:wght@600;700;800&display=swap');

.stApp { background: #0c0e14; }
section[data-testid="stSidebar"] {
    background: #13151e;
    border-right: 1px solid #2a2e42;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e8eaf0 !important;
}

/* Hide default Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

.topbar-custom {
    font-family: 'Outfit', sans-serif;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 0 20px;
    border-bottom: 1px solid #2a2e42;
    margin-bottom: 24px;
}
.topbar-custom .logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #4f6ef7, #f7a84f);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 18px; color: white;
}
.topbar-custom .title {
    font-weight: 700; font-size: 20px; color: #e8eaf0;
    font-family: 'Outfit', sans-serif;
}
.topbar-custom .subtitle {
    font-weight: 400; color: #6b6f88; margin-left: 8px;
}

.section-label {
    font-family: 'Outfit', sans-serif;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: #6b6f88;
    margin: 20px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #2a2e42;
}

.ad-card-title {
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #9498b0;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ad-card-title .size-badge {
    background: #1a1d2b;
    border: 1px solid #2a2e42;
    padding: 2px 8px;
    font-size: 10px;
    color: #6b6f88;
}

.preset-chip {
    display: inline-block;
    background: #1a1d2b;
    border: 1px solid #2a2e42;
    color: #9498b0;
    padding: 4px 12px;
    margin: 2px 4px 2px 0;
    font-size: 12px;
    font-family: 'Outfit', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
}
.preset-chip:hover {
    border-color: #4f6ef7;
    color: #6b8aff;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Defaults ───
defaults = {
    "company_name": "Edstellar",
    "headline1": "Still Exploring Corporate Training?",
    "headline2": "Upskill Your Teams with Expert-Led Training",
    "headline3": "Train Smarter. Scale Faster.",
    "headline4": "Your Team's Training Plan Is Waiting",
    "cta_text": "Get Free Consultation →",
    "stat1": "2000+", "stat_label1": "Courses",
    "stat2": "5000+", "stat_label2": "Trainers",
    "stat3": "100+", "stat_label3": "Locations",
    "clients": "VISA, MICROSOFT, AMAZON, INTEL",
    "benefits": "Customized programs for your team\n5,000+ certified expert trainers\nFlexible: virtual, onsite, or hybrid",
    "color_primary": "#1A56DB",
    "color_dark": "#0B1D3A",
    "color_accent": "#F59E0B",
    "logo_dark_data": None,
    "logo_light_data": None,
}
for k, val in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = val


# ─── Preset Definitions ───
PRESETS = {
    "🔥 Urgency": {
        "headline1": "Your Team's Growth Can't Wait",
        "headline2": "Don't Let Skills Gaps Hold You Back",
        "headline3": "Act Now. Upskill Today.",
        "headline4": "Limited Slots — Book Your Training Now",
        "cta_text": "Get Free Consultation →",
        "benefits": "Customized programs — start in 48 hours\n5,000+ certified expert trainers on standby\nFlexible: virtual, onsite, or hybrid",
    },
    "⭐ Social Proof": {
        "headline1": "Join 500+ Fortune 500 Companies",
        "headline2": "Trusted by the World's Best Teams",
        "headline3": "Why Top Companies Choose Us",
        "headline4": "Visa, Microsoft, Amazon Trust Edstellar",
        "cta_text": "Request Custom Quote →",
        "benefits": "Trusted by Fortune 500 companies globally\nRated 4.9/5 by L&D leaders\n14+ years of proven training excellence",
    },
    "🎯 Benefits": {
        "headline1": "Customized Training, Measurable ROI",
        "headline2": "Expert-Led Programs Tailored for You",
        "headline3": "Train Smarter. Scale Faster.",
        "headline4": "2,000+ Courses, One Training Partner",
        "cta_text": "Enquire Now — It's Free →",
        "benefits": "Customized programs for your team\n5,000+ certified expert trainers\nFlexible: virtual, onsite, or hybrid",
    },
    "🔄 Re-engage": {
        "headline1": "Still Searching for Training?",
        "headline2": "Pick Up Where You Left Off",
        "headline3": "Your Training Plan Awaits",
        "headline4": "Welcome Back — Let's Finalize Your Plan",
        "cta_text": "Complete Your Enquiry →",
        "benefits": "Zero obligation consultation\n100% customized training roadmap\nFree proposal within 24 hours",
    },
    "◻ Minimal": {
        "headline1": "Corporate Training. Done Right.",
        "headline2": "Expert Training for Modern Teams",
        "headline3": "Upskill. Reskill. Excel.",
        "headline4": "World-Class Training, Globally Delivered",
        "cta_text": "Learn More →",
        "benefits": "2,000+ instructor-led courses\nGlobal delivery in 100+ locations\nMeasurable business impact",
    },
}


# ─── Helper: Logo to base64 img tag ───
def logo_img_tag(bg_type, height=24, fallback_letter="E", fallback_bg="#1A56DB"):
    """Return an <img> tag for the appropriate logo variant, or a fallback div."""
    # bg_type='dark' means dark background -> use light logo
    # bg_type='light' means light background -> use dark logo
    primary_key = "logo_dark_data" if bg_type == "dark" else "logo_light_data"
    fallback_key = "logo_light_data" if bg_type == "dark" else "logo_dark_data"

    data = st.session_state.get(primary_key) or st.session_state.get(fallback_key)

    if data:
        b64 = base64.b64encode(data).decode()
        return f'<img src="data:image/png;base64,{b64}" style="height:{height}px;max-width:{height*4}px;object-fit:contain;">'
    else:
        radius = 0
        fs = int(height * 0.5)
        return (f'<div style="width:{height}px;height:{height}px;background:{fallback_bg};'
                f'border-radius:{radius}px;display:flex;align-items:center;justify-content:center;'
                f'font-weight:800;font-size:{fs}px;color:white;flex-shrink:0;">{fallback_letter}</div>')


def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def highlight_last_words(text, color):
    words = text.split()
    if len(words) <= 2:
        return f'<span style="color:{color};">{text}</span>'
    last2 = " ".join(words[-2:])
    rest = " ".join(words[:-2])
    return f'{rest} <span style="color:{color};">{last2}</span>'


# ─── Generate Ad HTML ───
def generate_ad_html(ad_id, width, height):
    """Generate standalone HTML for a single ad creative."""
    s = st.session_state
    c_pri = s["color_primary"]
    c_dark = s["color_dark"]
    c_acc = s["color_accent"]
    name = s["company_name"]
    fl = name[0].upper() if name else "E"
    clients = [c.strip() for c in s["clients"].split(",") if c.strip()]

    # Per-ad overridable values
    hl = get_ad_val(ad_id, "headline")
    cta = get_ad_val(ad_id, "cta")
    sub = get_ad_val(ad_id, "subtext", "")
    ben_raw = get_ad_val(ad_id, "benefits", s.get("benefits", ""))
    benefits = [b.strip() for b in ben_raw.split("\n") if b.strip()] if ben_raw else []

    common_head = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Fraunces:wght@600;700;800;900&display=swap" rel="stylesheet">
    <style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:'Outfit',sans-serif;background:transparent;}}</style></head><body>"""

    logo_dark_lg = logo_img_tag('dark', 28, fl, c_pri)
    logo_dark_xl = logo_img_tag('dark', 34, fl, c_pri)
    logo_dark_sm = logo_img_tag('dark', 18, fl, 'transparent')
    logo_light = logo_img_tag('light', 22, fl, c_pri)
    logo_light_sm = logo_img_tag('light', 18, fl, c_pri)

    ads = {}

    # 300x250 A - Dark/Urgency
    ads["300x250_A"] = f"""{common_head}
    <div style="width:300px;height:250px;padding:22px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;
        background:linear-gradient(145deg,{c_dark} 0%,{hex_to_rgba(c_pri,0.4)} 50%,{c_dark} 100%);">
      <div style="position:absolute;top:-40px;right:-40px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,{hex_to_rgba(c_acc,0.25)},transparent 70%);pointer-events:none;"></div>
      <div style="display:flex;align-items:center;gap:8px;z-index:1;">{logo_dark_lg}<span style="font-weight:800;font-size:13px;color:#e2e8f0;letter-spacing:0.5px;">{name.upper()}</span></div>
      <div style="font-family:'Fraunces',serif;font-size:19px;font-weight:700;line-height:1.25;color:white;z-index:1;">{highlight_last_words(hl, c_acc)}</div>
      <div style="display:flex;gap:14px;z-index:1;">
        <div style="text-align:center;"><div style="font-size:17px;font-weight:800;color:{c_pri};">{s['stat1']}</div><div style="font-size:8.5px;text-transform:uppercase;letter-spacing:0.5px;color:rgba(255,255,255,0.6);">{s['stat_label1']}</div></div>
        <div style="text-align:center;"><div style="font-size:17px;font-weight:800;color:{c_pri};">{s['stat2']}</div><div style="font-size:8.5px;text-transform:uppercase;letter-spacing:0.5px;color:rgba(255,255,255,0.6);">{s['stat_label2']}</div></div>
        <div style="text-align:center;"><div style="font-size:17px;font-weight:800;color:{c_pri};">{s['stat3']}</div><div style="font-size:8.5px;text-transform:uppercase;letter-spacing:0.5px;color:rgba(255,255,255,0.6);">{s['stat_label3']}</div></div>
      </div>
      <button style="background:linear-gradient(135deg,{c_acc},{c_acc});color:{c_dark};border:none;padding:10px 18px;font-weight:700;font-size:11.5px;text-transform:uppercase;text-align:center;font-family:'Outfit',sans-serif;letter-spacing:0.4px;z-index:1;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 300x250 B - Light/Social Proof
    client_chips = "".join(f'<div style="background:#f5f7fa;padding:5px 9px;font-size:8.5px;font-weight:700;color:#5a6070;letter-spacing:0.5px;">{c}</div>' for c in clients)
    sub_b = sub if sub else f"Join {len(clients)*125}+ companies transforming their workforce."
    ads["300x250_B"] = f"""{common_head}
    <div style="width:300px;height:250px;background:white;padding:20px;display:flex;flex-direction:column;justify-content:space-between;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="display:flex;align-items:center;gap:8px;">{logo_light}<span style="font-weight:800;font-size:14px;color:{c_dark};">{name}</span></div>
        <div style="background:{hex_to_rgba(c_pri,0.08)};color:{c_pri};font-size:9px;font-weight:700;padding:4px 10px;text-transform:uppercase;letter-spacing:0.4px;">★ Fortune 500 Trusted</div>
      </div>
      <div style="display:flex;gap:10px;padding:7px 0;border-top:1px solid #f0f0f0;border-bottom:1px solid #f0f0f0;">{client_chips}</div>
      <div style="font-family:'Fraunces',serif;font-size:17px;font-weight:700;line-height:1.3;color:{c_dark};">{highlight_last_words(hl, c_pri)}</div>
      <div style="font-size:10.5px;color:#7a7f94;line-height:1.4;">{sub_b}</div>
      <button style="background:{c_pri};color:white;border:none;padding:10px 18px;font-weight:700;font-size:11.5px;text-align:center;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 300x250 C - Gradient/Benefits
    benefits_html = "".join(f'<div style="display:flex;align-items:center;gap:7px;font-size:11px;color:rgba(255,255,255,0.88);"><div style="width:15px;height:15px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px;flex-shrink:0;">✓</div>{b}</div>' for b in benefits)
    ads["300x250_C"] = f"""{common_head}
    <div style="width:300px;height:250px;padding:20px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;
        background:linear-gradient(160deg,{c_pri},{hex_to_rgba(c_pri,0.7)} 40%,{c_dark});">
      <div style="position:absolute;bottom:-50px;left:-50px;width:180px;height:180px;border:2px solid rgba(255,255,255,0.06);border-radius:50%;pointer-events:none;"></div>
      <div style="padding:4px 12px;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;width:fit-content;background:rgba(255,255,255,0.15);color:white;">Corporate Training</div>
      <div style="font-family:'Fraunces',serif;font-size:20px;font-weight:700;color:white;line-height:1.2;z-index:1;">{hl}</div>
      <div style="display:flex;flex-direction:column;gap:5px;z-index:1;">{benefits_html}</div>
      <button style="background:white;color:{c_pri};border:none;padding:10px 18px;font-weight:700;font-size:11.5px;text-align:center;text-transform:uppercase;letter-spacing:0.4px;font-family:'Outfit',sans-serif;z-index:1;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 728x90 A - Dark
    sub_a = sub if sub else f"{s['stat1']} courses • {s['stat2']} trainers • {s['stat3']} locations worldwide"
    ads["728x90_A"] = f"""{common_head}
    <div style="width:728px;height:90px;display:flex;align-items:center;padding:0 24px;gap:20px;
        background:linear-gradient(90deg,{c_dark} 0%,{hex_to_rgba(c_pri,0.35)} 60%,{c_pri} 100%);">
      <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">{logo_img_tag('dark', 26, fl, 'transparent')}<span style="font-weight:800;font-size:15px;color:white;">{name}</span></div>
      <div style="width:1px;height:46px;background:rgba(255,255,255,0.12);flex-shrink:0;"></div>
      <div style="flex:1;">
        <div style="font-family:'Fraunces',serif;font-size:16px;font-weight:700;color:white;line-height:1.2;">{highlight_last_words(hl, c_acc)}</div>
        <div style="font-size:10.5px;color:rgba(255,255,255,0.5);margin-top:2px;">{sub_a}</div>
      </div>
      <button style="background:linear-gradient(135deg,{c_acc},{c_acc});color:{c_dark};border:none;padding:11px 22px;font-weight:800;font-size:11.5px;text-transform:uppercase;letter-spacing:0.6px;white-space:nowrap;flex-shrink:0;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 728x90 B - Light
    pills_html = "".join(f'<div style="background:{hex_to_rgba(c_pri,0.08)};color:{c_pri};padding:4px 11px;font-size:10px;font-weight:600;white-space:nowrap;">{p}</div>' for p in ["AI & Tech", "Leadership", "Compliance"])
    hl_b = hl if hl else f"Trusted by {', '.join(clients[:3])} & {len(clients)*125}+ Companies"
    sub_lb = sub if sub else "Expert-led corporate training tailored to your goals"
    ads["728x90_B"] = f"""{common_head}
    <div style="width:728px;height:90px;background:white;display:flex;align-items:center;padding:0 24px;gap:16px;border:1px solid #e4e6ec;">
      <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">{logo_light}<span style="font-weight:800;font-size:15px;color:{c_dark};">{name}</span></div>
      <div style="display:flex;gap:6px;flex-shrink:0;">{pills_html}</div>
      <div style="width:1px;height:46px;background:#e4e6ec;flex-shrink:0;"></div>
      <div style="flex:1;">
        <div style="font-family:'Fraunces',serif;font-size:15px;font-weight:700;line-height:1.2;color:{c_dark};">{hl_b}</div>
        <div style="font-size:10px;color:#7a7f94;margin-top:2px;">{sub_lb}</div>
      </div>
      <button style="background:{c_pri};color:white;border:none;padding:11px 22px;font-weight:700;font-size:11.5px;text-transform:uppercase;letter-spacing:0.4px;white-space:nowrap;flex-shrink:0;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 160x600 Skyscraper
    feats_html = ""
    feat_items = [("🎓", f"{s['stat1']} instructor-led courses"), ("🌍", f"Available in {s['stat3']} locations globally"), ("⚡", "AI, Leadership, Compliance & more"), ("🏢", "Customized for your org")]
    for icon, txt in feat_items:
        feats_html += f'<div style="display:flex;align-items:flex-start;gap:6px;text-align:left;"><div style="width:17px;height:17px;background:{hex_to_rgba(c_acc,0.2)};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px;flex-shrink:0;margin-top:1px;">{icon}</div><div style="font-size:10px;color:rgba(255,255,255,0.8);line-height:1.35;">{txt}</div></div>'

    ads["160x600"] = f"""{common_head}
    <div style="width:160px;height:600px;padding:18px 12px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;text-align:center;position:relative;overflow:hidden;
        background:linear-gradient(180deg,{c_dark},{hex_to_rgba(c_pri,0.4)} 40%,{c_pri} 80%,{c_dark});">
      <div style="position:absolute;top:45%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,{hex_to_rgba(c_acc,0.12)},transparent 70%);pointer-events:none;"></div>
      <div>{logo_dark_xl}<div style="font-weight:800;font-size:12px;letter-spacing:0.5px;margin-top:5px;color:rgba(255,255,255,0.85);">{name.upper()}</div></div>
      <div style="font-family:'Fraunces',serif;font-size:18px;font-weight:700;color:white;line-height:1.25;z-index:1;">{hl}</div>
      <div style="display:flex;flex-direction:column;gap:9px;z-index:1;width:100%;">{feats_html}</div>
      <div style="background:rgba(255,255,255,0.07);padding:12px;width:100%;z-index:1;"><div style="font-size:26px;font-weight:800;color:{c_acc};">14+</div><div style="font-size:8.5px;text-transform:uppercase;letter-spacing:0.5px;color:rgba(255,255,255,0.5);">Years of Excellence</div></div>
      <button style="background:linear-gradient(135deg,{c_acc},{c_acc});color:{c_dark};border:none;padding:10px 16px;font-weight:800;font-size:10.5px;text-transform:uppercase;letter-spacing:0.6px;width:100%;z-index:1;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 300x600 Half Page
    cards_html = ""
    card_items = [("🎯", "Customized Programs", "Tailored to your team's exact needs"), ("👨‍🏫", f"{s['stat2']} Expert Trainers", "Industry certified professionals"), ("🔄", "Flexible Delivery", "Virtual, onsite, or hybrid options"), ("📊", "Measurable Impact", "Track ROI with detailed analytics")]
    for icon, title, sub_c in card_items:
        cards_html += f'<div style="display:flex;align-items:center;gap:10px;padding:9px 11px;background:#f6f8fb;border-left:3px solid {c_pri};"><div style="font-size:18px;flex-shrink:0;">{icon}</div><div><div style="font-size:11.5px;font-weight:600;color:{c_dark};line-height:1.3;">{title}</div><div style="font-size:9.5px;color:#7a7f94;font-weight:400;">{sub_c}</div></div></div>'

    sub_hp = sub if sub else "You were exploring our training programs. Let's pick up where you left off."
    ads["300x600"] = f"""{common_head}
    <div style="width:300px;height:600px;background:white;display:flex;flex-direction:column;overflow:hidden;">
      <div style="background:linear-gradient(145deg,{c_dark},{c_pri});padding:24px 22px 20px;flex-shrink:0;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-25px;right:-25px;width:110px;height:110px;border-radius:50%;background:radial-gradient(circle,{hex_to_rgba(c_acc,0.3)},transparent 70%);pointer-events:none;"></div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">{logo_img_tag('dark', 28, fl, 'rgba(255,255,255,0.15)')}<span style="font-weight:800;font-size:14px;color:white;">{name}</span></div>
        <div style="font-family:'Fraunces',serif;font-size:22px;font-weight:700;color:white;line-height:1.2;margin-bottom:6px;">{hl}</div>
        <div style="font-size:11.5px;color:rgba(255,255,255,0.65);line-height:1.4;">{sub_hp}</div>
      </div>
      <div style="padding:18px 22px;flex:1;display:flex;flex-direction:column;justify-content:space-between;">
        <div>
          <div style="font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#7a7f94;margin-bottom:12px;">Why {len(clients)*125}+ Companies Choose {name}</div>
          <div style="display:flex;flex-direction:column;gap:8px;">{cards_html}</div>
        </div>
        <div>
          <div style="display:flex;align-items:center;gap:6px;font-size:9.5px;color:#7a7f94;padding:7px 0;"><div style="width:6px;height:6px;background:#3dd68c;border-radius:50%;"></div>Trusted by {", ".join(clients)} & more</div>
          <button style="background:linear-gradient(135deg,{c_pri},{c_dark});color:white;border:none;padding:13px 20px;font-weight:700;font-size:12.5px;text-align:center;text-transform:uppercase;letter-spacing:0.6px;font-family:'Outfit',sans-serif;width:100%;cursor:pointer;">{cta}</button>
        </div>
      </div>
    </div></body></html>"""

    # 320x50 A - Mobile Dark
    hl_50a = hl if hl else ""
    mob_text = hl_50a if hl_50a else f'<strong style="color:{c_acc};">{s["stat1"]} courses</strong> for your team!'
    ads["320x50_A"] = f"""{common_head}
    <div style="width:320px;height:50px;display:flex;align-items:center;padding:0 12px;gap:8px;overflow:hidden;
        background:linear-gradient(90deg,{c_dark},{c_pri});">
      <div style="display:flex;align-items:center;gap:5px;">{logo_dark_sm}<span style="font-weight:800;font-size:11px;color:white;">{name}</span></div>
      <div style="width:1px;height:22px;background:rgba(255,255,255,0.2);flex-shrink:0;"></div>
      <div style="flex:1;font-size:10px;color:rgba(255,255,255,0.9);font-weight:500;line-height:1.2;">{mob_text}</div>
      <button style="background:{c_acc};color:{c_dark};border:none;padding:5px 10px;font-weight:800;font-size:8.5px;text-transform:uppercase;letter-spacing:0.4px;flex-shrink:0;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    # 320x50 B - Mobile Light
    hl_50b = hl if hl else f'Still looking for <strong style="color:{c_pri};">corporate training?</strong>'
    ads["320x50_B"] = f"""{common_head}
    <div style="width:320px;height:50px;display:flex;align-items:center;padding:0 12px;gap:8px;overflow:hidden;background:white;border:1px solid #e4e6ec;">
      <div style="display:flex;align-items:center;gap:5px;">{logo_light_sm}<span style="font-weight:800;font-size:11px;color:{c_dark};">{name}</span></div>
      <div style="flex:1;font-size:10px;color:#5a6070;font-weight:500;">{hl_50b}</div>
      <button style="background:{c_pri};color:white;border:none;padding:5px 10px;font-weight:800;font-size:8.5px;text-transform:uppercase;letter-spacing:0.4px;flex-shrink:0;font-family:'Outfit',sans-serif;cursor:pointer;">{cta}</button>
    </div></body></html>"""

    return ads.get(ad_id, "")


# ─── Render HTML to PNG via Playwright ───
async def _render_png(html_str, width, height, scale=2):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width + 40, "height": height + 40})
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_str)
            tmp_path = f.name
        await page.goto(f"file://{tmp_path}")
        await page.wait_for_timeout(1200)
        el = await page.query_selector("body > div")
        if not el:
            el = page.locator("body > div").first
        png_bytes = await el.screenshot(type="png")
        await browser.close()
        os.unlink(tmp_path)
        return png_bytes


def render_png(html_str, width, height):
    return asyncio.run(_render_png(html_str, width, height))


# ─── Ad Definitions ───
AD_FORMATS = [
    {"id": "300x250_A", "label": "300×250 — Dark / Urgency",    "w": 300, "h": 250, "cat": "300x250"},
    {"id": "300x250_B", "label": "300×250 — Light / Social Proof", "w": 300, "h": 250, "cat": "300x250"},
    {"id": "300x250_C", "label": "300×250 — Gradient / Benefits",  "w": 300, "h": 250, "cat": "300x250"},
    {"id": "728x90_A",  "label": "728×90 — Dark",               "w": 728, "h": 90,  "cat": "728x90"},
    {"id": "728x90_B",  "label": "728×90 — Light",              "w": 728, "h": 90,  "cat": "728x90"},
    {"id": "160x600",   "label": "160×600 — Skyscraper",        "w": 160, "h": 600, "cat": "160x600"},
    {"id": "300x600",   "label": "300×600 — Half Page",         "w": 300, "h": 600, "cat": "300x600"},
    {"id": "320x50_A",  "label": "320×50 — Mobile Dark",        "w": 320, "h": 50,  "cat": "320x50"},
    {"id": "320x50_B",  "label": "320×50 — Mobile Light",       "w": 320, "h": 50,  "cat": "320x50"},
]


# ─── Per-Ad Editable Fields ───
# Each ad has specific fields that can be overridden individually
AD_FIELDS = {
    "300x250_A": {
        "headline": {"key": "headline1", "label": "Headline", "default_from": "headline1"},
        "cta":      {"key": "cta_text",  "label": "CTA Button", "default_from": "cta_text"},
        "subtext":  {"key": None,        "label": "Subtext", "default": ""},
    },
    "300x250_B": {
        "headline": {"key": "headline2", "label": "Headline", "default_from": "headline2"},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Request a Custom Quote →"},
        "subtext":  {"key": None,        "label": "Subtext", "default": "Join 500+ companies transforming their workforce."},
    },
    "300x250_C": {
        "headline": {"key": "headline3", "label": "Headline", "default_from": "headline3"},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Enquire Now — It's Free →"},
        "benefits": {"key": "benefits",  "label": "Benefits (one per line)", "default_from": "benefits"},
    },
    "728x90_A": {
        "headline": {"key": "headline4", "label": "Headline", "default_from": "headline4"},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Get Free Quote"},
        "subtext":  {"key": None,        "label": "Subtext", "default": ""},
    },
    "728x90_B": {
        "headline": {"key": None,        "label": "Headline", "default": ""},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Enquire Now"},
        "subtext":  {"key": None,        "label": "Subtext", "default": "Expert-led corporate training tailored to your goals"},
    },
    "160x600": {
        "headline": {"key": None,        "label": "Headline", "default": "Upskill Your Entire Workforce"},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Get Free Quote →"},
    },
    "300x600": {
        "headline": {"key": None,        "label": "Hero Headline", "default": "Ready to Transform Your Team's Skills?"},
        "subtext":  {"key": None,        "label": "Hero Subtext", "default": "You were exploring our training programs. Let's pick up where you left off."},
        "cta":      {"key": None,        "label": "CTA Button", "default": "Submit Your Training Enquiry →"},
    },
    "320x50_A": {
        "headline": {"key": None,        "label": "Text", "default": ""},
        "cta":      {"key": None,        "label": "CTA", "default": "Enquire"},
    },
    "320x50_B": {
        "headline": {"key": None,        "label": "Text", "default": "Still looking for corporate training?"},
        "cta":      {"key": None,        "label": "CTA", "default": "Get Quote"},
    },
}

# AI prompt templates per ad style
AD_AI_PRESETS = {
    "🔥 Urgency": {"headline": "Your Team's Growth Can't Wait", "cta": "Get Free Consultation →", "subtext": "Limited slots available — book now", "benefits": "Start training in 48 hours\n5,000+ trainers on standby\nFlexible delivery options"},
    "⭐ Social Proof": {"headline": "Trusted by Fortune 500 Companies", "cta": "Request Custom Quote →", "subtext": "Join 500+ leading companies", "benefits": "Fortune 500 trusted\nRated 4.9/5 by L&D leaders\n14+ years of excellence"},
    "🎯 Benefits": {"headline": "Customized Training. Measurable ROI.", "cta": "Enquire Now — Free →", "subtext": "Tailored programs for your team", "benefits": "Customized programs for your team\n5,000+ certified trainers\nVirtual, onsite, or hybrid"},
    "🔄 Re-engage": {"headline": "Still Searching for Training?", "cta": "Complete Your Enquiry →", "subtext": "Let's pick up where you left off", "benefits": "Zero obligation consultation\n100% customized roadmap\nFree proposal in 24 hours"},
    "◻ Minimal": {"headline": "Corporate Training. Done Right.", "cta": "Learn More →", "subtext": "World-class training, globally delivered", "benefits": "2,000+ instructor-led courses\n100+ global locations\nMeasurable business impact"},
}


def get_ad_val(ad_id, field, fallback=""):
    """Get per-ad override value, or fall back to global session state, or default."""
    override_key = f"ovr_{ad_id}_{field}"
    # Check if there's a per-ad override
    if override_key in st.session_state and st.session_state[override_key]:
        return st.session_state[override_key]
    # Fall back to global
    field_def = AD_FIELDS.get(ad_id, {}).get(field, {})
    if field_def.get("default_from"):
        return st.session_state.get(field_def["default_from"], fallback)
    return field_def.get("default", fallback)


def init_ad_overrides():
    """Initialize override keys in session state if not present."""
    for ad_id in AD_FIELDS:
        for field in AD_FIELDS[ad_id]:
            key = f"ovr_{ad_id}_{field}"
            if key not in st.session_state:
                st.session_state[key] = ""


# ─── OpenRouter LLM Config ───
OPENROUTER_MODELS = {
    "Claude 4 Sonnet (Recommended)": "anthropic/claude-sonnet-4",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Claude 3.5 Haiku (Fast)": "anthropic/claude-3.5-haiku",
    "GPT-4o": "openai/gpt-4o",
    "GPT-4o Mini (Fast)": "openai/gpt-4o-mini",
    "Gemini 2.0 Flash": "google/gemini-2.0-flash-001",
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat-v3-0324",
}

if "openrouter_api_key" not in st.session_state:
    st.session_state["openrouter_api_key"] = ""
if "openrouter_model" not in st.session_state:
    st.session_state["openrouter_model"] = "Claude 4 Sonnet (Recommended)"


def call_llm(prompt, system_prompt="", max_tokens=1000):
    """Call OpenRouter API and return the response text."""
    api_key = st.session_state.get("openrouter_api_key", "")
    if not api_key:
        return None

    model = OPENROUTER_MODELS.get(st.session_state.get("openrouter_model", ""), "anthropic/claude-sonnet-4")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://edstellar.com",
                "X-Title": "Edstellar AdRoll Creative Studio",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.8,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"LLM API Error: {str(e)}")
        return None


AD_SYSTEM_PROMPT = """You are an expert ad copywriter for corporate training retargeting ads.
You write for Edstellar, a global corporate training company with 2000+ courses, 5000+ trainers, 100+ locations, and Fortune 500 clients like Visa, Microsoft, Amazon, Intel.

The ads target HR/L&D professionals who visited Edstellar training pages but didn't enquire. Goal: make them come back and submit an enquiry.

RULES:
- Headlines must be punchy, under 8 words
- CTAs must be action-oriented, under 6 words
- Subtexts must be 1 short sentence
- Benefits must be 3 bullet points, each under 8 words
- Never use quotes or special characters
- Return ONLY valid JSON, no markdown"""


def generate_ad_content_llm(prompt, ad_id=None, ad_label=""):
    """Use LLM to generate ad content. Returns dict with headline, cta, subtext, benefits."""
    fields_needed = list(AD_FIELDS.get(ad_id, {}).keys()) if ad_id else ["headline", "cta", "subtext", "benefits"]

    user_prompt = f"""Generate ad copy for a retargeting display ad.
Ad format: {ad_label or 'General'}
User request: {prompt}

Company context: {st.session_state.get('company_name', 'Edstellar')} - corporate training company.
Stats: {st.session_state.get('stat1','2000+')} courses, {st.session_state.get('stat2','5000+')} trainers, {st.session_state.get('stat3','100+')} locations.

Return ONLY a JSON object with these fields (include only the ones listed):
{json.dumps({f: "string value" for f in fields_needed})}

For "benefits", return a string with items separated by newlines.
Return ONLY the JSON, no other text."""

    result = call_llm(user_prompt, AD_SYSTEM_PROMPT, max_tokens=500)
    if not result:
        return None

    # Parse JSON from response
    try:
        # Clean up response - extract JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        return json.loads(result)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        try:
            start = result.index("{")
            end = result.rindex("}") + 1
            return json.loads(result[start:end])
        except (ValueError, json.JSONDecodeError):
            st.error("Failed to parse LLM response. Using preset fallback.")
            return None


def generate_all_ads_llm(prompt):
    """Use LLM to generate content for ALL ad creatives at once."""
    user_prompt = f"""Generate ad copy for 9 retargeting display ads for a corporate training company.
User request: {prompt}

Company: {st.session_state.get('company_name', 'Edstellar')}
Stats: {st.session_state.get('stat1','2000+')} courses, {st.session_state.get('stat2','5000+')} trainers, {st.session_state.get('stat3','100+')} locations.
Clients: {st.session_state.get('clients', 'VISA, MICROSOFT, AMAZON, INTEL')}

Generate content for these ad formats. Return ONLY a JSON object:
{{
  "headline1": "headline for 300x250 dark urgency ad (max 8 words)",
  "headline2": "headline for 300x250 light social proof ad (max 8 words)",
  "headline3": "headline for 300x250 gradient benefits ad (max 6 words)",
  "headline4": "headline for 728x90 leaderboard ad (max 8 words)",
  "cta_text": "main CTA button text (max 5 words with arrow)",
  "benefits": "benefit 1\\nbenefit 2\\nbenefit 3"
}}

Return ONLY the JSON, no other text."""

    result = call_llm(user_prompt, AD_SYSTEM_PROMPT, max_tokens=600)
    if not result:
        return None

    try:
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        return json.loads(result)
    except json.JSONDecodeError:
        try:
            start = result.index("{")
            end = result.rindex("}") + 1
            return json.loads(result[start:end])
        except (ValueError, json.JSONDecodeError):
            return None


def has_llm():
    """Check if OpenRouter API key is configured."""
    return bool(st.session_state.get("openrouter_api_key", ""))


init_ad_overrides()
with st.sidebar:
    st.markdown("### ✦ AdRoll Creative Studio")
    st.caption("Build & download retargeting ad creatives")

    # ── Logo Upload ──
    st.markdown('<div class="section-label">Company Logos</div>', unsafe_allow_html=True)

    col_d, col_l = st.columns(2)
    with col_d:
        st.markdown("**☀️ For Dark BG**")
        st.caption("Light / white logo")
        logo_dark_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg", "svg", "webp"], key="logo_dark_up", label_visibility="collapsed")
        if logo_dark_file:
            st.session_state["logo_dark_data"] = logo_dark_file.read()
            st.image(st.session_state["logo_dark_data"], width=80)

    with col_l:
        st.markdown("**🌙 For Light BG**")
        st.caption("Dark / colored logo")
        logo_light_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg", "svg", "webp"], key="logo_light_up", label_visibility="collapsed")
        if logo_light_file:
            st.session_state["logo_light_data"] = logo_light_file.read()
            st.image(st.session_state["logo_light_data"], width=80)

    # ── AI / LLM Config ──
    st.markdown('<div class="section-label">🤖 AI Model (OpenRouter)</div>', unsafe_allow_html=True)

    api_key_input = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.get("openrouter_api_key", ""),
        type="password",
        placeholder="sk-or-v1-...",
        help="Get your key at openrouter.ai/keys",
    )
    if api_key_input != st.session_state.get("openrouter_api_key", ""):
        st.session_state["openrouter_api_key"] = api_key_input

    if has_llm():
        st.session_state["openrouter_model"] = st.selectbox(
            "Model",
            list(OPENROUTER_MODELS.keys()),
            index=list(OPENROUTER_MODELS.keys()).index(st.session_state.get("openrouter_model", "Claude 4 Sonnet (Recommended)")),
        )
        st.success(f"✅ Connected — {st.session_state['openrouter_model']}")
    else:
        st.caption("Add API key to enable AI-powered ad copy generation. Without a key, quick presets are still available.")
        st.markdown("[🔑 Get OpenRouter API Key](https://openrouter.ai/keys)", unsafe_allow_html=True)

    # ── AI Prompt ──
    st.markdown('<div class="section-label">AI Creative Prompt</div>', unsafe_allow_html=True)

    preset = st.selectbox("Quick Presets", ["— Select —"] + list(PRESETS.keys()), label_visibility="collapsed")
    if preset != "— Select —":
        for k, val in PRESETS[preset].items():
            st.session_state[k] = val
        st.rerun()

    ai_prompt = st.text_area(
        "Describe your ad",
        placeholder="e.g. Create urgency-based retargeting ads for corporate AI training programs...",
        height=100,
        label_visibility="collapsed",
    )
    if st.button("✨ Generate from Prompt", use_container_width=True, type="primary"):
        if ai_prompt:
            if has_llm():
                # ── Use LLM ──
                with st.spinner(f"🤖 Generating with {st.session_state['openrouter_model']}..."):
                    result = generate_all_ads_llm(ai_prompt)
                    if result:
                        for k in ["headline1", "headline2", "headline3", "headline4", "cta_text", "benefits"]:
                            if k in result and result[k]:
                                st.session_state[k] = result[k]
                        st.toast("✅ AI generated all ad content!")
                    else:
                        st.warning("LLM failed — falling back to preset matching")
                        # Fallback to preset
                        lower = ai_prompt.lower()
                        picked = "🎯 Benefits"
                        if any(w in lower for w in ["urgent", "hurry", "limited", "fast", "now"]):
                            picked = "🔥 Urgency"
                        elif any(w in lower for w in ["trust", "client", "social", "proof", "fortune"]):
                            picked = "⭐ Social Proof"
                        elif any(w in lower for w in ["re-engage", "retarget", "come back", "welcome", "still"]):
                            picked = "🔄 Re-engage"
                        elif any(w in lower for w in ["clean", "minimal", "simple", "subtle"]):
                            picked = "◻ Minimal"
                        for k, val in PRESETS[picked].items():
                            st.session_state[k] = val
                        st.toast(f'Applied "{picked}" preset as fallback')
            else:
                # ── No API key — use preset matching ──
                lower = ai_prompt.lower()
                picked = "🎯 Benefits"
                if any(w in lower for w in ["urgent", "hurry", "limited", "fast", "now"]):
                    picked = "🔥 Urgency"
                elif any(w in lower for w in ["trust", "client", "social", "proof", "fortune"]):
                    picked = "⭐ Social Proof"
                elif any(w in lower for w in ["re-engage", "retarget", "come back", "welcome", "still"]):
                    picked = "🔄 Re-engage"
                elif any(w in lower for w in ["clean", "minimal", "simple", "subtle"]):
                    picked = "◻ Minimal"
                for k, val in PRESETS[picked].items():
                    st.session_state[k] = val
                if "red" in lower: st.session_state["color_accent"] = "#EF4444"
                if "green" in lower: st.session_state["color_accent"] = "#10B981"
                if "purple" in lower: st.session_state["color_primary"] = "#7C3AED"
                if "orange" in lower: st.session_state["color_accent"] = "#F97316"
                if "teal" in lower: st.session_state["color_primary"] = "#0D9488"
                st.toast(f'Applied "{picked}" style (add API key for AI generation)')
            st.rerun()

    # ── Content Settings ──
    st.markdown('<div class="section-label">Content Settings</div>', unsafe_allow_html=True)

    st.session_state["company_name"] = st.text_input("Company Name", st.session_state["company_name"])
    st.session_state["headline1"] = st.text_input("Headline (Dark)", st.session_state["headline1"])
    st.session_state["headline2"] = st.text_input("Headline (Light)", st.session_state["headline2"])
    st.session_state["headline3"] = st.text_input("Headline (Gradient)", st.session_state["headline3"])
    st.session_state["headline4"] = st.text_input("Headline (Leaderboard)", st.session_state["headline4"])
    st.session_state["cta_text"] = st.text_input("CTA Button Text", st.session_state["cta_text"])

    c1, c2 = st.columns(2)
    with c1:
        st.session_state["stat1"] = st.text_input("Stat 1", st.session_state["stat1"])
        st.session_state["stat2"] = st.text_input("Stat 2", st.session_state["stat2"])
        st.session_state["stat3"] = st.text_input("Stat 3", st.session_state["stat3"])
    with c2:
        st.session_state["stat_label1"] = st.text_input("Label 1", st.session_state["stat_label1"])
        st.session_state["stat_label2"] = st.text_input("Label 2", st.session_state["stat_label2"])
        st.session_state["stat_label3"] = st.text_input("Label 3", st.session_state["stat_label3"])

    # ── Colors ──
    st.markdown('<div class="section-label">Brand Colors</div>', unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.session_state["color_primary"] = st.color_picker("Primary", st.session_state["color_primary"])
    with cc2:
        st.session_state["color_dark"] = st.color_picker("Dark", st.session_state["color_dark"])
    with cc3:
        st.session_state["color_accent"] = st.color_picker("Accent", st.session_state["color_accent"])

    # ── Clients & Benefits ──
    st.markdown('<div class="section-label">Clients & Benefits</div>', unsafe_allow_html=True)
    st.session_state["clients"] = st.text_input("Client Names (comma separated)", st.session_state["clients"])
    st.session_state["benefits"] = st.text_area("Benefits (one per line)", st.session_state["benefits"], height=80)


# ═══════════════════════════════════════
# ─── MAIN AREA ───
# ═══════════════════════════════════════

# Topbar
st.markdown("""
<div class="topbar-custom">
    <div class="logo">✦</div>
    <div class="title">AdRoll Creative Studio<span class="subtitle">by Edstellar</span></div>
</div>
""", unsafe_allow_html=True)

# Filter tabs
filter_options = ["All", "300×250", "728×90", "160×600", "300×600", "320×50"]
filter_map = {"All": None, "300×250": "300x250", "728×90": "728x90", "160×600": "160x600", "300×600": "300x600", "320×50": "320x50"}
selected_filter = st.radio("Format Filter", filter_options, horizontal=True, label_visibility="collapsed")
active_cat = filter_map[selected_filter]

st.markdown("---")

# ── Generate & Download All ──
if st.button("⬇ Generate & Download All PNGs (ZIP)", use_container_width=True, type="primary"):
    with st.spinner("Rendering all 9 creatives... This takes ~30 seconds"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for ad in AD_FORMATS:
                html = generate_ad_html(ad["id"], ad["w"], ad["h"])
                png_bytes = render_png(html, ad["w"], ad["h"])
                zf.writestr(f"Edstellar_{ad['id']}.png", png_bytes)
        zip_buffer.seek(0)
        st.download_button(
            label="📦 Download ZIP with all 9 creatives",
            data=zip_buffer,
            file_name="Edstellar_AdRoll_Creatives.zip",
            mime="application/zip",
            use_container_width=True,
        )
        st.success("All 9 creatives rendered! Click above to download.")

st.markdown("")

# ── Render Ad Previews ──
filtered_ads = [a for a in AD_FORMATS if active_cat is None or a["cat"] == active_cat]


def render_ad_card(a):
    """Render a single ad card with preview, AI prompt expander, and download button."""
    ad_id = a["id"]

    st.markdown(f'<div class="ad-card-title">{a["label"]} <span class="size-badge">{a["w"]}×{a["h"]}</span></div>', unsafe_allow_html=True)

    # Preview
    html = generate_ad_html(ad_id, a["w"], a["h"])
    st.components.v1.html(html, width=a["w"] + 4, height=a["h"] + 4, scrolling=False)

    # ── Per-Ad AI Prompt Expander ──
    with st.expander(f"✏️ Edit content for {a['label']}", expanded=False):
        fields = AD_FIELDS.get(ad_id, {})

        # Quick AI preset selector for this ad
        ai_col1, ai_col2 = st.columns([2, 1])
        with ai_col1:
            ad_prompt = st.text_input(
                "AI Prompt",
                placeholder="e.g. Make this urgency-focused with a strong CTA...",
                key=f"aiprompt_{ad_id}",
                label_visibility="collapsed",
            )
        with ai_col2:
            if st.button("✨ Apply", key=f"aigen_{ad_id}", use_container_width=True):
                if ad_prompt:
                    if has_llm():
                        # ── Use LLM for this specific ad ──
                        with st.spinner(f"🤖 Generating..."):
                            result = generate_ad_content_llm(ad_prompt, ad_id, a["label"])
                            if result:
                                for f in fields:
                                    if f in result and result[f]:
                                        st.session_state[f"ovr_{ad_id}_{f}"] = result[f]
                                st.toast(f"✅ AI updated {a['label']}")
                                st.rerun()
                            else:
                                st.warning("LLM failed — using preset fallback")
                    # Fallback: keyword matching to presets
                    if not has_llm() or not result:
                        lower = ad_prompt.lower()
                        picked = "🎯 Benefits"
                        if any(w in lower for w in ["urgent", "hurry", "limited", "fast", "now", "rush"]):
                            picked = "🔥 Urgency"
                        elif any(w in lower for w in ["trust", "client", "social", "proof", "fortune", "company"]):
                            picked = "⭐ Social Proof"
                        elif any(w in lower for w in ["re-engage", "retarget", "come back", "welcome", "still", "return"]):
                            picked = "🔄 Re-engage"
                        elif any(w in lower for w in ["clean", "minimal", "simple", "subtle", "short"]):
                            picked = "◻ Minimal"

                        preset = AD_AI_PRESETS[picked]
                        if "headline" in fields:
                            st.session_state[f"ovr_{ad_id}_headline"] = preset.get("headline", "")
                        if "cta" in fields:
                            st.session_state[f"ovr_{ad_id}_cta"] = preset.get("cta", "")
                        if "subtext" in fields:
                            st.session_state[f"ovr_{ad_id}_subtext"] = preset.get("subtext", "")
                        if "benefits" in fields:
                            st.session_state[f"ovr_{ad_id}_benefits"] = preset.get("benefits", "")

                        st.toast(f'Applied "{picked}" to {a["label"]}')
                        st.rerun()

        # Quick preset chips
        preset_cols = st.columns(5)
        for idx, (pname, pdata) in enumerate(AD_AI_PRESETS.items()):
            with preset_cols[idx]:
                if st.button(pname, key=f"qp_{ad_id}_{idx}", use_container_width=True):
                    if "headline" in fields:
                        st.session_state[f"ovr_{ad_id}_headline"] = pdata.get("headline", "")
                    if "cta" in fields:
                        st.session_state[f"ovr_{ad_id}_cta"] = pdata.get("cta", "")
                    if "subtext" in fields:
                        st.session_state[f"ovr_{ad_id}_subtext"] = pdata.get("subtext", "")
                    if "benefits" in fields:
                        st.session_state[f"ovr_{ad_id}_benefits"] = pdata.get("benefits", "")
                    st.rerun()

        st.markdown("---")

        # Editable fields for this specific ad
        for field_name, field_def in fields.items():
            ovr_key = f"ovr_{ad_id}_{field_name}"
            current = st.session_state.get(ovr_key, "")
            # Show placeholder from global setting
            global_key = field_def.get("default_from")
            placeholder = st.session_state.get(global_key, field_def.get("default", "")) if global_key else field_def.get("default", "")

            if field_name == "benefits":
                new_val = st.text_area(
                    field_def["label"],
                    value=current,
                    placeholder=f"Leave empty to use global: {placeholder[:60]}...",
                    height=70,
                    key=f"edit_{ovr_key}",
                )
            else:
                new_val = st.text_input(
                    field_def["label"],
                    value=current,
                    placeholder=f"Global: {placeholder[:50]}",
                    key=f"edit_{ovr_key}",
                )

            if new_val != current:
                st.session_state[ovr_key] = new_val

        # Reset button
        if st.button(f"🔄 Reset to global defaults", key=f"reset_{ad_id}"):
            for field_name in fields:
                st.session_state[f"ovr_{ad_id}_{field_name}"] = ""
            st.rerun()

    # Download button
    if st.button(f"⬇ Download {ad_id}.png", key=f"dl_{ad_id}"):
        with st.spinner("Rendering..."):
            png = render_png(html, a["w"], a["h"])
            st.download_button(f"💾 Save {ad_id}.png", png, f"Edstellar_{ad_id}.png", "image/png", key=f"save_{ad_id}")


# ── Layout: Group ads smartly into rows ──
i = 0
while i < len(filtered_ads):
    ad = filtered_ads[i]

    if ad["w"] <= 320 and ad["h"] <= 250:
        # Small ads: 2 per row
        if i + 1 < len(filtered_ads) and filtered_ads[i + 1]["w"] <= 320 and filtered_ads[i + 1]["h"] <= 250:
            col1, col2 = st.columns(2)
            with col1:
                render_ad_card(filtered_ads[i])
            with col2:
                render_ad_card(filtered_ads[i + 1])
            i += 2
            continue
        else:
            render_ad_card(ad)
    elif ad["w"] >= 700:
        render_ad_card(ad)
    else:
        # Tall ads: side by side if two available
        if ad["h"] > 300 and i + 1 < len(filtered_ads) and filtered_ads[i + 1]["h"] > 300:
            col1, col2 = st.columns(2)
            with col1:
                render_ad_card(filtered_ads[i])
            with col2:
                render_ad_card(filtered_ads[i + 1])
            i += 2
            continue
        else:
            render_ad_card(ad)

    i += 1
    st.markdown("")
