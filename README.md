# 🚀 Headstart - Your Hackathon Architect

Transform raw hackathon ideas into comprehensive **Project Design & Requirements (PDR)** documents in minutes.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)

## ✨ What is Headstart?

Headstart is an autonomous AI-powered tool that takes your rough hackathon idea and generates a complete, actionable project specification. It's like having a senior solutions architect and technical researcher working together to plan your project.

### Key Features

- 🎯 **Strategic Gap Analysis** - Identifies what already exists so you don't reinvent the wheel
- 💡 **Winning Features** - Suggests USPs that will impress hackathon judges
- 💸 **Free Tier Focus** - Prioritizes FREE and open-source tools (crucial for student hackathons)
- ✅ **Fact Verification** - Validates claims about free tiers with citations
- 📋 **Copy-Paste Ready** - Outputs clean Markdown you can feed directly to an LLM to start coding

## 🏗️ Architecture

Headstart uses a **Hub-and-Spoke multi-agent architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│              "AI-powered waste sorting app"                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 AGENT 1: THE PLANNER                        │
│                   (sonar-reasoning-pro)                     │
│         Breaks idea into 3 research angles                  │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   REPORTER 1      │ │   REPORTER 2      │ │   REPORTER 3      │
│   Market Gap      │ │   Tech Stack      │ │   Wow Factor      │
│   (sonar-pro)     │ │   (sonar-pro)     │ │   (sonar-pro)     │
└───────────────────┘ └───────────────────┘ └───────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               AGENT 3: FACTS CHECKER                        │
│         Validates free-tier claims & citations              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│             AGENT 4: EDITOR-IN-CHIEF                        │
│                    (sonar-pro)                              │
│            Synthesizes final PDR document                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL PDR OUTPUT                         │
│   Executive Summary | Tech Stack | Feature Roadmap | etc.  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- Perplexity API key ([Get one here](https://www.perplexity.ai/settings/api))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/headstart.git
   cd headstart
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key**
   
   Create a `.env` file in the project root:
   ```env
   PERPLEXITY_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   
   Navigate to `http://localhost:7860`

## 📖 Usage

1. **Enter your idea** - Describe your hackathon project in the text box
   - Example: *"AI-powered waste sorting app for college campuses"*

2. **Click Generate PDR** - Watch as the agents work through:
   - Planning research angles
   - Researching in parallel
   - Verifying tool claims
   - Synthesizing the final document

3. **Copy your PDR** - Click the copy button and paste into your favorite LLM to start coding!

## 📄 PDR Output Structure

The generated PDR includes:

| Section | Description |
|---------|-------------|
| **Executive Summary** | Elevator pitch for your project |
| **Competitive Landscape** | What exists vs. why yours is better |
| **Tech Stack** | Recommended tools labeled FREE/PAID |
| **Feature Roadmap** | Phase 1 (MVP) vs Phase 2 (Winning Features) |
| **Implementation Steps** | Step-by-step guide to build it |
| **Risk Mitigation** | Potential issues and solutions |
| **Demo Script** | How to present to judges |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PERPLEXITY_API_KEY` | Your Perplexity API key | Yes |

### Models Used

| Agent | Model | Purpose |
|-------|-------|---------|
| Planner | `sonar-reasoning-pro` | Strategic analysis |
| Reporters | `sonar-pro` | Research & discovery |
| Editor | `sonar-pro` | Document synthesis |

## 📁 Project Structure

```
headstart/
├── app.py              # Main application (single-file architecture)
├── requirements.txt    # Python dependencies
├── .env               # API keys (not committed)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🤝 Contributing


## 🙏 Acknowledgments

- Powered by [Perplexity AI](https://www.perplexity.ai/)
- Built with [Gradio](https://gradio.app/)

---

**Made with ❤️ for hackathon enthusiasts**
