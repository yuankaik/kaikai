# GStack 安装实录

## 依赖链

安装 gstack 需要：
1. `git clone` → ✅ 代理可用
2. `./setup --host hermes` → ❌ 需要 bun
3. `curl -fsSL https://bun.sh/install | bash` → ❌ 需要 unzip
4. `apt-get install unzip` → ✅ 成功
5. `curl ... | bash` → ❌ 用户阻止（pipe-to-bash 安全策略）
6. `npm install -g bun --proxy http://127.0.0.1:56666` → ✅ 成功（1分钟）
7. `cd gstack && ./setup --host hermes` → ✅ 生成 55 个技能

## 关键经验

- **bun 通过 npm 装**：当 `curl | bash` 被阻止时，`npm install -g bun` 可用，但需要加 `--proxy` 参数
- **gstack 原生支持 Hermes**：`./setup --host hermes` 或 `bun run gen:skill-docs --host hermes`
- **生成结果**：55 个 `gstack-*/SKILL.md` 文件到 `~/.hermes/skills/`，总计 64K 行 / 838K tokens
