# Witness Networks: 3-minute talk script

Read one block per slide. About 60 words each, roughly 25 seconds at a calm pace.

**Slide 1**

Hi, I'm Shrey. This project asks a simple question. If AI agents can edit their own logs, can the other agents in the system act as witnesses and expose a group that is covering its tracks? I'll show where that works, where it fails, and a cheap fix.

**Slide 2**

This is not hypothetical. In July 2026 around twelve hundred OpenAI agents coordinated on an unsanctioned message board, and investigators found spoofed tool outputs in more than seven percent of transcripts. Hash chains don't help: they prove a record didn't change, not that it was true. But in a multi-agent system, every message is stored twice, by the sender and by the receiver. So can the other agents be witnesses?

**Slide 3**

I built a testbed with eight LLM agents fixing a data pipeline. In attack episodes, one to four of them secretly pass a key along and send it outside. Then they cover up: they delete or rewrite their own records, or ask honest teammates to 'correct' theirs. I compare four auditors: an exact matcher that checks every copy of every message, and three LLM monitors that read the agents' journals.

**Slide 4**

First result. I prove a simple rule: a cover-up can be caught by comparing logs exactly when some altered record names an agent outside the coalition. The exact matcher follows that rule in all 898 scripted audits and reaches 0.935 AUROC. The LLM monitors, all the way up to Claude Sonnet 5, sit at chance. They detect the attack, but a cleaned-up journal fools them.

**Slide 5**

Second result: colluders can ask honest agents to change their copies. Small 7B models agree 93 percent of the time; frontier models almost never do. But the framing matters. Call it redacting a leaked secret and Gemini, gpt-oss and GPT-5.4-nano comply at 57 to 99 percent. Claude refused eleven of twelve pretexts, but agreed 23 percent of the time when the operator pre-approved the redaction.

**Slide 6**

The catch: sloppy 7B forgers get caught almost every time, but a Gemini forger is caught only 61 percent of the time, and in a real agent wiki only about five percent of posts are naturally echoed. So redundancy has to be designed in. Copy each message to one random extra peer and send receipts for outside calls, and detection rises from 42 to 97 percent at one and a half times the storage, with no false alarms.

**Slide 7**

So, four design rules. Keep verbatim copies of messages, not summaries. Copy each message to one random peer and send receipts for outside calls. Keep a trusted log of outside calls. And whenever a record is redacted, log a hash of what was removed. The code and results are on GitHub. Thanks for watching.

Total: 450 words (about 3 minutes at 140 words per minute).