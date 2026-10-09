# Hallucination probe: reference for the two runs

Written on 6 Oct 2026 from `hallucination_probe.py`, `probe-run-1.txt` and `probe-run-2.txt`.
It records what the files show. Anything not visible in them is marked as unknown.

## What the probe tests

Same evidence, same question, two system prompts. The docstring asks: *what does the looser system prompt do?*

- **Evidence:** only `doc-101` (Harding & Voss: Annual Strategy Review) from `corpus.py`, sent as the context. No Voyage, no Chroma, no retrieval or relevance floor is involved.
- **Loose prompt:** "You are a helpful legal analyst. Answer the question fully and helpfully as you can. Cite the document id in square brackets where you use it." It has no instruction to stay inside the context and no refusal wording.
- **Grounded prompt:** `llm.GROUNDED_SYSTEM_PROMPT`. Answer using only the context, cite after each claim, and say `grounding.REFUSAL_SENTENCE` if the context does not contain the answer.
- **Check applied to every answer:** `grounding.check_citations(answer, ["doc-101"])`.
- **The questions are unanswerable from `doc-101` on purpose.** The document never names the managing partner or says how long they have held the role. It also has no comparison with the magic circle firms. Any specific name, tenure or comparison would therefore be invented.
- **Model:** the default in `llm.py` is `claude-haiku-4-5-20251001`. The output files do not record the model, `max_tokens` or `stop_reason`.

## The four runs

| # | File | Prompt | Verdict | What happened |
|---|---|---|---|---|
| 1 | probe-run-1.txt | loose | `refusal: False`, `passed: False` | Said the document does not name the managing partner or give tenure, and has no comparison with the magic circle firms. Quoted the document accurately ("the managing partner told the partnership that the priority for the next two years is margin, not size"). Listed real figures (revenue $1.24 billion, 1,850 lawyers, nine offices, 210 equity partners). Suggested other sources to consult. 9 sentences flagged as uncited. |
| 2 | probe-run-1.txt | grounded | `refusal: True`, `passed: True` | Opened with the refusal sentence, then added one more paragraph saying the document gives no name, no tenure and no comparison, ending with `[doc-101]`. |
| 3 | probe-run-2.txt | loose | `refusal: False`, `passed: False` | Same substance as run 1, different layout. Added a "What the Document Does Reveal" section and mentioned "internal profitability indicators (such as write-off rates by practice)". That matches the Pricing section of `doc-101` (write-offs by practice). 9 sentences flagged as uncited. |
| 4 | probe-run-2.txt | grounded | `refusal: True`, `passed: True` | Same pattern as run 2: refusal sentence, then a short explanation with `[doc-101]`. |

## What did not happen

- **The loose prompt did not hallucinate.** In both runs it declined to name a managing partner, give a tenure or compare with the magic circle firms. The expected failure (made-up facts under a permissive prompt) did not appear, so this probe does not show the loose prompt is dangerous. Two runs is a small sample.
- **No difference in substance between the two prompts.** Both said the document does not contain the answer. The difference was format (long markdown vs a short refusal) and what the check reported.
- **No unsupported figures** appeared in any of the four answers. Every figure matches `doc-101`.
- **No errors, timeouts or provider failures** appear in the output.
- **The output is not deterministic.** The two loose answers (rows 1 and 3) differ in layout and detail, and the two grounded answers (rows 2 and 4) differ slightly in wording. The verdicts were the same each time.

## What the check reported, and why it is misleading

- **The loose answers "failed" for a formatting reason, not for hallucination.** `split_sentences` treats every markdown heading (`# Analysis...`), every bullet and every closing line of 3 or more words as a sentence. None of them carried a `[doc-101]` marker, so they were flagged as uncited. Examples from run 1: `## Managing Partner Identity and Tenure`, `Annual revenue of $1.24 billion`. These are not claims that needed citing. So `passed: False` on the loose answers says "no citation markers on headings and bullets", not "invented facts".
- **The grounded answers "passed" as a refusal, but they were not pure refusals.** `is_refusal` returns True if the refusal sentence appears anywhere. The grounded answers contained the refusal sentence and then extra explanatory sentences, and the check ignored those. That is the known gap noted in the review of `grounding.py` (a refusal plus further text counts as a clean refusal).
- **Net effect:** the check's verdicts here (loose = fail, grounded = pass) match the intuition that the grounded prompt is safer, but the reasons are formatting, not truthfulness. Do not cite these results as evidence that the loose prompt invents facts.

## Defects in the probe itself

1. **Missing comma in `QUESTIONS`.** The two questions are joined into one string, so the output shows a single question ("...held the role?How does harding & Voss's profitability..."). The probe never tested the two questions separately.
2. **The inner loop is outside the question loop.** The `for name, prompt` block is not indented under `for question in QUESTIONS`, so it only runs for the last question. Together with defect 1, each run made **2 model calls (one loose, one grounded), not the 4 the code comment promises.** The "4 runs" in this reference are the 4 answers across the 2 files.
3. **Typos in the loose prompt:** "heplfully", and "as" + "you can" are joined without a space ("asyou can"). This is the text the model actually received.
4. **Printing:** the label prints as `n-- loose prompt` (it should be `\n--`), and the verdict line ends with a stray `)`.
5. **One document as context.** The model was never given the other corpus documents, so "not in the context" and "not in the corpus" are not the same thing here.

## What would make the next run more informative

- Fix the missing comma and the indentation, so each question gets both prompts.
- Add at least one question whose answer *is* in `doc-101` and one where a plausible-sounding specific is tempting (a named person, an exact percentage).
- Judge the loose answers on content (does a name, number or comparison appear that is not in the document), not only on `check_citations`.
- Print `stop_reason` and token counts so truncation can be ruled out.
