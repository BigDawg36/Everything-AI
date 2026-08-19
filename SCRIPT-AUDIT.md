# SCRIPT-AUDIT.md — mechanical inventory of vendored executable scripts

Generated 2026-07-16 by a pattern scan (GAPS.md #9). This is an **enumeration, not a
security judgment**: each script file under `.claude/skills/` is listed with mechanical
flags for the three risk categories. A flag means the pattern appears in the file — it
does not mean the behavior is malicious; an unflagged file can still do something a
regex can't see. Skill scripts run with user permissions when a skill invokes them:
**skim any flagged script before letting a skill run it.**

Flags:
- `network` — makes or can make network calls (curl/wget/urllib/requests/fetch/axios/sockets)
- `home-writes` — touches paths outside the repo (`$HOME`, `~/.…`, expanduser, `/etc`, `/usr/local`)
- `exec` — spawns processes or evaluates code (subprocess/os.system/child_process/eval)
- `curl-pipe-sh` — pipes a download directly into a shell (highest-risk pattern)

**Totals:** 218 scripts | network: 20 | home-writes: 28 | exec: 60 | curl-pipe-sh: 2

Manually reviewed `curl-pipe-sh` hits (both benign as vendored):
- `obsidian-second-brain/install.sh:91` — a *printed hint* suggesting the standard `uv` installer command; not executed by the script.
- `obsidian-second-brain/scripts/quick-install.sh:3` — a usage *comment* showing how upstream users invoke the installer; not executed by the script. The script itself does clone/symlink into `~/.claude/` (hence its flags).

## `arcads-external-api` (1 scripts, 0 flagged)

No flags.

## `brainstorming` (4 scripts, 2 flagged)

| Script | Flags |
|---|---|
| `brainstorming/scripts/helper.js` | network |
| `brainstorming/scripts/server.cjs` | network, exec |

## `burpsuite-project-parser` (1 scripts, 0 flagged)

No flags.

## `caveman-compress` (7 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `caveman-compress/scripts/compress.py` | home-writes, exec |

## `chatgpt-image-ad` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `chatgpt-image-ad/scripts/generate_image.py` | network |

## `crypto-protocol-diagram` (1 scripts, 0 flagged)

No flags.

## `debug-buttercup` (1 scripts, 0 flagged)

No flags.

## `devcontainer-setup` (2 scripts, 2 flagged)

| Script | Flags |
|---|---|
| `devcontainer-setup/resources/install.sh` | home-writes |
| `devcontainer-setup/resources/post_install.py` | home-writes, exec |

## `diagramming-code` (1 scripts, 0 flagged)

No flags.

## `generate-youtube-thumbnail` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `generate-youtube-thumbnail/scripts/generate-batch.sh` | network |

## `graph-evolution` (1 scripts, 0 flagged)

No flags.

## `interpreting-culture-index` (7 scripts, 0 flagged)

No flags.

## `ios-simulator-skill` (43 scripts, 30 flagged)

| Script | Flags |
|---|---|
| `ios-simulator-skill/scripts/app_launcher.py` | exec |
| `ios-simulator-skill/scripts/app_state_capture.py` | exec |
| `ios-simulator-skill/scripts/appearance.py` | exec |
| `ios-simulator-skill/scripts/clipboard.py` | exec |
| `ios-simulator-skill/scripts/container.py` | exec |
| `ios-simulator-skill/scripts/gesture.py` | exec |
| `ios-simulator-skill/scripts/hang_watcher.py` | exec |
| `ios-simulator-skill/scripts/keyboard.py` | exec |
| `ios-simulator-skill/scripts/location.py` | exec |
| `ios-simulator-skill/scripts/log_monitor.py` | exec |
| `ios-simulator-skill/scripts/navigator.py` | exec |
| `ios-simulator-skill/scripts/privacy_manager.py` | exec |
| `ios-simulator-skill/scripts/push_notification.py` | exec |
| `ios-simulator-skill/scripts/sim_list.py` | exec |
| `ios-simulator-skill/scripts/simctl_boot.py` | exec |
| `ios-simulator-skill/scripts/simctl_create.py` | exec |
| `ios-simulator-skill/scripts/simctl_delete.py` | exec |
| `ios-simulator-skill/scripts/simctl_erase.py` | exec |
| `ios-simulator-skill/scripts/simctl_shutdown.py` | exec |
| `ios-simulator-skill/scripts/simulator_selector.py` | exec |
| `ios-simulator-skill/scripts/status_bar.py` | exec |
| `ios-simulator-skill/scripts/test_recorder.py` | exec |
| `ios-simulator-skill/scripts/xcode/builder.py` | exec |
| `ios-simulator-skill/scripts/xcode/cache.py` | home-writes |
| `ios-simulator-skill/scripts/xcode/xcresult.py` | exec |
| `ios-simulator-skill/scripts/common/cache_utils.py` | home-writes |
| `ios-simulator-skill/scripts/common/device_utils.py` | exec |
| `ios-simulator-skill/scripts/common/hang_sessions.py` | home-writes |
| `ios-simulator-skill/scripts/common/idb_utils.py` | exec |
| `ios-simulator-skill/scripts/common/screenshot_utils.py` | exec |

## `let-fate-decide` (2 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `let-fate-decide/scripts/test_draw_cards.py` | exec |

## `nano-banana-image-ad` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `nano-banana-image-ad/scripts/generate_image.py` | network |

## `obsidian-second-brain` (102 scripts, 46 flagged)

| Script | Flags |
|---|---|
| `obsidian-second-brain/install.sh` | network, home-writes, curl-pipe-sh |
| `obsidian-second-brain/update.sh` | home-writes |
| `obsidian-second-brain/hooks/obsidian-bg-agent.sh` | home-writes, exec |
| `obsidian-second-brain/hooks/validate-ai-first.sh` | network |
| `obsidian-second-brain/scripts/architect_scan.py` | exec |
| `obsidian-second-brain/scripts/install-codex-wrappers.sh` | home-writes |
| `obsidian-second-brain/scripts/mine_commit_decisions.py` | exec |
| `obsidian-second-brain/scripts/quick-install.sh` | network, home-writes, curl-pipe-sh |
| `obsidian-second-brain/scripts/run-command.sh` | home-writes |
| `obsidian-second-brain/scripts/setup.sh` | home-writes |
| `obsidian-second-brain/scripts/setup_settings_hook.py` | home-writes |
| `obsidian-second-brain/scripts/sweep_non_ascii.py` | exec |
| `obsidian-second-brain/scripts/triage_links.py` | network |
| `obsidian-second-brain/scripts/research/research.py` | home-writes |
| `obsidian-second-brain/scripts/research/research_deep.py` | home-writes |
| `obsidian-second-brain/scripts/research/lib/cache.py` | home-writes |
| `obsidian-second-brain/scripts/research/lib/config.py` | home-writes |
| `obsidian-second-brain/scripts/research/lib/grok.py` | network |
| `obsidian-second-brain/scripts/research/lib/perplexity.py` | network |
| `obsidian-second-brain/scripts/research/lib/podcast.py` | network |
| `obsidian-second-brain/scripts/research/lib/source_config.py` | home-writes |
| `obsidian-second-brain/scripts/research/lib/vault.py` | exec |
| `obsidian-second-brain/scripts/research/lib/video_frames.py` | exec |
| `obsidian-second-brain/scripts/research/lib/youtube.py` | network |
| `obsidian-second-brain/scripts/eval/retrieval_eval.py` | home-writes, exec |
| `obsidian-second-brain/scripts/eval/semantic_search.py` | network, exec |
| `obsidian-second-brain/integrations/telegram-journal/setup.sh` | home-writes |
| `obsidian-second-brain/integrations/telegram-journal/telegram_journal.py` | network, home-writes, exec |
| `obsidian-second-brain/integrations/obsidian-mcp-server/vault_ops.py` | network, home-writes, exec |
| `obsidian-second-brain/tests/test_bg_agent_hook.py` | exec |
| `obsidian-second-brain/tests/test_bom_frontmatter.py` | exec |
| `obsidian-second-brain/tests/test_eval_ruler.py` | exec |
| `obsidian-second-brain/tests/test_export_okf.py` | exec |
| `obsidian-second-brain/tests/test_front_door.py` | exec |
| `obsidian-second-brain/tests/test_heal_precision.py` | exec |
| `obsidian-second-brain/tests/test_link_graph_mirror.py` | exec |
| `obsidian-second-brain/tests/test_no_banned_chars_in_instructions.py` | network |
| `obsidian-second-brain/tests/test_note_safety.py` | exec |
| `obsidian-second-brain/tests/test_showroom.py` | exec |
| `obsidian-second-brain/tests/test_smoke.py` | home-writes, exec |
| `obsidian-second-brain/tests/test_symlink_resilience.py` | exec |
| `obsidian-second-brain/tests/test_vault_health_precision.py` | exec |
| `obsidian-second-brain/tests/test_vault_stats.py` | exec |
| `obsidian-second-brain/adapters/claude-code/adapter.sh` | home-writes |
| `obsidian-second-brain/adapters/hermes/adapter.sh` | home-writes |
| `obsidian-second-brain/adapters/pi/adapter.sh` | home-writes |

## `playwright-skill` (2 scripts, 2 flagged)

| Script | Flags |
|---|---|
| `playwright-skill/run.js` | exec |
| `playwright-skill/lib/helpers.js` | network |

## `sales` (4 scripts, 2 flagged)

| Script | Flags |
|---|---|
| `sales/scripts/analyze_prospect.py` | network |
| `sales/scripts/contact_finder.py` | network |

## `sarif-parsing` (1 scripts, 0 flagged)

No flags.

## `semgrep` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `semgrep/scripts/merge_sarif.py` | exec |

## `standup` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `standup/standup.mjs` | home-writes, exec |

## `systematic-debugging` (1 scripts, 0 flagged)

No flags.

## `ui-ux-pro-max` (3 scripts, 0 flagged)

No flags.

## `version-bump` (1 scripts, 0 flagged)

No flags.

## `writing-skills` (1 scripts, 1 flagged)

| Script | Flags |
|---|---|
| `writing-skills/render-graphs.js` | exec |

## `yara-rule-authoring` (2 scripts, 0 flagged)

No flags.

## `zeroize-audit` (25 scripts, 2 flagged)

| Script | Flags |
|---|---|
| `zeroize-audit/tools/generate_poc.py` | exec |
| `zeroize-audit/tools/scripts/check_rust_asm.py` | exec |

