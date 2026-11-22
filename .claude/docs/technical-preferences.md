# Technical Preferences

<!-- project.yaml at the repo root is the machine-readable source of truth for
     engine, specialists, naming, performance, platform, and testing.framework.
     This file is the human-readable LEGACY FALLBACK: agents and skills resolve
     each key from project.yaml first and fall back here only when the
     project.yaml key is absent. /setup-engine dual-writes both.
     Forbidden patterns and allowed libraries are NOT migrated — they live only
     in this file. Populated by /setup-engine; updated as decisions are made. -->

## Engine & Language

- **Engine**: Unreal Engine 5.8 (installed 5.8.4)
- **Language**: C++ (primary), Blueprint (tuning and prototyping only — Blueprints are binary assets the agents cannot author reliably)
- **Rendering**: Lumen + Nanite (deferred), Virtual Shadow Maps
- **Physics**: Chaos

## Input & Platform

<!-- Written by /setup-engine. Read by /ux-design, /ux-review, /test-setup, /team-ui, and /dev-story -->
<!-- to scope interaction specs, test helpers, and implementation to the correct input methods. -->

- **Target Platforms**: PC (Windows, Steam / Epic). Development on macOS; Windows + RTX is the only performance/look reference
- **Input Methods**: Keyboard/Mouse, Gamepad
- **Primary Input**: Keyboard/Mouse
- **Gamepad Support**: Partial (recommended)
- **Touch Support**: None
- **Platform Notes**: Enhanced Input for all bindings; walking only (no sprint); notebook and map must be usable with gamepad

## Naming Conventions

- **Classes**: Prefixed PascalCase (`A` Actor, `U` UObject, `F` struct, `E` enum, `I` interface)
- **Variables**: PascalCase (e.g., `MoveSpeed`); booleans with `b` prefix (`bIsOpen`)
- **Signals/Events**: Delegates/handlers PascalCase `On<Event>`
- **Files**: Match class without prefix (e.g., `InteractableDoor.h`). Assets per briefing V2: `SM_`, `M_`/`MI_`, `T_` (`_D`, `_N`, `_ORM`), `BP_`, `DA_`, `PLA_` (buildings by address, e.g. `PLA_Lenina_18`) under `Content/Kadykchan/`
- **Scenes/Prefabs**: Levels/Maps PascalCase under `Content/Kadykchan/Maps/`; one Packed Level Actor per address
- **Constants**: SCREAMING_SNAKE (UNVERIFIED — not sourceable from docs/engine-reference/unreal/)

## Performance Budgets

- **Target Framerate**: 60 fps at 1440p with upscaling (TSR / DLSS) on a mid-range RTX (briefing V11; start assumption, measured in the Vertical Slice)
- **Frame Budget**: 16.6 ms; GPU profile after each zone
- **Draw Calls**: Nanite for near geometry, HLOD for distant blocks; interiors streamed only near the player. Textures 2K standard, 4K hero only
- **Memory Ceiling**: [TO BE CONFIGURED — measure in the Vertical Slice]

## Testing

- **Framework**: Unreal Automation Spec (tests under `Source/<Module>/Private/Tests/`, named `Kadyktschan.[System].[Scenario]`)
- **Minimum Coverage**: [TO BE CONFIGURED]
- **Required Tests**: Balance formulas, gameplay systems, networking (if applicable)

## Forbidden Patterns

<!-- Add patterns that should never appear in this project's codebase -->
- [None configured yet — add as architectural decisions are made]

## Allowed Libraries / Addons

<!-- Add approved third-party dependencies here -->
- [None configured yet — add as dependencies are approved]

## Architecture Decisions Log

<!-- Quick reference linking to full ADRs in docs/architecture/ -->
- [No ADRs yet — use /architecture-decision to create one]

## Engine Specialists

<!-- Written by /setup-engine when engine is configured. -->
<!-- Read by /code-review, /architecture-decision, /architecture-review, and team skills -->
<!-- to know which specialist to spawn for engine-specific validation. -->

- **Primary**: unreal-specialist
- **Language/Code Specialist**: ue-blueprint-specialist (Blueprint graphs) or unreal-specialist (C++)
- **Shader Specialist**: unreal-specialist (no dedicated shader specialist — primary covers materials)
- **UI Specialist**: ue-umg-specialist (UMG widgets, CommonUI, input routing, widget styling)
- **Additional Specialists**: ue-gas-specialist (Gameplay Ability System, attributes, gameplay effects), ue-replication-specialist (property replication, RPCs, client prediction, netcode)
- **Routing Notes**: Invoke primary for C++ architecture and broad engine decisions. Invoke Blueprint specialist for Blueprint graph architecture and BP/C++ boundary design. Invoke GAS specialist for all ability and attribute code. Invoke replication specialist for any multiplayer or networked systems. Invoke UMG specialist for all UI implementation.

### File Extension Routing

<!-- Skills use this table to select the right specialist per file type. -->
<!-- If a row says [TO BE CONFIGURED], fall back to Primary for that file type. -->

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.cpp, .h files) | unreal-specialist |
| Shader / material files (.usf, .ush, Material assets) | unreal-specialist |
| UI / screen files (.umg, UMG Widget Blueprints) | ue-umg-specialist |
| Scene / prefab / level files (.umap, .uasset) | unreal-specialist |
| Native extension / plugin files (Plugin .uplugin, modules) | unreal-specialist |
| Blueprint graphs (.uasset BP classes) | ue-blueprint-specialist |
| General architecture review | Primary |
