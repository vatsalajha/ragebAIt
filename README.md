<div align="center">

![ragebAIt Hero](.github/assets/hero.png)

# 🎬 ragebAIt

**AI Sports Miscommentary Generator - Turn any sports clip into comedy gold.**

[![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![AI](https://img.shields.io/badge/AI-Gemini%20%26%20fal.ai-blue?style=for-the-badge)](https://fal.ai)

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started)

</div>

---

## ⚡ Features

- **🎙️ AI Commentary**: Instantly generate hilarious, ironic, or just plain weird sports commentary for any short clip.
- **🎭 Parody Engine**: One-click AI parody video generation. Turn a tense sports moment into a surreal comedy sketch.
- **🖼️ Meme Studio**: Powered by Nano Banana, generate relevant sports memes in seconds.
- **🔊 Comedic TTS**: Multiple distinct "miscommentator" personalities with expressive, high-quality voices.

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion
- **Components**: Radix UI + Lucide Icons

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **LLM**: Google Gemini 1.5 Pro
- **Media Generation**: [fal.ai](https://fal.ai) (Minimax for Image-to-Video)
- **Meme Generation**: Nano Banana API

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys: `GEMINI_API_KEY`, `FAL_KEY`

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vatsalajha/ragebAIt.git
   cd ragebAIt
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp .env.example .env # Add your keys here
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 📖 API Documentation

Once the backend is running, you can access the interactive Swagger docs at:
`http://localhost:8000/docs`

---

<div align="center">
Built with ❤️ by the ragebAIt team
</div>
