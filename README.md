# 📖 KDPEasy Story Composer

Tool #3 in the **KDPEasy Suite** — compose finished storybook
pages (image + fairy-tale text + decorative frame) from your
chatbot output, ready to feed into the PDF Builder.

**Live app:** https://kdpeasy-story-composer.streamlit.app

---

## 🇻🇳 Hướng dẫn deploy (dành cho anh chủ tool)

### Bước 1 — Tạo repo mới trên GitHub
1. Mở https://github.com/new
2. **Repository name:** `kdpeasy-story-composer`
3. **Public** ✅
4. ✅ Tick "Add a README file"
5. Bấm **Create repository**

### Bước 2 — Upload 3 file vào repo
Trong repo vừa tạo, bấm **Add file → Upload files**, kéo cả 3 file
trong thư mục `C:\Users\Admin\Downloads\KDPEasy-Story-Composer\` lên:

- `app.py`
- `requirements.txt`
- `README.md`

Bấm **Commit changes**.

### Bước 3 — Deploy lên Streamlit Cloud
1. Mở https://share.streamlit.io
2. Bấm **Create app → Deploy a public app from GitHub**
3. **Repository:** `daodinhthe1989-blip/kdpeasy-story-composer`
4. **Branch:** `main`
5. **Main file path:** `app.py`
6. **App URL:** `kdpeasy-story-composer`
7. Bấm **Deploy**

Đợi ~2 phút. Mật khẩu vào tool: **`KDPSTORY2026`**

> 💡 Tool #3 **KHÔNG cần** API token Replicate. Free 100%.
> Lần đầu mở app sẽ tải font Cinzel + Cormorant Garamond từ
> Google Fonts (~5 giây).

---

## 🇺🇸 How customers use it

### What it does
Turns your chatbot text + ChatGPT-generated images into a
finished storybook layout with fairy-tale fonts, drop caps,
and a decorative frame. Outputs one PNG per page; feed those
PNGs into the **KDPEasy PDF Builder** to get the final KDP
PDF.

### Step-by-step
1. **Unlock** with the VIP password.
2. **Pick page size** in the sidebar (8.5×8.5 is the classic
   square children's book — used by most KDP bestsellers).
3. **Pick a style:**
   - **Decorative frame** — Ornate (border + stars) recommended.
   - **Drop cap** — big fancy first letter (keep on).
   - **Font scale** — bump up if text feels small.
4. **Compose page 1:**
   - Paste the page text from your chatbot.
   - Upload the ChatGPT-generated illustration for that page.
   - Pick a layout: A (image top), B (image left), C (full-bleed),
     or D (oval).
   - Watch the **live preview** on the right.
5. **Press ➕** to add page 2. Repeat.
6. **Reorder / duplicate / delete** any page with the buttons.
7. **Click "Build PNG ZIP"** → download.
8. **Open the [KDPEasy PDF Builder](https://kdpeasy-pdf-builder.streamlit.app)**,
   upload the PNG ZIP contents → build PDF → upload to KDP.

### Recommended settings for a 24-page fairy-tale book
- Page size: **8.5 × 8.5 in (Square)**
- Frame: **Ornate**
- Drop cap: **On**
- Font scale: **1.0**
- Line spacing: **1.35**
- Mix layouts: A for narrative pages, C for spreads, D for
  the title page or epilogue.

---

## 🔗 Full KDPEasy workflow

```
ChatGPT or your custom chatbot
        ↓ (generates story text + image prompts)
ChatGPT image generation
        ↓ (turn prompts into illustrations)
KDPEasy Story Composer  ← you are here
        ↓ (PNG per page)
KDPEasy PDF Builder
        ↓ (combine into KDP-ready PDF)
Amazon KDP upload
```

---

## 🛠️ Tech stack
- **Streamlit** — UI
- **Pillow** — image compositing, drop cap, fairy-tale frame
- **requests** — fetches Cinzel + Cormorant Garamond fonts on
  first run (Google Fonts OFL license)

No paid APIs. Runs free on Streamlit Cloud.

---

Made with ❤️ by **KDPEasy Studio** for KDP storytellers.
