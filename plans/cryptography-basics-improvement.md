# Cryptography Basics — Improvement Plan

**Target:** Bring all four scores (Usefulness, Topic Coverage, Exercises, Graphics) to **9/10**.

---

## Pre-existing Bugs Discovered During Review

| Bug | Location | Fix |
|-----|----------|-----|
| **Section 3 MCQ wrong answer** | `quantum-mcq` (line 463) — question asks about hash collision resistance, `correctIndex: 0` points to lattice-based PQC answer. None of 4 options list collision resistance. | Replace all options with real hash-property distractors, correct answer = "Collision resistance" |
| **Assessment references nonexistent exercise ID** | `assessment.exercises[4].exerciseId = "protocol-error"` (line 525) — actual exercise ID is `protocol-errors` (line 401, missing final `s`). | Fix to `"protocol-errors"` |

---

## 1. Usefulness: 7 → 9

### 1.1 Add Practical "Try It" Sidebars
Insert inline callout boxes in lesson content that direct the learner to try encryption themselves:

- **Lesson 1.1**: *"Try it: Encrypt `ATTACK` with key 17. Check your answer with a friend."*
- **Lesson 1.2**: *"Try it: Given ciphertext `KHOOR`, how many shifts until you get English? That's brute force in action."*
- **Lesson 2.1**: *"Try it: On your computer: `echo 'hello' | openssl enc -aes-256-cbc -pbkdf2 -iter 100000`. See the binary output?"*
- **Lesson 3.1**: *"Try it: `echo -n 'hello' | sha256sum` — compare to the hash in the lesson."*

**Format**: A paragraph starting with **Try it:** in bold, clearly distinct from lesson body. No special JSON schema needed — just markdown.

### 1.2 Add Tools & Commands Appendix
New top-level field (or last lesson in Section 3):
- `openssl enc -aes-256-cbc` (encrypt a file)
- `gpg --gen-key` (generate a key pair)
- `sha256sum` / `shasum -a 256` (hash a file)
- `openssl s_client -connect example.com:443` (inspect a TLS handshake)

Short, practical. Referenced from sidebars in §1.1.

### 1.3 RSA Toy Numbers → Real-World Note
In Lesson 2.1, after the toy RSA example (n=33), add:
> *Real RSA (2048-bit) uses primes ~300 digits each. Generate one with `openssl genrsa -out private.pem 2048` and inspect it with `openssl rsa -text -in private.pem`.*

---

## 2. Topic Coverage: 7 → 9

### 2.1 Add Lesson 3.2: Symmetric Encryption (AES)
**New lesson:** `lesson-3-2`, id: `aes-internals`

Content to cover:
- Block cipher concept (fixed-size blocks, not per-character)
- Key sizes: AES-128, AES-192, AES-256
- Block cipher modes: ECB (leaks patterns — show the famous penguin image), CBC (IV needed), GCM (authenticated encryption)
- IV / nonce: why you must never reuse one
- Padding: PKCS#7, why padding matters
- Authenticated encryption: why encrypt-then-MAC

**Diagram**: ECB vs CBC comparison (process diagram, side-by-side columns showing how identical plaintext blocks produce different ciphertexts in CBC but identical ones in ECB).

**Exercises** (see §3):
- MCQ: ECB weakness
- Drag sequence: AES encryption steps
- Error spotting: "AES is unbreakable because it has 256-bit keys" text

### 2.2 Add Lesson 3.3: TLS Handshake
**New lesson:** `lesson-3-3`, id: `tls-handshake`

Content to cover:
- The problem TLS solves (secure communication on an open network)
- Handshake overview: ClientHello → ServerHello + Certificate → Key Exchange → Finished
- Certificate chain: leaf → intermediate → root CA
- How hybrid encryption works: RSA/DH for key exchange, AES for bulk data
- Certificate pinning vs trust-on-first-use
- Why TLS is not "end-to-end" (terminates at server — explain E2E separately)

**Diagram**: TLS handshake flowchart with 4-5 nodes showing message flow.

**Exercises** (see §3):
- Drag sequence: order TLS handshake steps
- MCQ: Why hybrid encryption? (speed + key distribution)

### 2.3 Expand Lesson 3.1 (Hash Functions)
Add to existing `.content`:
- HMAC: why `SHA-256(password)` is wrong (length extension attacks, no secret key)
- Key derivation: PBKDF2, bcrypt, Argon2 — why password hashing != general-purpose hashing
- Real-world vulnerabilities: MD5 collisions (1996, practical by 2009), SHA-1 (SHAttered, 2017)

**No new lesson needed** — expand existing `lesson-3-1`.

### 2.4 Add `learningObjectives` Field
Schema-supported but unused. Add 8 objectives to module root:

```json
"learningObjectives": [
  "Explain how the Caesar cipher works and why it's trivially breakable",
  "Apply frequency analysis and brute force to break a substitution cipher",
  "Describe the key distribution problem and how asymmetric cryptography solves it",
  "Perform RSA encryption and decryption with small parameters",
  "Explain the three essential properties of cryptographic hash functions",
  "Compare symmetric and asymmetric encryption in terms of speed, key management, and use cases",
  "Describe the TLS handshake and how hybrid encryption secures web traffic",
  "Identify the quantum computing threat to current cryptography and explain post-quantum approaches"
]
```

---

## 3. Exercises: 6 → 9

### 3.1 Fix Section 3 MCQ (`quantum-mcq`)
Replace with hash-property question:

```json
{
  "id": "quantum-mcq",
  "prompt": "Which property of a hash function ensures that two different inputs cannot produce the same output?",
  "order": 2,
  "type": "mcq",
  "options": [
    "Collision resistance — it is computationally infeasible to find two inputs with the same hash",
    "Determinism — the same input always produces the same hash",
    "Preimage resistance — given a hash, you cannot find the original input",
    "Avalanche effect — changing one bit of input changes ~50% of output bits"
  ],
  "correctIndex": 0,
  "explanation": "Collision resistance guarantees that finding two inputs with the same hash is computationally infeasible. Determinism (B) is necessary but doesn't prevent collisions. Preimage resistance (C) deals with reversing a hash, not collisions. The avalanche effect (D) describes how sensitive the output is to input changes, not collision avoidance."
}
```

### 3.2 Add Drag-to-Sequence Exercises
**New: `caesar-flow-drag`** (Section 1, order 5):
> "Arrange the steps of Caesar cipher communication in the correct order."
- Items: "Choose a shift key", "Write plaintext message", "Shift each letter by the key", "Send ciphertext", "Reverse the shift on each letter", "Read original message"
- Expected order matches that sequence.

**New: `tls-handshake-drag`** (Section 3, in new lesson 3.3 or section exercises):
> "Order the TLS handshake steps."
- Items: "ClientHello", "ServerHello + Certificate", "Key Exchange", "Change Cipher Spec", "Finished"
- Straight chronological.

### 3.3 Add Numeric-Input Exercises
**New: `mod-arithmetic`** (Section 1, order 6):
> "Compute 7^3 mod 5." Answer: 3.

**New: `key-space-calc`** (Section 3, order 4):
> "A cipher has a 56-bit key. How many possible keys are there? Express in scientific notation."
- Accepted: "7.2 × 10^16", "7.2*10^16", "72057594037927936"

### 3.4 Add Section 3 Exercises (currently weakest)
**New: `sha-errors`** (Section 3, order 5, error_spotting):
> Text: "SHA-256 is a type of encryption that can be reversed if you have the right key [ERROR:1]. It produces a variable-length output depending on the input size [ERROR:2]. Two different inputs can produce the same output, which is called a collision [CORRECT]."
- Errors: [0, 1] (SHA-256 is hashing, not encryption; output is fixed 256-bits)

**New: `pqc-drag`** (Section 3, order 6, drag_sequence):
> "Order the post-quantum cryptography approaches by NIST standardization timeline."

### 3.5 Diversify Socratic Validation Modes
Currently all 4 Socratic exercises use `validationMode: "embedding"`. Change:
- `caesar-socratic` (simple recall) → `keyword` (faster, no model download)
- `caesar-socratic-ai` (complex comparison) → keep `embedding`
- `protocol-socratic` → `keyword` (straightforward concepts)
- `quantum-socratic` → `embedding` (complex reasoning)

### 3.6 Replace MCQ Nonsense Options
The "PYTHON — depends on programming language" option in `caesar-mcq` is funny but not instructive. Replace with:

```json
"CZGGJ — shift backward by 2 positions in the alphabet"
```

So the 4 options become: correct MJQQT, plausible but wrong (shift 5 applied backwards), wrong shift back, random word. All test actual understanding.

### 3.7 Exercise Count Summary

| Section | Current | After | Change |
|---------|---------|-------|--------|
| S1: Classical Ciphers | 4 | 6 | +2 (drag + numeric) |
| S2: Cryptographic Protocols | 4 | 4 | — |
| S3: Modern Cryptography | 3 | 7 | +4 (fix MCQ, drag, numeric, error-spotting) |
| **Total** | **11** | **17** | **+6** |

---

## 4. Graphics: 5 → 9

### 4.1 Section 3: Add 3 Diagrams

**Diagram 1: Avalanche Effect** (`avalanche-diagram`, type: `flowchart`)
- Node: "Input: 'hello'" → "SHA-256" → "2cf24dba..."
- Node: "Input: 'hello!'" → "SHA-256" → "ce0609a1..."
- Node: "XOR difference: ~50% bits flipped"
- Edge labels: e.g., "1-bit change"

**Diagram 2: Symmetric vs Asymmetric** (`sym-vs-asym`, type: `process`)
Two parallel columns:
- Left: Symmetric — "Same key K", "Encrypt with K", "Decrypt with K", "Fast, bulk data"
- Right: Asymmetric — "Key pair (Pub, Priv)", "Encrypt with Pub", "Decrypt with Priv", "Slow, key exchange"

**Diagram 3: Shor's Algorithm Threat** (`shor-threat`, type: `timeline`)
- "RSA-2048 (secure now)"
- "Shor's Algorithm discovered"
- "Quantum computer with ~4000 qubits"
- "RSA and ECC broken"
- "PQC migration complete"

### 4.2 Add Edge Labels to Existing Diagrams
The `encrypt-decrypt-flow` diagram (S1) has 5 edges but only 2 labels (`+3`, `-3`). Add:
- `plaintext → encrypt`: label: `input`
- `ciphertext → transmit`: label: `via`
- `transmit → decrypt`: label: `receive`

### 4.3 Add Color to Timeline Nodes
The `crypto-timeline` (S2) has 5 nodes but none use the `color` field. Assign:
- symmetric: `#2D5A27` (green)
- key-exchange: `#1A237E` (blue)
- asymmetric: `#4A148C` (purple)
- tls: `#37474F` (grey)
- e2e: `#E65100` (orange)

### 4.4 Verify SVG Asset Tracking
The SVGs in `assets/illustrations/` exist locally. Confirm they're:
- Tracked in git (`git ls-files`)
- Referenced correctly in markdown (`assets/illustrations/caesar-wheel.svg`)
- No `.gitignore` pattern excludes `.svg` or `assets/` directories

### 4.5 Add Frequency Histogram SVG
New SVG: `frequency-histogram.svg` showing English letter frequencies (E~12.7% tallest bar, Z~0.07% shortest). Referenced in Lesson 1.2 where frequency analysis is introduced. Visual reinforcement of the concept.

---

## Effort Summary

| Category | Changes | Est. Time |
|----------|---------|-----------|
| **Usefulness** | 3 sidebars + 1 appendix + 1 note | ~30 min |
| **Topic Coverage** | 2 new lessons + 1 content expansion + objectives | ~2-3 hr |
| **Exercises** | 1 bug fix + 6 new exercises + 4 patches | ~1.5 hr |
| **Graphics** | 3 new diagrams + 4 polish items | ~1.5 hr |
| **Other** | Fix assessment bug (`protocol-error`→`protocol-errors`) | ~2 min |
| **Total** | **~18 changes** | **~5.5 hr** |

---

## Order of Execution

1. **Quick fixes first** (15 min): Fix `quantum-mcq` bug, fix `protocol-error` assessment ref, replace nonsense MCQ option, add edge labels.
2. **Graphics** (1.5 hr): Add 3 Section 3 diagrams + histogram SVG + color timeline nodes.
3. **Exercises** (1.5 hr): Add drag-to-sequence, numeric-input, error-spotting to fill gaps.
4. **Topic Coverage** (2-3 hr): Write symmetric crypto lesson + TLS handshake lesson.
5. **Usefulness polish** (30 min): Add try-it sidebars, tools appendix, RSA real-world note.
6. **Final verification**: Re-read full module JSON, validate coherency, check all exercise IDs referenced in assessment exist.
