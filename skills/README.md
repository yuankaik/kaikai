# Hermes Agent 技能库备份

**技能总数：** 344 个  
**备份时间：** 2026-06-14  
**用途：** 系统重装后 clone 此仓库，复制 skills/ 到 ~/.hermes/skills/ 即可恢复全部技能。

## 恢复方法

```bash
git clone https://github.com/yuankaik/kaikai.git
cp -r kaikai/skills/* ~/.hermes/skills/
hermes gateway restart
```

## 技能来源

| 来源 | 数量 | 说明 |
|------|------|------|
| 全盘搜索迁移 | 217 | .local/skills + .agents + superpowers + codex |
| GitHub 热门手动迁移 | 12 | Karpathy、Awesome-Go、prompts.chat、命令行艺术、Anthropic Skills、Firecrawl、Awesome-LLM-Apps、Agency-Agents |
| GStack 自动生成 | 55 | YC CEO Garry Tan 的虚拟工程团队 |
| 微信连接 | 2 | hermes-messaging-setup |

## 技能分类速查

- **apple** (5): apple-notes, apple-reminders, findmy, imessage, macos-computer-use
- **autonomous-ai-agents** (11): agency-agents, awesome-llm-apps, claude-code, codex, gstack + 55 gstack-*, hermes-agent, honcho, kanban-codex-lane, opencode, openhands
- **blockchain** (3): evm, hyperliquid, solana
- **communication** (1): one-three-one-rule
- **creative** (25): architecture-diagram, ascii-art, ascii-video, baoyu-*, blender-mcp, claude-design, comfyui, concept-diagrams, design-md, excalidraw, humanizer, hyperframes, ideation, kanban-video-orchestrator, manim-video, meme-generation, p5js, pixel-art, popular-web-designs, pretext, sketch, songwriting, touchdesigner-mcp
- **data-science** (1): jupyter-live-kernel
- **devops** (9): command-line-art, docker-management, github-workflow-automation, inference-sh-cli, kanban-orchestrator, kanban-worker, pinggy-tunnel, watchers, webhook-subscriptions
- **dogfood** (1): adversarial-ux-test
- **email** (2): agentmail, himalaya
- **finance** (8): 3-statement-model, comps-analysis, dcf-model, excel-author, lbo-model, merger-model, pptx-author, stocks
- **gaming** (2): minecraft-modpack-server, pokemon-player
- **github** (6): codebase-inspection, github-auth, github-code-review, github-issues, github-pr-workflow, github-repo-management
- **health** (2): fitness-nutrition, neuroskill-bci
- **hermes** (1): hermes-messaging-setup
- **mcp** (4): fastmcp, mcp-builder, mcporter, native-mcp
- **media** (5): gif-search, heartmula, songsee, spotify, youtube-content
- **migration** (1): openclaw-migration
- **misc** (47): agent-browser, ai-automation-workflows, anthropics-skills-catalog, brainstorming, content-research-writer, data-analysis, deep-productivity, deploy-to-vercel, dispatching-parallel-agents, dogfood, executing-plans, exploratory-data-analysis, finishing-a-development-branch, imagegen, ml-paper-writing, n8n, nutrient-document-processing, office-productivity, openai-docs, pdf, personal-productivity, plugin-creator, postgresql-code-review, receiving-code-review, requesting-code-review, skill-creator, skill-installer, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, vercel-*, verification-before-completion, web-design-guidelines, writing-guidelines, writing-plans, writing-skills, xlsx, yuanbao
- **mlops** (37): audiocraft, axolotl, chroma, clip, dspy, faiss, flash-attention, guidance, huggingface-*, instructor, lambda-labs, llama-cpp, llava, modal, nemo-curator, obliteratus, outlines, peft, pinecone, pytorch-*, qdrant, segment-anything, simpo, slime, stable-diffusion, tensorrt-llm, torchtitan, trl-fine-tuning, unsloth, vllm, wandb, whisper
- **note-taking** (1): obsidian
- **productivity** (18): airtable, awesome-chatgpt-prompts, canvas, google-workspace, here-now, linear, maps, memento-flashcards, nano-pdf, notion, ocr-and-documents, powerpoint, shop-app, shopify, siyuan, teams-meeting-pipeline, telephony
- **red-teaming** (1): godmode
- **research** (16): arxiv, bioinformatics, blogwatcher, darwinian-evolver, domain-intel, drug-discovery, duckduckgo-search, gitnexus-explorer, llm-wiki, osint-investigation, parallel-cli, polymarket, qmd, research-paper-writing, scrapling, searxng-search
- **security** (4): 1password, oss-forensics, sherlock, web-pentest
- **smart-home** (1): openhue
- **social-media** (1): xurl
- **software-development** (14): awesome-go-reference, code-wiki, debugging-hermes-tui, hermes-agent-skill-authoring, hermes-s6-container-supervision, karpathy-coding-guidelines, node-inspect-debugger, plan, python-debugpy, rest-graphql-debug, spike
- **web-development** (2): firecrawl-web-scraping, page-agent

## GitHub 仓库信息

- 仓库地址：https://github.com/yuankaik/kaikai
- 本地路径：~/kaikai
- 技能路径：~/kaikai/skills/
