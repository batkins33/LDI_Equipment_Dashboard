Tangent Forge Podcast System – Roadmap & Checklist
Seed README/checklist for a tf-podcast-system repo.
Purpose: capture all podcast / podcast-automation thinking in one place and make it shippable.



0. Intent & Scope
What this is
	•	A single source of truth for:
	◦	Tangent Forge podcast concepts
	◦	Topic lanes & show formats
	◦	Automation layers (from recording → assets → distribution)
	◦	Repo structure and next actions
Why it exists
	•	Align podcast ideas with Tangent Forge's core:   Form Follows Clarity → repeatable systems, not one-off episodes.
	•	Aim for fast validation + early revenue: light MVP shows, heavy automation over time.
	•	Keep it implementation-ready for dev agents (GitHub / Workspace / Netlify).



1. Repository Skeleton
Suggested structure for a tf-podcast-system repo:
tf-podcast-system/
├─ README.md                  # This file
├─ /docs
│  ├─ concepts.md             # Long-form description of shows & goals
│  ├─ workflow_end_to_end.md  # Recording → publish pipeline
│  ├─ automation_notes.md     # Technical detail & tools used
│  └─ content_calendar.md     # Planning & topics
├─ /shows
│  ├─ tf_core/                # Main Tangent Forge podcast
│  ├─ profit_pulse/           # QPV & productization series
│  ├─ prompt_lab/             # Prompt-pack & AI-writing series
│  └─ workspace_utilities/    # Micro-apps, Workspace tools
├─ /automation
│  ├─ ingest/                 # Recording import scripts / configs
│  ├─ transcript/             # Transcription + cleanup
│  ├─ summarize/              # Show notes, titles, highlights
│  ├─ repurpose/              # Clips, posts, email, prompt packs
│  └─ publish/                # RSS, YouTube, site hooks
├─ /templates
│  ├─ episode_outline.md
│  ├─ show_notes.md
│  ├─ social_caption.md
│  └─ email_broadcast.md
└─ /ops
   ├─ qpv_matrix.md           # QPV scores per show / experiment
   └─ metrics.md              # Downloads, subscribers, leads, revenue



2. Podcast Concept Inventory
These are structured as concept lanes. If specific names were agreed before, you can drop them into the "Title" fields.
2.1.
Tangent Forge Core Podcast
High-level creative systems, QPV thinking, and productization.
	•	Working Title: Tangent Forge Radio (rename as needed)
	•	Format: 20–35 min episodes, solo + occasional guest
	•	Positioning: "Behind the scenes of turning ideas into micro-products."
	•	Primary audience: Indie builders, solopreneurs, creative technologists
	•	Core themes:
	◦	QPV Matrix stories (Quickness / Profitability / Validation in real projects)
	◦	Post-mortems on shipped or killed ideas
	◦	Prompt Pack → Product journeys
	◦	Brand system thinking (VisionSmith / BrandSmith / ForgeSmith)
	•	Episode types:
	◦	Casefile – break down a specific project
	◦	Workshop – live prompt engineering / idea refinement
	◦	Debrief – what worked / failed this month
	◦	Signals – short takes on market or tech shifts



2.2.
Profit Pulse / QPV Show
Focused lane on monetization experiments and product diagnostics.
	•	Working Title: Profit Pulse Sessions
	•	Format: 15–25 min, shorter tactical sessions
	•	Angle: "Live diagnostic on a product idea or funnel."
	•	Core segments:
	◦	Idea teardown (rate Q, P, V live)
	◦	Listener/product submissions
	◦	"From 0 → $100" micro-experiments
	•	Assets to derive from each episode:
	◦	QPV summary graphic
	◦	1–2 prompt pack ideas born from the session
	◦	Short action checklist PDF



2.3.
Prompt Pack / Alex / Writing Lab
Shows that showcase and extend the writing/prompt ecosystem.
	•	Working Title: Prompt Lab or Alex Studio
	•	Format: 20–30 min, live walkthroughs + before/after breakdowns
	•	Core themes:
	◦	Turning blank-page pain into workflows
	◦	Using the Alex system to evolve drafts
	◦	Real client-type scenarios (freelancer briefs, revisions, etc.)
	•	Recurring segments:
	◦	Prompt Makeover – improve a listener's prompt
	◦	Pack to Product – turning a prompt set into a sellable pack
	◦	Tone Gym – practicing tone/voice adjustments live
	•	Repurposing hooks:
	◦	Each episode → 1 mini prompt pack
	◦	Clips demonstrating a single Alex pattern



2.4.
Workspace Utilities & Micro-Apps
Podcast lane tied to Google Workspace, micro-utilities, and automation.
	•	Working Title: Micro Utility Dispatch
	•	Focus: the small tools (Gmail add-ons, Docs helpers, etc.)
	•	Episode types:
	◦	Idea → Add-On – live spec + QPV for a micro app
	◦	Process Rewire – take a messy workflow and clean it up
	◦	Addon Autopsy – what a specific tool gets right/wrong
	•	Integration with dev side:
	◦	Each episode outputs a lightweight design brief in /docs
	◦	Tag ideas for future implementation and cross-ref with repo issues



2.5.
Narrative / Conceptual Lanes (Optional)
Consider these as optional "seasons" or special runs rather than permanent shows:
	•	Modern Vestige Stories
	◦	Collectible, heritage, or artifact stories → feed ArtifactIQ.
	•	Verdantia / Growth Diaries
	◦	Habit / plant-care / slow growth metaphors mapped to creative work.
	•	Accountability / Blame Game
	◦	Philosophical, reflective episodes linked to journaling tools.
If these existed in earlier notes under specific names, capture them in docs/concepts.md.



3. Automation Surface Map
This section translates "podcast" from "media thing" → pipeline.
Think of each step as a module we can automate or semi-automate.
3.1. End-to-End Flow
	1	Record
	2	Ingest
	3	Transcribe
	4	Clean & Segment
	5	Summarize & Structure
	6	Repurpose into formats
	7	Publish & syndicate
	8	Track metrics & feedback
We'll track automation per step:
	•	Manual only
	•	Semi-automated
	•	Fully automated (MVP target where realistic)



3.2. Recording & Ingest
Goals
	•	Central place where raw audio/video lands.
	•	Consistent metadata for every session.
Checklist
	•	Decide primary recording stack   (e.g., Zoom / Riverside / Loom / local DAW – your choice, documented in /docs/workflow_end_to_end.md)
	•	Standardize file naming:
	◦	[show]-[YYYYMMDD]-[episode-short-title].wav/mp4
	•	Set up ingest folder:
	◦	/automation/ingest/inbox/
	◦	/automation/ingest/archive/
	•	Script/agent concept:
	◦	Watch ingest inbox
	◦	Move to cloud storage + tag with show, date, status
	◦	Create stub episode.yml with metadata:
show: tf_core
date: 2025-12-10
title_working: "Working title here"
length_minutes: 32
status: recorded



3.3. Transcription & Cleanup
Goals
	•	Reliable, searchable transcript; cleaned enough to feed prompt tools.
Checklist
	•	Choose transcription engine (document in /docs/automation_notes.md)
	•	Automate:
	◦	Trigger transcription when new file appears in ingest archive
	◦	Save to /automation/transcript/[show]/[episode-id].md
	•	Cleanup steps (script/LLM pipeline):
	◦	Remove filler words (uh, um, cross-talk)
	◦	Add speaker labels
	◦	Rough paragraphing and timestamps
	•	Mark in episode.yml:
	◦	status: transcribed



3.4. Summaries, Show Notes, & Titles
Goals
	•	One pass of the transcript produces multiple structured artifacts.
Checklist
	•	Define prompt templates (in /templates):
	◦	show_notes.md – episode summary, bullet takeaways, links
	◦	titles.md – 10 title options: SEO-friendly, curiosity, punchy, etc.
	◦	description.md – short + long descriptions
	◦	chapter_markers.md – segments with timestamps & labels
	•	Build an automation script/LLM flow that:
	◦	Takes transcript.md
	◦	Uses standardized prompts
	◦	Writes results into /shows/[show]/episodes/[episode-id]/assets/
	•	Update episode.yml:
	◦	status: drafted_notes
	◦	selected_title: "..."



3.5. Repurposing Engine
Goals
	•	Every episode becomes multi-channel content + internal IP.
Outputs per episode (target)
	•	3–5 short clips (audio or video)
	•	3–7 social posts
	•	1 email broadcast
	•	1 blog/long-form post
	•	1 mini prompt pack or worksheet (where relevant)
Checklist
	•	Define clip-detection logic:
	◦	Use transcript to identify "high energy" or "high insight" segments
	◦	Save them in /automation/repurpose/clips_candidates.md
	•	Prompt templates:
	◦	social_caption.md – short, platform variations
	◦	email_broadcast.md – there/subject/CTA pattern
	◦	blog_post.md – expand one segment into article
	◦	prompt_pack_from_episode.md – instructions to convert insights to prompts
	•	Automate:
	◦	Generate all drafts at once after status: drafted_notes
	◦	Store in:
	▪	/shows/[show]/episodes/[episode-id]/repurposed/
	◦	Mark manual review spots clearly (e.g., TODO: add link)



3.6. Publishing & Syndication
Goals
	•	One source of truth per episode → multiple destinations.
Checklist
	•	Decide hosting (RSS / platform) and document in /docs/workflow_end_to_end.md
	•	Maintain mapping file:
rss_feed_url: ...
youtube_playlist_id: ...
website_collection_slug: ...
	•
	•	Automate:
	◦	RSS show notes and audio upload (if API available)
	◦	YouTube title/description from selected templates
	◦	Site entry (Netlify/other) via markdown or CMS API
	•	Track:
	◦	Published URLs in episode.yml
	◦	status: published



3.7. Metrics & Feedback
Goals
	•	Know which shows/episodes actually move QPV and revenue.
Checklist
	•	Define success metrics:
	◦	Downloads
	◦	Email signups
	◦	Product clicks / sales (prompt packs, Profit Pulse, etc.)
	•	Create /ops/metrics.md with:
	◦	Per-episode table (ID, date, show, topic, downloads, leads, revenue)
	◦	Simple rolling 30/90-day trends
	•	Add retrospectives section:
	◦	What worked (topics, formats)
	◦	What flopped
	◦	Hypotheses for next experiments



4. QPV & Phased Roadmap
Tie everything to Tangent Forge's Quickness / Profitability / Validation approach.
4.1. Phase 0 – Seed & Sanity Check (1–2 episodes, manual-heavy)
	•	Choose one primary show lane to prove first (recommend: Tangent Forge Core or Profit Pulse Sessions).
	•	Record 1–2 pilot episodes.
	•	Run minimal automation:
	◦	Manual transcript via chosen tool
	◦	Manually run LLM prompts to create: titles, show notes, 2–3 social posts.
	•	Publish to a basic RSS + one channel (Apple/Spotify or YouTube).
	•	Collect high-level response:
	◦	Did you enjoy recording this?
	◦	Is there a clear "hook" for listeners?
	◦	Any immediate product/pack tie-ins?



4.2. Phase 1 – Systemize the Workflow
Goal: Go from "handmade" to "repeatable" for one show.
	•	Lock in:
	◦	Show one-liner
	◦	Episode template
	◦	Basic visual identity (cover art in TF brand system)
	•	Implement basic automation:
	◦	Ingest + transcription pipeline
	◦	LLM script to generate notes/titles/description
	•	Produce & publish:
	◦	4–6 episodes (one "season 0")
	•	Evaluate:
	◦	QPV for this lane:
	▪	Q: How fast from recording to publish?
	▪	P: Any product uplift? (prompt pack sales, email list growth)
	▪	V: Feedback from listeners, completion rates, replies.



4.3. Phase 2 – Repurposing & Product Hooks
Goal: Make each episode a product engine, not just content.
	•	For the validated show:
	◦	Add consistent CTA: newsletter, pack, Profit Pulse, etc.
	◦	Define at least one default asset per episode:
	▪	A mini prompt pack
	▪	A worksheet / checklist
	▪	A Notion template
	•	Systemize repurposing:
	◦	Standard social/post/email outputs
	◦	Template library tuned to each show
	•	Start cross-promotion:
	◦	From podcast → Gumroad packs
	◦	From packs → podcast episodes as "companion audio"



4.4. Phase 3 – Multi-Show & Deeper Automation
Goal: Once one lane works, expand carefully.
	•	Clone the working system to:
	◦	Prompt Lab / Alex series
	◦	Workspace Utilities Dispatch
	•	Centralize:
	◦	Shared automation under /automation/
	◦	Shared prompt templates under /templates/
	•	Build higher-end automation:
	◦	Auto-clip proposals from transcripts
	◦	Auto-draft show descriptions based on QPV angle
	◦	Auto-update metrics via API (where possible)



5. Operational Checklists
5.1. Episode Lifecycle Checklist
	•	IDEA
	◦	Add idea to /docs/content_calendar.md
	◦	Tag with show + themes + potential product tie-ins
	•	PREP
	◦	Create episode.yml
	◦	Rough outline in /shows/[show]/episodes/[id]/outline.md
	•	RECORD
	◦	Record session
	◦	Save to ingest with correct filename
	•	PROCESS
	◦	Transcribe
	◦	Clean transcript
	◦	Run notes/titles/description prompts
	•	REVIEW
	◦	Choose final title & description
	◦	Light edit of show notes
	•	PUBLISH
	◦	Upload audio/video
	◦	Add notes & links
	◦	Trigger repurposing prompts
	•	POST-LAUNCH
	◦	Publish social posts & email
	◦	Log metrics after 7/30/90 days
	◦	Add learnings to retrospectives



6. Next Steps
If you drop this into a repo as README.md, I'd recommend:
	1	Create the repo skeleton exactly as outlined.
	2	Add a docs/concepts.md and:
	◦	Fill in any specific podcast names or ideas you remember that aren't listed here.
	3	Choose one show lane (Core TF or Profit Pulse) and:
	◦	Create the /shows/[show]/episodes/0001/ folder
	◦	Record/ingest a single pilot episode.
	4	Spin up a small dev agent task:
	◦	"Implement Phase 1 pipelines from /automation section of README."
