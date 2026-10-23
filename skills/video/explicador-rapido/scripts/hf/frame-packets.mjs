#!/usr/bin/env node

// Thin wrapper over the shared packet builder in hyperframes — this file only
// pins the paths that are specific to this workflow skill. The logic (frame
// splitting, rule citation, packet bounds, `_role.md` assembly) has one owner:
// ../../hyperframes/scripts/lib/frame-packets-core.mjs

import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import * as core from "./lib/frame-packets-core.mjs";

// Modificado para explicador-rapido: el rol de los subagentes viaja en ./rol/ (antes venía de otras skills de
// HyperFrames ya retiradas). Sin la carpeta de reglas de animación, los paquetes simplemente no las citan.
const SKILL_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CONFIG = {
  animationDir: resolve(SKILL_DIR, "../hyperframes-animation"),
  corePath: resolve(SKILL_DIR, "hf/rol/frame-worker-core.md"),
  deltaPath: resolve(SKILL_DIR, "hf/rol/frame-worker.md"),
};

export function buildRolePayload({ outDir }) {
  return core.buildRolePayload({ ...CONFIG, outDir });
}

export function buildFramePackets(options) {
  return core.buildFramePackets({ ...CONFIG, ...options });
}

if (core.isMainModule(import.meta.url)) core.runCli({ buildFramePackets, buildRolePayload });
