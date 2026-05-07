"""
Golden test set for the Critic Agent.

10 hand-labeled scripts where the human (Maryam) has declared the expected
verdict in advance. The Critic's agreement rate against these labels is the
core quality metric for Milestone 5.

Distribution:
  - 4 GOOD (should PASS)               — IDs golden_001 to golden_004
  - 3 BAD non-hallucination (REJECT)   — IDs golden_005 to golden_007
  - 2 HALLUCINATION (REJECT, hard fail)— IDs golden_008 to golden_009
  - 1 BORDERLINE (debatable)           — ID golden_010

Languages: 8 English, 2 Arabic.
Topics: tech, health, business, education, climate, history.

Each entry contains everything needed to construct a CriticInput, plus the
human's expected verdict and reasoning notes. The reasoning notes are NOT
shown to the Critic — they're for human reviewers reading the test set.
"""

GOLDEN_SET = [
    # ====================================================================
    # CASE 1: GOOD — Tech, casual American voice, well-grounded
    # ====================================================================
    {
        "case_id": "golden_001",
        "language": "en",
        "topic": "tech",
        "expected": {
            "verdict": "PASS",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "All claims trace to key_points. Tone is casual and matches the voice. Host reacts naturally; flows well; clear arc.",
        },
        "input": {
            "script": {
                "script_id": "golden_001",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Welcome back, everyone! Today we're talking about the rise of foldable phones. I've got our resident gadget nerd with me. So — Galaxy Z Fold 7. Worth the hype?"},
                    {"speaker": "guest", "text": "Honestly? Yeah. Samsung dropped it in March 2026 and the hinge is way better than last year's."},
                    {"speaker": "host", "text": "Wait, the hinge was the big complaint though, right? Is this real or marketing?"},
                    {"speaker": "guest", "text": "Real. The crease is actually less visible. And get this — the foldable market grew 23% year over year. People are buying these now, not just nerds like me."},
                    {"speaker": "host", "text": "That's a huge jump. Okay, last question — would you recommend it?"},
                    {"speaker": "guest", "text": "For early adopters, absolutely. Mainstream buyers? Maybe wait one more cycle."},
                ],
            },
            "key_points": [
                "Samsung released the Galaxy Z Fold 7 in March 2026",
                "The redesigned hinge addresses prior durability concerns",
                "The crease on the screen is less visible than previous generations",
                "The foldable phone market grew 23% year over year",
            ],
            "source_meta": {
                "source_id": "src_g001",
                "type": "blog",
                "title": "Foldable Phones: 2026 Market Review",
            },
            "voice_metadata": {
                "voice_id": "11labs_tech_bro_001",
                "name": "Jake",
                "accent": "American",
                "tone_label": "casual, energetic",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 2: GOOD — Health, calm British voice, well-grounded
    # ====================================================================
    {
        "case_id": "golden_002",
        "language": "en",
        "topic": "health",
        "expected": {
            "verdict": "PASS",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Calm, measured tone matches the voice. All facts grounded. Good explanatory flow.",
        },
        "input": {
            "script": {
                "script_id": "golden_002",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Hello, and welcome. Today we're discussing sleep — specifically why so many of us struggle with it. I'm joined by a sleep researcher. Thanks for being here."},
                    {"speaker": "guest", "text": "Thank you for having me. It's a topic I think about quite a lot."},
                    {"speaker": "host", "text": "So let's start simple. How much sleep do adults actually need?"},
                    {"speaker": "guest", "text": "The research consistently points to seven to nine hours for most adults. But I should add — quality matters as much as quantity."},
                    {"speaker": "host", "text": "Quality over quantity. That's interesting. What do you mean by quality?"},
                    {"speaker": "guest", "text": "Things like uninterrupted deep sleep cycles. A study from 2024 found that fragmented sleep, even at full duration, doesn't restore cognitive function the same way."},
                    {"speaker": "host", "text": "So a broken eight hours is worse than a solid six?"},
                    {"speaker": "guest", "text": "In many cases, yes. Though I'd be careful about generalizing — individual needs vary."},
                ],
            },
            "key_points": [
                "Most adults need seven to nine hours of sleep per night",
                "Sleep quality matters as much as quantity",
                "A 2024 study found that fragmented sleep does not restore cognitive function the same way as continuous sleep",
                "Individual sleep needs vary",
            ],
            "source_meta": {
                "source_id": "src_g002",
                "type": "article",
                "title": "Why Sleep Quality Trumps Sleep Quantity",
            },
            "voice_metadata": {
                "voice_id": "11labs_calm_brit_002",
                "name": "Eleanor",
                "accent": "British",
                "tone_label": "calm, measured, thoughtful",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 3: GOOD — Business, energetic American
    # ====================================================================
    {
        "case_id": "golden_003",
        "language": "en",
        "topic": "business",
        "expected": {
            "verdict": "PASS",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Strong hook, varied questions, all facts grounded, energetic tone consistent with voice.",
        },
        "input": {
            "script": {
                "script_id": "golden_003",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Okay, picture this — a startup goes from zero to a billion-dollar valuation in eighteen months. Sounds impossible, right? But that's exactly what happened with FlashPay this year. Let's break it down."},
                    {"speaker": "guest", "text": "Yeah, it's wild. They raised their Series A in early 2025 and hit unicorn status by mid-2026."},
                    {"speaker": "host", "text": "Eighteen months. What did they actually do differently?"},
                    {"speaker": "guest", "text": "Two things. First, they launched in markets nobody else was serving — small businesses in Southeast Asia. Second, their fees were transparent, no hidden costs."},
                    {"speaker": "host", "text": "Transparent pricing as a moat. I love that. So what's next for them?"},
                    {"speaker": "guest", "text": "They're moving into Latin America next quarter. Whether that scales or not — we'll see."},
                ],
            },
            "key_points": [
                "FlashPay went from Series A funding to unicorn status in 18 months",
                "FlashPay raised its Series A in early 2025",
                "FlashPay reached unicorn status by mid-2026",
                "FlashPay focused on small businesses in Southeast Asia",
                "FlashPay differentiated through transparent fee structures",
                "FlashPay plans to expand to Latin America next quarter",
            ],
            "source_meta": {
                "source_id": "src_g003",
                "type": "article",
                "title": "How FlashPay Hit Unicorn Status in 18 Months",
            },
            "voice_metadata": {
                "voice_id": "11labs_energetic_us_003",
                "name": "Marcus",
                "accent": "American",
                "tone_label": "energetic, enthusiastic",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 4: GOOD — Arabic, education topic
    # ====================================================================
    {
        "case_id": "golden_004",
        "language": "ar",
        "topic": "education",
        "expected": {
            "verdict": "PASS",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Arabic script with appropriate Egyptian Arabic tone. All facts grounded. Natural conversational flow.",
        },
        "input": {
            "script": {
                "script_id": "golden_004",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "أهلاً بكم في الحلقة الجديدة! النهاردة هنتكلم عن التعليم عن بُعد بعد الجائحة. معايا خبيرة في المجال."},
                    {"speaker": "guest", "text": "أهلاً بيك، شكراً على الاستضافة."},
                    {"speaker": "host", "text": "نبدأ من الأول — التعليم عن بُعد فعلاً نجح ولا لأ؟"},
                    {"speaker": "guest", "text": "النتائج مختلطة. دراسة من جامعة كامبريدج سنة 2024 لقت إن نسبة 60% من الطلاب اتأثروا سلباً، بس في المقابل التعليم وصل لمناطق جديدة ما كانش يوصلها."},
                    {"speaker": "host", "text": "يعني فيه جانب إيجابي. إيه الدرس الأكبر اللي طلع منها؟"},
                    {"speaker": "guest", "text": "إن النموذج المختلط هو الأنسب. لا online بالكامل ولا offline بالكامل."},
                ],
            },
            "key_points": [
                "A 2024 study from Cambridge University found that 60% of students were negatively affected by remote learning",
                "Remote learning extended education to previously unreached areas",
                "The hybrid model is considered most effective",
            ],
            "source_meta": {
                "source_id": "src_g004",
                "type": "article",
                "title": "التعليم عن بُعد: دروس ما بعد الجائحة",
            },
            "voice_metadata": {
                "voice_id": "11labs_egyptian_ar_004",
                "name": "Salma",
                "accent": "Egyptian Arabic",
                "tone_label": "warm, conversational",
                "language": "ar",
            },
        },
    },

    # ====================================================================
    # CASE 5: BAD — Robotic, essay-like (Naturalness fail)
    # ====================================================================
    {
        "case_id": "golden_005",
        "language": "en",
        "topic": "climate",
        "expected": {
            "verdict": "REJECT",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Reads like an article split into two voices. No reactions, no interruptions, formal essay phrases ('Furthermore', 'In conclusion'). Tone clashes with 'casual, energetic' voice.",
        },
        "input": {
            "script": {
                "script_id": "golden_005",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Greetings. In today's episode, we shall examine the phenomenon of urban heat islands and their consequential effects on metropolitan populations."},
                    {"speaker": "guest", "text": "Indeed. Urban heat islands constitute a significant climatological challenge. According to recent research, cities can be up to seven degrees Celsius warmer than surrounding rural areas during summer months."},
                    {"speaker": "host", "text": "Furthermore, what are the primary causal mechanisms underlying this temperature differential?"},
                    {"speaker": "guest", "text": "There are three principal factors. Firstly, the prevalence of dark surfaces such as asphalt absorbs solar radiation. Secondly, the reduction of vegetation diminishes evapotranspiration cooling. Thirdly, anthropogenic heat emissions from vehicles and air conditioning systems contribute substantially."},
                    {"speaker": "host", "text": "In conclusion, what mitigation strategies should municipalities implement to address this issue?"},
                    {"speaker": "guest", "text": "The implementation of green roofs, the expansion of urban tree canopy, and the utilization of high-albedo materials in construction represent the most efficacious approaches as documented in the literature."},
                ],
            },
            "key_points": [
                "Cities can be up to 7 degrees Celsius warmer than surrounding rural areas in summer",
                "Dark surfaces like asphalt absorb solar radiation",
                "Reduced vegetation decreases evapotranspiration cooling",
                "Anthropogenic heat from vehicles and AC contributes to urban heat",
                "Green roofs, urban tree canopy expansion, and high-albedo materials are mitigation strategies",
            ],
            "source_meta": {
                "source_id": "src_g005",
                "type": "article",
                "title": "Urban Heat Islands and Climate Adaptation",
            },
            "voice_metadata": {
                "voice_id": "11labs_casual_us_005",
                "name": "Alex",
                "accent": "American",
                "tone_label": "casual, energetic",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 6: BAD — Tone mismatch (formal voice, slangy script)
    # ====================================================================
    {
        "case_id": "golden_006",
        "language": "en",
        "topic": "history",
        "expected": {
            "verdict": "REJECT",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Script uses heavy slang ('bruh', 'lit', 'no cap') but voice is 'formal, scholarly'. Severe tone mismatch.",
        },
        "input": {
            "script": {
                "script_id": "golden_006",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Yo, what's up everyone! Today we're getting into the Roman Empire's fall — and bruh, it's wild."},
                    {"speaker": "guest", "text": "No cap, the Western Roman Empire collapsed in 476 AD when Odoacer was like 'I'm taking over' and deposed Romulus Augustulus."},
                    {"speaker": "host", "text": "476 — that's so long ago, that's lit. What happened next?"},
                    {"speaker": "guest", "text": "Honestly the empire was kinda dead inside way before that. Inflation, barbarian invasions, plague — it was a whole vibe."},
                    {"speaker": "host", "text": "The Byzantine Empire kept going though, right? That's actually fire."},
                    {"speaker": "guest", "text": "Yeah for real, until 1453 when Constantinople fell. Iconic ending, no cap."},
                ],
            },
            "key_points": [
                "The Western Roman Empire fell in 476 AD",
                "Odoacer deposed Romulus Augustulus",
                "Inflation, barbarian invasions, and plague contributed to the decline",
                "The Byzantine Empire continued until 1453",
                "Constantinople fell in 1453",
            ],
            "source_meta": {
                "source_id": "src_g006",
                "type": "article",
                "title": "The Fall of the Western Roman Empire",
            },
            "voice_metadata": {
                "voice_id": "11labs_scholarly_006",
                "name": "Professor Hartford",
                "accent": "British",
                "tone_label": "formal, scholarly, measured",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 7: BAD — Weak structure, no clear arc
    # ====================================================================
    {
        "case_id": "golden_007",
        "language": "en",
        "topic": "tech",
        "expected": {
            "verdict": "REJECT",
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": "Topics jump around randomly. No intro, no proper closing. Disjointed; reader can't follow what the episode is about.",
        },
        "input": {
            "script": {
                "script_id": "golden_007",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "So Python 3.13 has the no-GIL build."},
                    {"speaker": "guest", "text": "Yeah, also Rust released 1.85 with new async features."},
                    {"speaker": "host", "text": "Did you see that GitHub Copilot can now do full PRs?"},
                    {"speaker": "guest", "text": "AI coding tools are everywhere. Anyway, JavaScript still dominates web."},
                    {"speaker": "host", "text": "Right, and TypeScript usage hit 78% in the Stack Overflow survey."},
                    {"speaker": "guest", "text": "True. So what's for lunch?"},
                ],
            },
            "key_points": [
                "Python 3.13 includes a no-GIL experimental build",
                "Rust 1.85 introduced new async features",
                "GitHub Copilot can now generate full pull requests",
                "TypeScript usage reached 78% in the latest Stack Overflow developer survey",
            ],
            "source_meta": {
                "source_id": "src_g007",
                "type": "blog",
                "title": "2026 Programming Language Trends",
            },
            "voice_metadata": {
                "voice_id": "11labs_casual_us_007",
                "name": "Sam",
                "accent": "American",
                "tone_label": "casual, friendly",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 8: HALLUCINATION — Invented statistics
    # ====================================================================
    {
        "case_id": "golden_008",
        "language": "en",
        "topic": "tech",
        "expected": {
            "verdict": "REJECT",
            "hard_fail": True,
            "min_factual_grounding": 5,  # We expect Critic to score factual_grounding < 5
            "expected_factual_max": 3,
            "reasoning": "Script invents specific statistics ('43% of users') and a quote ('Tim Cook said...') NOT in key_points. Classic hallucination.",
        },
        "input": {
            "script": {
                "script_id": "golden_008",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "So Apple released the Vision Pro 2 this month. What's the take?"},
                    {"speaker": "guest", "text": "Apple released the Vision Pro 2 in October 2026 with a lighter design."},
                    {"speaker": "host", "text": "How light?"},
                    {"speaker": "guest", "text": "It's now 380 grams, which is 30% lighter than the original. And get this — Tim Cook said in the keynote that 43% of users found the original 'too heavy for daily use.'"},
                    {"speaker": "host", "text": "Wow, 43%? That's a lot."},
                    {"speaker": "guest", "text": "Yeah and the new battery lasts 4.5 hours, up from the original's 2 hours."},
                ],
            },
            "key_points": [
                "Apple released the Vision Pro 2 in October 2026",
                "The Vision Pro 2 has a lighter design than the original",
                "Battery life was improved compared to the original",
            ],
            "source_meta": {
                "source_id": "src_g008",
                "type": "blog",
                "title": "Apple Vision Pro 2: First Impressions",
            },
            "voice_metadata": {
                "voice_id": "11labs_casual_us_008",
                "name": "Riley",
                "accent": "American",
                "tone_label": "casual, curious",
                "language": "en",
            },
        },
    },

    # ====================================================================
    # CASE 9: HALLUCINATION — Arabic, fabricated source quote
    # ====================================================================
    {
        "case_id": "golden_009",
        "language": "ar",
        "topic": "health",
        "expected": {
            "verdict": "REJECT",
            "hard_fail": True,
            "min_factual_grounding": 5,
            "expected_factual_max": 3,
            "reasoning": "Script invents a specific WHO statistic ('80% من سكان الشرق الأوسط') and study findings not present in key_points.",
        },
        "input": {
            "script": {
                "script_id": "golden_009",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "أهلاً بكم. النهاردة بنتكلم عن نقص فيتامين د في المنطقة."},
                    {"speaker": "guest", "text": "موضوع مهم جداً. منظمة الصحة العالمية ذكرت إن 80% من سكان الشرق الأوسط عندهم نقص في فيتامين د."},
                    {"speaker": "host", "text": "80%؟ ده رقم كبير جداً."},
                    {"speaker": "guest", "text": "أيوة، ودراسة من جامعة القاهرة سنة 2025 أكدت إن النقص ده بيسبب زيادة 35% في كسور العظام عند كبار السن."},
                    {"speaker": "host", "text": "إيه الحل؟"},
                    {"speaker": "guest", "text": "التعرض للشمس وتناول المكملات. الجرعة المثالية حسب الدراسة 2000 وحدة دولية يومياً."},
                ],
            },
            "key_points": [
                "Vitamin D deficiency is common in the Middle East region",
                "Vitamin D deficiency can affect bone health",
                "Sun exposure and supplements can address the deficiency",
            ],
            "source_meta": {
                "source_id": "src_g009",
                "type": "article",
                "title": "نقص فيتامين د في الشرق الأوسط",
            },
            "voice_metadata": {
                "voice_id": "11labs_egyptian_ar_009",
                "name": "Mona",
                "accent": "Egyptian Arabic",
                "tone_label": "warm, informative",
                "language": "ar",
            },
        },
    },

    # ====================================================================
    # CASE 10: BORDERLINE — debatable; fine engagement, slightly stiff
    # ====================================================================
    {
        "case_id": "golden_010",
        "language": "en",
        "topic": "business",
        "expected": {
            "verdict": "BORDERLINE",  # Could go either way; useful for measuring agreement
            "hard_fail": False,
            "min_factual_grounding": 5,
            "reasoning": (
                "Reasonable people could score this 3 or 4 on naturalness. It's grounded "
                "and structured but has a faintly stiff quality. We accept either PASS or "
                "REJECT here — used to measure how the Critic handles ambiguity."
            ),
        },
        "input": {
            "script": {
                "script_id": "golden_010",
                "version": 1,
                "turns": [
                    {"speaker": "host", "text": "Welcome. Today's topic is remote work productivity. We have a workplace researcher with us."},
                    {"speaker": "guest", "text": "Thank you for having me."},
                    {"speaker": "host", "text": "Recent data suggests remote work productivity is mixed. What does your research show?"},
                    {"speaker": "guest", "text": "A 2025 Stanford study found remote workers were 13% more productive on solo tasks but 8% less productive on collaborative work."},
                    {"speaker": "host", "text": "So it depends on the type of work."},
                    {"speaker": "guest", "text": "Correct. The study also noted that hybrid arrangements showed the best balance."},
                    {"speaker": "host", "text": "Thank you for sharing this insight."},
                ],
            },
            "key_points": [
                "A 2025 Stanford study found remote workers were 13% more productive on solo tasks",
                "Remote workers were 8% less productive on collaborative work",
                "Hybrid arrangements showed the best balance in the study",
            ],
            "source_meta": {
                "source_id": "src_g010",
                "type": "article",
                "title": "Remote Work Productivity: 2025 Findings",
            },
            "voice_metadata": {
                "voice_id": "11labs_neutral_us_010",
                "name": "Jordan",
                "accent": "American",
                "tone_label": "professional, neutral",
                "language": "en",
            },
        },
    },
]


# Quick stats
def summary():
    by_verdict = {}
    for case in GOLDEN_SET:
        v = case["expected"]["verdict"]
        by_verdict[v] = by_verdict.get(v, 0) + 1
    by_lang = {}
    for case in GOLDEN_SET:
        l = case["language"]
        by_lang[l] = by_lang.get(l, 0) + 1
    by_topic = {}
    for case in GOLDEN_SET:
        t = case["topic"]
        by_topic[t] = by_topic.get(t, 0) + 1
    return {
        "total": len(GOLDEN_SET),
        "by_verdict": by_verdict,
        "by_language": by_lang,
        "by_topic": by_topic,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=2))
