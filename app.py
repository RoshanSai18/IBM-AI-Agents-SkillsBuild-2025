"""
Headstart: Turn hackathon ideas into actionable project specs.
"""

import asyncio
import json
import os
import re

import gradio as gr
import httpx
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
MODEL_REASONING = "sonar-reasoning-pro"
MODEL_RESEARCH = "sonar-pro"

KNOWN_TOOLS = [
    "Firebase", "Supabase", "MongoDB", "PostgreSQL", "Redis",
    "OpenAI", "Anthropic", "Hugging Face", "Replicate", "Groq",
    "Stripe", "PayPal", "Twilio", "SendGrid", "Mailgun",
    "Vercel", "Netlify", "Railway", "Render", "Fly.io",
    "AWS", "GCP", "Azure", "Cloudflare", "DigitalOcean",
    "React", "Vue", "Svelte", "Next.js", "Nuxt",
    "FastAPI", "Flask", "Django", "Express", "Node.js",
    "TensorFlow", "PyTorch", "Scikit-learn", "OpenCV",
    "Polygon", "Ethereum", "Solana", "Metamask", "Web3.js",
    "GitHub", "GitLab", "Docker", "Kubernetes"
]


async def call_perplexity(messages, model=MODEL_RESEARCH):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": messages}
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def planner(user_idea, log):
    await log("🎯 **Planner**: Analyzing your idea...")
    
    system = """You are a Hackathon Mentor. Break down the user's idea into exactly 3 research angles.

Respond with JSON only:
{
    "angles": [
        "Market Gap: What exists and what's missing?",
        "Tech Stack: What FREE tools fit this?", 
        "Wow Factor: What will impress judges?"
    ]
}"""

    user = f"Hackathon idea: '{user_idea}'\n\nBreak this into 3 research angles."
    
    try:
        response = await call_perplexity(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            model=MODEL_REASONING
        )
        
        match = re.search(r'\{[\s\S]*"angles"[\s\S]*\}', response)
        if match:
            angles = json.loads(match.group()).get("angles", [])
            if len(angles) >= 3:
                await log("✅ **Planner**: Found 3 research angles")
                for i, angle in enumerate(angles[:3], 1):
                    await log(f"   {i}. {angle[:80]}...")
                return angles[:3]
        
        await log("⚠️ **Planner**: Using fallback angles")
        return [user_idea, f"Tech stack for {user_idea}", f"Unique features for {user_idea}"]
        
    except Exception as e:
        await log(f"❌ **Planner Error**: {e}")
        return [
            f"Existing solutions for {user_idea}",
            f"Free tools for {user_idea}",
            f"Innovative features for {user_idea}"
        ]


async def reporter(angle, reporter_id, log):
    await log(f"🔍 **Reporter {reporter_id}**: Researching '{angle[:50]}...'")
    
    system = """You are a Technical Researcher for hackathons.
Prioritize FREE and OPEN SOURCE tools.

For each tool mentioned, state: FREE, FREE TIER, OPEN SOURCE, or PAID.
Include citation numbers [1], [2] for claims.

Structure:
## Existing Solutions
## Gap Analysis  
## Recommended Tools & APIs
## Key Insights"""

    user = f"""Research: '{angle}'

Find:
1. Existing solutions (name competitors)
2. Gaps in current offerings
3. FREE/OPEN SOURCE tools
4. Gotchas (rate limits, costs)"""

    try:
        response = await call_perplexity(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        )
        tools = extract_tools(response)
        await log(f"✅ **Reporter {reporter_id}**: Found {len(tools)} tools")
        
        return {
            "reporter_id": reporter_id,
            "angle": angle,
            "findings": response,
            "tools": tools,
            "status": "success"
        }
    except Exception as e:
        await log(f"❌ **Reporter {reporter_id} Error**: {e}")
        return {
            "reporter_id": reporter_id,
            "angle": angle,
            "findings": f"Research failed: {e}",
            "tools": [],
            "status": "error"
        }


def extract_tools(text):
    tools = []
    text_lower = text.lower()
    
    for tool in KNOWN_TOOLS:
        if tool.lower() in text_lower:
            idx = text_lower.find(tool.lower())
            context = text_lower[max(0, idx-50):idx+100]
            
            if "free tier" in context:
                tier = "FREE TIER"
            elif "free" in context:
                tier = "FREE"
            elif "open source" in context:
                tier = "OPEN SOURCE"
            elif "paid" in context:
                tier = "PAID"
            else:
                tier = "Unknown"
            
            if not any(t["name"] == tool for t in tools):
                tools.append({"name": tool, "tier": tier, "verified": False})
    
    return tools


async def run_reporters(angles, log):
    await log("\n📡 **Dispatching 3 Reporters...**\n")
    
    async def staggered(angle, idx):
        await asyncio.sleep(idx * 1.0)
        return await reporter(angle, idx + 1, log)
    
    tasks = [staggered(angle, i) for i, angle in enumerate(angles)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    processed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed.append({
                "reporter_id": i + 1,
                "angle": angles[i],
                "findings": f"Error: {result}",
                "tools": [],
                "status": "error"
            })
        else:
            processed.append(result)
    
    return processed


def facts_checker(reports, log):
    log("🔎 **FactsChecker**: Validating claims...")
    
    all_tools = []
    verified_reports = []
    
    for report in reports:
        if report["status"] == "error":
            verified_reports.append(report)
            continue
        
        findings = report["findings"]
        tools = report["tools"]
        
        for tool in tools:
            name = tool["name"]
            has_citation = bool(re.search(rf'{re.escape(name)}[^[]*\[\d+\]', findings, re.IGNORECASE))
            
            if tool["tier"] in ["FREE", "FREE TIER", "OPEN SOURCE"]:
                free_cited = bool(re.search(rf'{re.escape(name)}[^[]*(?:free|open source)[^[]*\[\d+\]', findings, re.IGNORECASE))
                if free_cited:
                    tool["verified"] = True
                    tool["status"] = "✅ Verified"
                elif has_citation:
                    tool["verified"] = True
                    tool["status"] = "✅ Cited"
                else:
                    tool["status"] = "⚠️ Needs Verification"
            else:
                tool["verified"] = has_citation
                tool["status"] = "✅ Cited" if has_citation else "ℹ️ Uncited"
            
            if not any(t["name"] == name for t in all_tools):
                all_tools.append(tool)
        
        modified = findings
        for tool in tools:
            if not tool.get("verified") and tool["tier"] in ["FREE", "FREE TIER"]:
                modified = re.sub(
                    rf'({re.escape(tool["name"])})',
                    r'\1 *(Verify)*',
                    modified, count=1, flags=re.IGNORECASE
                )
        
        verified_reports.append({**report, "findings": modified, "tools": tools})
    
    verified = sum(1 for t in all_tools if t.get("verified"))
    log(f"✅ **FactsChecker**: {verified}/{len(all_tools)} verified")
    
    return verified_reports, all_tools


async def editor(user_idea, reports, tools, log):
    await log("\n📝 **Editor**: Writing PDR...\n")
    
    research = "\n\n".join(
        f"### {r['angle']}\n\n{r['findings']}"
        for r in reports if r["status"] == "success"
    )
    
    tool_list = "\n".join(f"- {t['name']}: {t['tier']} {t.get('status', '')}" for t in tools)
    
    system = """You are a Solutions Architect writing a Project Design & Requirements (PDR).

Output clean Markdown. Focus on FREE TIER solutions.

Structure:
# Project Design & Requirements (PDR)

## 1. Executive Summary
Elevator pitch.

## 2. Competitive Landscape
| Solution | Strengths | Weaknesses | Our Advantage |

## 3. Tech Stack
### Frontend / Backend / Database / APIs
- Tool: Reason (FREE/PAID)

## 4. Feature Roadmap
### Phase 1: MVP (48hrs)
### Phase 2: Winning Features

## 5. Implementation Steps
Step-by-step guide.

## 6. Risk Mitigation

## 7. Demo Script
3-minute pitch.

---
*Generated by Headstart*"""

    user = f"""Create PDR for: "{user_idea}"

Research:
{research}

Tools:
{tool_list}

Prioritize FREE solutions. Be specific."""

    try:
        response = await call_perplexity(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        )
        await log("✅ **Editor**: PDR complete!")
        return response
    except Exception as e:
        await log(f"❌ **Editor Error**: {e}")
        return f"# Error\n\n{e}"


async def generate_pdr(user_idea):
    logs = []
    
    async def log(msg):
        logs.append(msg)
    
    def log_sync(msg):
        logs.append(msg)
    
    if not PERPLEXITY_API_KEY or PERPLEXITY_API_KEY == "your_api_key_here":
        yield ("❌ Set PERPLEXITY_API_KEY in .env", "# API Key Required", "{}")
        return
    
    await log("🚀 **Headstart Initiated**")
    await log(f"📋 **Idea**: {user_idea}\n")
    yield ("\n".join(logs), "*Generating...*", "{}")
    
    await log("─" * 40)
    angles = await planner(user_idea, log)
    yield ("\n".join(logs), "*Running reporters...*", "{}")
    
    await log("\n" + "─" * 40)
    reports = await run_reporters(angles, log)
    yield ("\n".join(logs), "*Verifying...*", "{}")
    
    await log("\n" + "─" * 40)
    verified, all_tools = facts_checker(reports, log_sync)
    
    tools_json = json.dumps({
        "tools": [{"name": t["name"], "tier": t["tier"], "status": t.get("status", "")} for t in all_tools],
        "summary": {
            "total": len(all_tools),
            "free": sum(1 for t in all_tools if t["tier"] in ["FREE", "FREE TIER", "OPEN SOURCE"]),
            "verified": sum(1 for t in all_tools if t.get("verified"))
        }
    }, indent=2)
    
    yield ("\n".join(logs), "*Writing PDR...*", tools_json)
    
    await log("\n" + "─" * 40)
    pdr = await editor(user_idea, verified, all_tools, log)
    
    await log("\n" + "─" * 40)
    await log("🎉 **Done!**")
    yield ("\n".join(logs), pdr, tools_json)


def create_ui():
    with gr.Blocks(
        title="Headstart",
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
        css=".log-box{font-family:monospace;font-size:0.85em}.pdr-output{min-height:600px}"
    ) as app:
        
        gr.Markdown("""
# 🚀 Headstart

Transform your hackathon idea into a **Project Design & Requirements** document.

🎯 Analyze → 🔍 Research → ✅ Verify → 📝 Synthesize
        """)
        
        with gr.Row():
            idea_input = gr.Textbox(
                label="Your Idea",
                placeholder="e.g., 'AI waste sorting app for campuses'",
                lines=2,
                scale=4
            )
            generate_btn = gr.Button("🚀 Generate", variant="primary", scale=1)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Log")
                log_output = gr.Markdown("*Waiting...*", elem_classes=["log-box"])
            
            with gr.Column(scale=2):
                gr.Markdown("### 📋 PDR")
                pdr_output = gr.Markdown("*Your PDR will appear here...*", elem_classes=["pdr-output"])
                copy_btn = gr.Button("📋 Copy", size="sm")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🧰 Tools")
                tools_output = gr.JSON(value={})
        
        async def run(idea):
            if not idea.strip():
                yield ("❌ Enter an idea", "*No idea*", {})
                return
            async for logs, pdr, tools in generate_pdr(idea):
                try:
                    t = json.loads(tools) if isinstance(tools, str) else tools
                except:
                    t = {}
                yield (logs, pdr, t)
        
        generate_btn.click(fn=run, inputs=[idea_input], outputs=[log_output, pdr_output, tools_output])
        idea_input.submit(fn=run, inputs=[idea_input], outputs=[log_output, pdr_output, tools_output])
        
        copy_btn.click(
            fn=None, inputs=[pdr_output], outputs=[],
            js="(pdr) => { navigator.clipboard.writeText(pdr); alert('Copied!'); }"
        )
        
        gr.Examples(
            examples=[
                ["AI waste sorting app for campuses"],
                ["Decentralized voting for student elections"],
                ["Real-time collaborative code editor"],
                ["Mental health chatbot for students"],
                ["Carbon footprint tracker with gamification"],
            ],
            inputs=[idea_input],
            label="Examples"
        )
        
        gr.Markdown("---\n*Powered by Perplexity AI*")
    
    return app


if __name__ == "__main__":
    app = create_ui()
    app.queue()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
