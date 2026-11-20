# NaturalTyper: Future Roadmap & Architectural Evolution

NaturalTyper simulates nuanced human keystroke dynamics with fatigue degradation, variable inter-key latencies, and intentional typographical errors. This document outlines future algorithmic developments.

---

## 1. Biometric Modeling & Empirical Keystroke Datasets

- **Empirical N-Gram Flight Time Models**:
  - Replace randomized Gaussian jitter with empirical digram/trigram latency distributions (e.g. "th", "er", and "ing" typed significantly faster than cross-keyboard combinations like "q-p").
  - Train Markov decision processes directly on personal typing logs to clone a specific human user's exact cadence.
- **Multilingual & International Layout Support**:
  - Extend adjacent-key neighbor mapping beyond US QWERTY to AZERTY, QWERTZ, Dvorak, and Colemak physical keyboard geometries.

---

## 2. Hardware-Level Stealth Integration

- **RP2040 / ESP32 HID Firmware Transpiler**:
  - Export NaturalTyper flight-time sequences into binary micro-scripts flashed directly to USB HID dongles, allowing hardware-injected human typing on locked-down airgapped enterprise terminals.
- **Micro-Sleep & Cognition Hesitation Breaks**:
  - Model contextual cognitive hesitation (e.g., pausing longer at paragraph breaks, quotation marks, complex terminology, or numbers).

---

## 3. Interfaces & Remote Control

- **WebSocket / Headless Daemon API**:
  - Expose a local headless WebSocket / Unix domain socket server to allow external automation pipelines (Playwright, Selenium, Pentaract) to inject natural human typing programmatically.
