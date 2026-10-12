# Building Multiple Resume Variants for One Candidate

When a candidate targets **two different hiring cultures at once** (e.g. foreign-owned
commercial companies AND state-owned/central enterprises), one resume is not enough.
This is the playbook. Derived from the Kai Yuan warehouse-manager search (2026-09).

---

## The core principle: variants are NOT translations

A Chinese/English pair, or a commercial/SOE pair, is **two different evaluation logics**,
not one document restyled. Same facts, different ordering, emphasis, and tone.

Worked example — the same "independently automated KPI reporting" fact:

| Target | How it's presented | Why |
|---|---|---|
| Commercial / foreign-owned | Its own section, "AI-assisted reporting", prominent | Reads as initiative and problem-solving |
| State-owned / central enterprise | Demoted to a bullet, no "AI"/"independently" wording | SOE leaders read "employee wrote their own software" as *if you have time for that, is your real job light?* or *is this an attempt to cut headcount?* Plus IT/data-governance risk |
| English (foreign employer) | Demoted to a plain project bullet | "Employee used external AI tools on company data" can trip **data-governance** questions in Western MNCs |

**Same fact, opposite valence depending on reader.** Never carry a "highlight" across
variants unchanged.

---

## Variant matrix (pick the two that fit the search)

| Element | Commercial version | SOE / central-enterprise version | English version |
|---|---|---|---|
| **Header** | Position only, never industry | Position + **户籍 (local household registration)** | Position only |
| **Political affiliation / 职称** | Omit | Omit unless 党员 (only advantageous items appear) | N/A |
| **Household registration** | Omit | **Include — real plus for SOEs** | Omit |
| **Governing tone** | Capability + transferability + digitisation | **Stability + compliance + zero-incident + institutionalisation** | Capability + retention + safety record |
| **Add this bullet** | Industry-keyword compliance row | **SOP / process documentation** (制度与流程建设) | Same SOP bullet — German-owned firms weight *auditable documented procedures* heavily |
| **AI / self-built tooling** | Own section | Demoted bullet, no tech framing | Project bullet, no "AI" wording |
| **Safety record** | One bullet among many | **Elevate** — SOEs treat safety as 一票否决 (knock-out, not a bonus) | **Elevate to a standalone bolded sentence** — EHS is a veto criterion; "zero lost-time injuries" is the standard term |
| **Spelling** | N/A | N/A | British for European-owned employers; US spelling only if applying to a US-HQ role |

---

## Industry-unlock header rule (both variants)

Do **not** write the target industry into the header. Writing
`Warehouse Manager (medical device · GMP-compliant warehousing)` quietly rejects every
job in the adjacent industries you're also pursuing.

```
✅ 求职方向：仓库经理 / 仓储物流经理          ← position only
❌ 求职方向：仓库经理（医药医疗器械·GMP方向）  ← locks out everything else
```

Industry matching then happens in the body via keyword density (SAP, batch lot traceability,
status segregation, ISO three-system audit, SKU count). **One resume reads as if written
for whichever reader picks it up.** No need to maintain a third platform-specific variant.

---

## Phrases that backfire

| Don't write | Why it backfires |
|---|---|
| "连续N年无主动离职记录" | Reverse-read as *why has nobody hired you away?* or *were you nearly managed out each time?* Tenure already shows in the dates line — annotating it manufactures doubt. Also irrelevant to the role's actual screening axis. |
| "主投：X ｜ 并投：Y" | Resumes don't explain strategy, they demonstrate fit. Any line needing the reader to parse a hierarchy is lost in the 7-second scan. |
| "熟悉GMP规范" (bare claim) | Everyone writes this. Say instead *"my work and GMP's requirements are the same work"* + name the transferred mechanisms. Never "familiar with" the thing you've never done — that's the line that gets exposed in interview. |
| Job title inflated past the internal grade | Resolve it honestly in one self-consistent form: `Warehouse Manager (internal title: Team Leader)`. |

---

## Honest-boundary handling for employment gaps / unverifiable history

Two distinct situations, two distinct fixes:

**Gap with no employer at all** → fill it. A listed non-relevant job beats a blank period.
Prepare a "why I switched" answer that (a) doesn't disparage the earlier industry,
(b) names a genuine capability bridge, (c) lands on years-of-focus. Frame the transition as
**a deliberate choice, not drift**.

**Employer exists but left no verifiable trail** (e.g. no social-insurance record — normal for
2000s-era private/brand-agent employers in China) → keep it on the resume, and **disclose
proactively in interview, never wait for the background check**:

> "Those years the company didn't enrol staff in social insurance — common then — so I have no
> documentation. What that period gave me was …"

Proactive disclosure reads as candid; discovered-by-background-check reads as concealment.
Same fact, opposite impression.

**Never attach a candidate to a famous brand they didn't work for.** If they worked for the
brand's *agent/distributor*, write `Company (brand's China agent for X)` — attaching to the
brand name is a background-check red line.

---

## Platform-registration collateral (the deliverable that actually gets used)

A resume PDF doesn't get a candidate hired on job boards; the **online-resume fields** do,
because recruiters search fields, not attachments. A blank online profile = invisible.

Produce a companion **copy-paste text file** alongside the PDF containing:
long-form work history, self-evaluation, skill tags, and the per-field answer table.
The user pastes instead of typing. This also sidesteps any request to fill the account on
the user's behalf (no login state, and writing to someone's account is out of bounds).

### Field-placement rules that change outcomes

- **First action, always: block the current employer.** Online resumes default to
  recruiter-visible; a still-employed candidate updating their profile can be seen by their
  own HR. Do this *before* enriching anything. Add name variants (local + original +
  abbreviated) since employer accounts register under inconsistent names.
- **Expected salary is culture-dependent, not one number.** Set it from the *industry* the
  candidate is willing to trade salary for, not a flat figure. If the candidate's stated
  priority order is industry > salary > commute, then low-ball only for the industry that
  buys the credential — hold firm elsewhere. Warn against trading the top priority for
  commute time.
- **Non-tech candidates must not tag "AI"/"digital"** in skill fields. It pools them with IT
  roles, so warehouse/operations recruiters stop seeing them while tech recruiters surface
  them for jobs they can't do.
- **Fill synonym job titles** (仓库经理 / 仓储经理 / 物流经理 / 仓储物流经理) — recruiters
  and company types search different words; 4 synonyms ≈ 4× discoverability, all genuine.
- **Never auto-parse-and-accept.** Uploaded-resume parsers merge same-institution education
  entries and drop the 全日制/非全日制 attribute (a background-checked field). Parsing also
  never fills expected-position or skill tags — the two fields that drive discoverability.
  Hybrid use: let the parser fill mechanical fields, then overwrite the
  experience/self-evaluation/education blocks with the prepared text.

---

## Verification: always check the *coverage range*, not just that a rule exists

When generating a workbook/spreadsheet with data validation and conditional formatting,
verify the applied **sqref covers every data row**, including the head of the table:

```
下拉: F6:F75          ← starts at row 6; the first 4 rows have no dropdown
条件格式: A2:H35      ← 199 data rows exist; only 34 are covered
```

Both defects render fine in a viewer and pass a "does the file open" check. Load the saved
file back and assert the ranges explicitly. Derive the range from the last populated row,
not from the sample-row count.
