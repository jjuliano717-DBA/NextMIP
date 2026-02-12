# Next MIP Content Engineering Protocol v1.0

## 1. High-Velocity Content Creation Process
To rapidly generate high-quality, indexed content, follow this "Agentic Content" workflow:

### Step 1: Topic Selection (The "Void" Check)
- **Goal:** Answer questions your competitors aren't answering.
- **Action:** Use tools (or search manually) to find "zero-click" queries where the answer is buried in a PDF or forum.
- **Example:** "How to automate NIST 800-171 self-assessments" (Instead of just "What is NIST 800-171?")

### Step 2: Structure for Machines (Gen AI Optimization)
Gen AI (ChatGPT, Claude, Gemini) prefers structured, dense information.
- **Use the `article.html` template.** It includes pre-configured Schema.org markup.
- **Front-Load the Answer:** The first 100 words should directly answer the user's core question. No fluff.
- **Use Definition Lists:** `<dl>`, `<dt>`, `<dd>` tags help bots understand key terms.
- **Table Data:** Use tables for comparisons (e.g., "MIP vs. MSP Costs").

### Step 3: Drafting & Refining
- **Title:** Must include the primary keyword.
- **Headings:** H2s and H3s should be questions people ask.
- **Internal Linking:** Link back to the `index.html` anchor tags (e.g., `#industries`, `#contact`).

### Step 4: Publication
1. Duplicate `templates/article.html`.
2. Rename to a keyword-rich slug (e.g., `predictive-remediation-manifesto.html`).
3. Fill in the Title, Description, and Schema JSON-LD at the top of the file.
4. Replace the content in `div.prose`.
5. Deploy.

## 2. Technical SEO Checklist (Per Page)
- [ ] **Title Tag:** 50-60 characters, distinct.
- [ ] **Meta Description:** 150-160 characters, active voice (CTR focused).
- [ ] **Canonical Tag:** Ensure it points to the authoritative URL.
- [ ] **Open Graph:** Verify `og:image` and `og:title` for social sharing.
- [ ] **Schema.org:** Update the `datePublished` and `headline` in the JSON-LD script.

## 3. Template Usage Guide

### `templates/landing.html`
- **Use for:** High-conversion sales pages, PPC landing pages.
- **Key Feature:** Removing navigation/footer distraction (optional) to focus on the form.

### `templates/page.html`
- **Use for:** "About Us", "Careers", "Legal/Privacy".
- **Key Feature:** Clean, readable text column with standard navigation.

### `templates/article.html`
- **Use for:** Blog posts, white papers, technical guides.
- **Key Feature:** Includes sidebar TOC, author schema, and typography optimized for long-form reading.
