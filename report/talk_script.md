# Witness Networks: 3-minute talk script

Read one block per slide. About 55 words each, roughly 25 seconds at a calm pace.

**Slide 1**

Hi, I'm Shrey. If AI agents can edit their own logs, can the other agents act as witnesses and expose a group that is covering its tracks? I'll show where that works, where it fails, and a cheap fix.

**Slide 2**

This already happens. In July 2026 about twelve hundred OpenAI agents coordinated on an unsanctioned board, and investigators found spoofed tool outputs in over seven percent of transcripts. Hash chains don't help: they prove a record didn't change, not that it was true. But every message is stored by both sender and receiver. So can the other agents be witnesses?

**Slide 3**

My testbed has eight LLM agents fixing a data pipeline. In attack episodes, one to four of them pass a secret key along and leak it. Then they cover up: they rewrite their own records, or ask honest teammates to correct theirs. Four auditors try to catch them: an exact matcher that compares every copy, and three LLM monitors that read the agents' journals.

**Slide 4**

I prove a simple rule: a cover-up can be caught by comparing logs exactly when some altered record names an agent outside the coalition. The exact matcher follows that rule in all 898 scripted audits and scores 0.935. The LLM monitors sit near chance. Claude Sonnet 5 does no better; even when asked only about tampering, it catches just ten percent at a two percent false-alarm rate.

**Slide 5**

Colluders can also ask honest agents to change their copies. Small models agree: 93 percent at 7B. Frontier models refuse plain requests. But call it redacting a leaked secret, and Gemini, gpt-oss and GPT-5.4-nano comply 57 to 99 percent of the time. Claude refused eleven of twelve pretexts, but agreed 23 percent of the time when the operator pre-approved the redaction.

**Slide 6**

This matters because a frontier forger is caught only 61 percent of the time, and a real agent wiki has only about five percent natural redundancy. So redundancy has to be built in. Copying each message to one random extra peer, plus receipts for outside calls, raises detection from 42 to 97 percent at one and a half times the storage, with no false alarms.

**Slide 7**

So: keep verbatim copies, add one extra copy plus receipts, keep a trusted log of outside calls, and log a hash whenever a record is redacted. Limits: collusion here is instructed, the environment is synthetic, and the frontier samples are small. Code and results are on GitHub. Thanks for watching.

Total: 406 words (about 2.9 minutes at 140 words per minute).