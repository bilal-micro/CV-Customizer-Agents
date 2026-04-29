# 🗺️ Module: Frontend Components

**Description:** Encapsulates reusable UI elements like forms, trackers, and displays.
**Goal:** Creates modular, maintainable user interface elements.
**Directories:** `frontend/src/components`
**Files:** 7 | **Functions:** 28

[⬅️ Back to Index](./index.md)

---

## 📄 File: `frontend/src/components/JobForm.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 226
- **Functions:** 2

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `JobForm` | `export function JobForm() : any` | 6 |  |
| `getCharCounterClass` | `const getCharCounterClass = (current: number, max: number) => any` | 101 |  |

---

## 📄 File: `frontend/src/components/KeywordDetails.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 163
- **Functions:** 6

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `MatchedKeywordCard` | `function MatchedKeywordCard({ keyword }: { keyword: MatchedKeyword }) : any` | 8 |  |
| `MissingKeywordCard` | `function MissingKeywordCard({ keyword }: { keyword: MissingKeyword }) : any` | 80 |  |
| `KeywordDetails` | `export function KeywordDetails({ matchedKeywords, missingKeywords }: KeywordDetailsProps) : any` | 127 |  |
| `getEffectivenessColor` | `const getEffectivenessColor = (score: number) => any` | 11 |  |
| `getEffectivenessLabel` | `const getEffectivenessLabel = (score: number) => any` | 17 |  |
| `getPriorityColor` | `const getPriorityColor = (impact: string) => any` | 89 |  |

---

## 📄 File: `frontend/src/components/KeywordExtractionDisplay.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 137
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `getPriorityIcon` | `function getPriorityIcon(priority: number) : string` | 9 |  |
| `getPriorityLabel` | `function getPriorityLabel(priority: number) : string` | 15 |  |
| `getConfidenceColor` | `function getConfidenceColor(confidence: number) : string` | 21 |  |
| `getCategoryIcon` | `function getCategoryIcon(category: string) : string` | 27 |  |
| `getKeywordText` | `function getKeywordText(item: ExtractedKeyword) : string` | 51 |  |
| `KeywordCard` | `function KeywordCard({ item, category }: { item: ExtractedKeyword; category?: string }) : any` | 55 |  |
| `KeywordExtractionDisplay` | `export function KeywordExtractionDisplay({ items, label, category }: KeywordExtractionDisplayProps) : any` | 119 |  |

---

## 📄 File: `frontend/src/components/LoginForm.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 91
- **Functions:** 1

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `handleSubmit` | `const handleSubmit = async (e: React.FormEvent) => any` | 12 |  |

---

## 📄 File: `frontend/src/components/ProcessList.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 86
- **Functions:** 1

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `ProcessList` | `export function ProcessList() : any` | 7 |  |

---

## 📄 File: `frontend/src/components/ProcessTracker.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 483
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `RatingBar` | `function RatingBar({ value, label }: { value: number \| null; label: string }) : any` | 26 |  |
| `KeywordList` | `function KeywordList({ items, label, category }: { items: KeywordItem[]; label: string; category?: string }) : any` | 50 |  |
| `ProcessTracker` | `export function ProcessTracker({ stages }: { stages: StageResult[] }) : any` | 94 |  |
| `formatKeyword` | `const formatKeyword = (item: KeywordItem) => string` | 53 |  |
| `getProgressPercentage` | `const getProgressPercentage = () => any` | 95 |  |
| `getSectionIcon` | `const getSectionIcon = (name: string) => any` | 167 |  |
| `getRelevanceColor` | `const getRelevanceColor = (relevance: number) => any` | 178 |  |

---

## 📄 File: `frontend/src/components/RegistrationForm.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 264
- **Functions:** 4

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `validateEmail` | `const validateEmail = (email: string) => boolean` | 22 |  |
| `getPasswordStrength` | `const getPasswordStrength = (password: string) => { strength: string; color: string; percentage: number }` | 27 |  |
| `validateForm` | `const validateForm = () => boolean` | 45 |  |
| `handleSubmit` | `const handleSubmit = async (e: React.FormEvent) => any` | 83 |  |

---
