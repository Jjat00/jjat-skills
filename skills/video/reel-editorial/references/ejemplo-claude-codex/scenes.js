      tl.set(["#p2-mascot", "#p7-mascot"], { y: 0, rotation: 0 }, 0);

      /* ---------- pantalla completa ---------- */
      pop("#o1-tag", 0.25, { y: -30 });
      rise("#o2-card", 15.2, -50);
      tl.set("#o2-s2", { display: "block" }, 16.44);
      pop("#o2-s2", 16.44);
      rise("#o3-card", 35.0, -50);
      tl.set("#o3-s2", { display: "block" }, 38.52);
      pop("#o3-s2", 38.52);
      rise("#o4-card", 57.4, -50);
      tl.set("#o4-s2", { display: "block" }, 61.22);
      pop("#o4-s2", 61.22);

      /* ---------- 01 comparación (comparison-split) ---------- */
      rise("#p1-label", 2.98, 12);
      tl.fromTo("#p1-title", { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 3.0);
      tl.fromTo("#p1-left", { opacity: 0, x: -260, rotationY: 28, scale: 0.85 }, { opacity: 1, x: 0, rotationY: 12, scale: 1, duration: 0.7, ease: "power3.out" }, 2.96);
      tl.fromTo("#p1-right", { opacity: 0, x: 260, rotationY: -28, scale: 0.85 }, { opacity: 1, x: 0, rotationY: -12, scale: 1, duration: 0.7, ease: "power3.out" }, 5.04);
      pop("#p1-badge-l", 4.28);
      pop("#p1-badge-r", 5.78);
      tl.fromTo("#p1-cards", { y: 0 }, { y: -8, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: 2 }, 4.0);

      /* ---------- 02 el problema (kinetic-type-beats) ---------- */
      rise("#p2-label", 6.62, 12);
      show("#p2b1", 6.62, 9.34);
      tl.fromTo("#p2b1 .headline", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, 6.62);
      pop("#p2-logo", 7.82);
      pop("#p2-c1", 8.48, { x: -40 });
      pop("#p2-c2", 9.06, { x: -40 });
      show("#p2b2", 9.36, 11.6);
      tl.fromTo("#p2b2 .giant", { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power4.out" }, 9.36);
      rise("#p2b2 .headline", 9.9, 30);
      tl.fromTo("#p2-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "power2.inOut" }, 10.2);
      show("#p2b3", 11.6);
      tl.fromTo("#p2-sesga", { opacity: 0, scale: 1.7, rotation: -4 }, { opacity: 1, scale: 1, rotation: -2, duration: 0.32, ease: "power4.out" }, 11.62);
      rise("#p2b3 .headline", 12.2, 30);
      tl.fromTo("#p2-x", { opacity: 0, scale: 1.8, rotation: 0 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.25, ease: "power4.out" }, 12.76);
      tl.set("#p2-x i:first-child", { rotation: 22 }, 0);
      tl.set("#p2-x i:last-child", { rotation: -22 }, 0);
      tl.fromTo("#p2-mascot", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, 12.0);
      tl.fromTo("#p2-mascot", { rotation: 0 }, { rotation: 8, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: 7, immediateRender: false }, 12.5);

      /* ---------- 03 herdr (device-surface-showcase) ---------- */
      rise("#p3-label", 18.7, 12);
      tl.fromTo("#p3-term", { opacity: 0, y: 120, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }, 19.44);
      tl.fromTo("#p3-word", { opacity: 0, scale: 1.3, x: -40 }, { opacity: 1, scale: 1, x: 0, duration: 0.5, ease: "power3.out" }, 21.46);
      rise("#p3-sub", 21.9, 20);
      tl.fromTo("#p3-sticker", { opacity: 0, scale: 0.4, rotation: 0 }, { opacity: 1, scale: 1, rotation: 6, duration: 0.45, ease: "back.out(2.5)" }, 23.46);

      /* ---------- 04 el flujo (prompt-type-submit-generate) ---------- */
      rise("#p4-label", 24.9, 12);
      rise("#p4-title", 27.02, 40);
      tl.fromTo("#p4-t2", { color: "#1b1714" }, { color: "#E0301E", duration: 0.2 }, 28.28);
      tl.fromTo("#p4-term", { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, 28.5);
      pop("#p4-commit", 30.5, { x: -30 });
      tl.fromTo("#p4-caret", { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "steps(1)", yoyo: true, repeat: 33 }, 24.8);

      /* ---------- 05 la conversación (agent-progress-theater, hilo) ---------- */
      rise("#p5-label", 39.05, 12);
      tl.fromTo("#p5-claude", { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, 39.05);
      tl.fromTo("#p5-codex", { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, 39.2);
      pop("#p5-role", 39.06, { x: 40 });
      pop("#p5-model", 40.12, { x: 40 });
      pop("#p5-b1", 43.0, { y: 40 });
      pop("#p5-b2", 43.9, { y: 40 });
      pop("#p5-b3", 44.8, { y: 40 });

      /* ---------- 06 el resultado (agent-progress-theater, checklist) ---------- */
      rise("#p6-label", 45.7, 12);
      show("#p6a", 45.6, 53.7);
      rise("#p6-review", 45.76, 40);
      tl.fromTo("#p6-spin", { rotation: 0 }, { rotation: 1080, duration: 3.0, ease: "none" }, 45.8);
      tl.to("#p6-spin", { opacity: 0, duration: 0.15 }, 48.7);
      tl.fromTo("#p6-stamp", { opacity: 0, scale: 2.6, rotation: -8 }, { opacity: 1, scale: 1, rotation: -8, duration: 0.28, ease: "power4.in" }, 48.6);
      tl.fromTo("#p6a", { x: 0 }, { x: 10, duration: 0.05, yoyo: true, repeat: 3, ease: "none" }, 48.88);
      pop("#p6-pr", 51.8, { y: 30 });
      pop("#p6-cm", 52.46, { y: 30 });
      show("#p6b", 53.74);
      rise("#p6b .headline", 53.74, 40);
      tl.fromTo("#p6-iter", { scale: 1.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }, 54.6);
      tl.fromTo("#p6-a1", { strokeDasharray: 480, strokeDashoffset: 480 }, { strokeDashoffset: 0, duration: 0.5, ease: "power2.out" }, 54.7);
      tl.fromTo("#p6-a2", { strokeDasharray: 480, strokeDashoffset: 480 }, { strokeDashoffset: 0, duration: 0.5, ease: "power2.out" }, 55.1);
      tl.set(["#p6-r1", "#p6-r2", "#p6-r3"], { display: "none" }, 53.74);
      tl.set("#p6-r1", { display: "inline" }, 54.7);
      tl.set("#p6-r1", { display: "none" }, 55.3);
      tl.set("#p6-r2", { display: "inline" }, 55.3);
      tl.set("#p6-r2", { display: "none" }, 55.9);
      tl.set("#p6-r3", { display: "inline" }, 55.9);
      tl.fromTo("#p6-best", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: "back.out(2.2)" }, 56.64);

      /* ---------- 07 cierre (kinetic-type-beats, CTA) ---------- */
      rise("#p7-label", 62.3, 12);
      tl.fromTo("#p7-mascot", { opacity: 0, y: 90 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, 62.4);
      tl.fromTo("#p7-mascot", { rotation: -8 }, { rotation: 8, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 7, immediateRender: false }, 62.9);
      tl.fromTo("#p7-follow", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power4.out" }, 63.56);
      rise("#p7-sub", 64.0, 30);

