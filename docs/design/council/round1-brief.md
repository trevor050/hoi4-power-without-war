# Council Review, Round 1 Brief

You are one of three independent reviewers (Claude Opus 5.5, GPT-6.2 Sol, Gemini 4 Neon) on the design of a Hearts of Iron IV mod. This is a design review, not a code review. No code exists yet.

## What to read

- The design document: `C:\Users\Trevor\Projects\hoi4-power-without-war\docs\design\2026-11-25-power-without-war-design.md`
- The game is installed at `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV` (v1.20). Its `documentation\` folder holds the official script docs (effects, triggers, modifiers, dynamic variables, scripted GUI concepts), and `common\defines\00_defines.lua` holds the defines. Use these to ground feasibility claims. Workshop mods, including The Road to 56, are under `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360`.

Do not modify the design document or any game or mod file. Only write your own output file.

## The spirit of this review (read carefully)

The goal is to make this mod as **fun and engaging** as possible. The designer explicitly does not want reviewers who are reductive or merely critical. A review that lists ten reasons things might not work and leaves nothing standing is a failed review.

Rules:
- **Every problem you raise must come with a concrete solution that keeps or increases the fun.** "This might not work" is not acceptable on its own; "this might not work, do this instead" is.
- Prefer **reshaping** an idea over cutting it. Cut only when you replace it with something better.
- If something is infeasible in the engine, propose the closest feasible version or a creative workaround. Ground engine claims in the game's documentation files where you can; say when you are guessing.
- Bring **new ideas**: mechanics, historical events, interactions between systems, UI moments, AI behaviors that would make the non-combat game more exciting. Ambition is welcome.
- Keep the pillars intact: no currency, hidden math with fuzzy feedback, decisions not buttons, hard but fair, alive but not noisy, low micro by default.

## What to produce

Write your review to:
`C:\Users\Trevor\Projects\hoi4-power-without-war\docs\design\council\round1-<your-name>.md`
where `<your-name>` is `opus`, `sol`, or `neon`.

Structure:
1. **Problems and fixes.** For each: the problem (which section), why it matters for the player experience, and your fix. Rank by impact on fun.
2. **Things not considered.** Gaps, interactions, edge cases, player exploits, AI behaviors, multiplayer or performance concerns, each with a proposed handling.
3. **New ideas.** Additions or reshapes that would make the mod more enjoyable, with a sentence on how each could be built.
4. **Engine notes.** Anything you verified or found in the game files that changes feasibility (cite the file).
5. **Your top 5.** The five changes you would make first, in order.

Be specific and concrete. Aim for depth over breadth. When finished, reply with a short summary and the path to your file.
