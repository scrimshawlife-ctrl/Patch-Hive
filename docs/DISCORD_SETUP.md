# PatchHive Discord Server Setup Guide

## Overview

Complete setup guide for the official PatchHive Discord community server. This document covers server configuration, roles, channels, bots, moderation, and community guidelines.

---

## **⬡ SERVER CONFIGURATION**

### **Basic Settings**

```
Server Name: PatchHive
Server Description: Deterministic Eurorack Design & Patch Exploration
Vanity URL: discord.gg/patchhive
Region: Auto (optimal for majority)
AFK Channel: #lounge (15 min timeout)
AFK Timeout: 15 minutes
Default Notification: Only @mentions
2FA Requirement: Required for moderators
Verification Level: Medium (must have verified email)
Explicit Content Filter: Scan media from all members
```

### **Server Icon**

Use `docs/assets/discord/server-icon.svg` (512×512px)
- Export as 512×512 PNG
- Background: #020407
- Cyan hex (#7FF7FF) with magenta signals (#FF1EA0)

### **Server Banner** (Boost Level 2+)

Create 960×540px banner with:
- PatchHive header graphic (honeycomb pattern)
- Tagline: "Modular Synthesis • Deterministic Exploration"
- Cyan/Magenta on black aesthetic

### **Welcome Screen** (Community Server)

Enable welcome screen with:
- Welcome message: "Welcome to PatchHive! Read #rules and verify your account."
- Channels to show: #rules, #getting-started, #general
- Required: Agree to rules before accessing server

---

## **⬡ ROLE STRUCTURE**

### **Administrative Roles**

#### **@Admin** (Red #FF1EA0)
- Full server permissions
- Server owner and co-owners
- Permissions: Administrator

#### **@Moderator** (Cyan #7FF7FF)
- Community moderation
- Channel management
- Permissions:
  - Manage Messages
  - Manage Threads
  - Kick Members
  - Timeout Members
  - View Audit Log

#### **@Bot Manager** (Purple #9B59B6)
- Bot configuration
- Permissions:
  - Manage Webhooks
  - Use External Emojis
  - Manage Emojis

### **Community Roles**

#### **@Contributor** (Green #00FF88)
- Active community contributors
- Regular patch creators
- Helpful community members
- Permissions: None special (recognition only)

#### **@Patch Master** (Gold #FFD700)
- 100+ patches created
- Highly voted patches
- Permissions: None special (recognition only)

#### **@Module Designer** (Orange #FF8800)
- Hardware designers
- Module developers
- Industry professionals
- Permissions: None special (recognition only)

#### **@Beta Tester** (Blue #3498DB)
- PatchHive beta testing program
- Early access to features
- Permissions: Access to #beta-testing channel

#### **@Verified** (Light Gray)
- Completed onboarding
- Agreed to rules
- Auto-assigned after verification
- Permissions: Send Messages, Read Message History

### **Activity Roles** (Auto-assigned by bot)

#### **@Level 5** → **@Level 10** → **@Level 25**
- MEE6 or similar level bot
- Based on message activity
- Visual progression colors (darker → brighter cyan)

### **Interest Roles** (Self-assignable)

```
🎛️ @Eurorack
🎹 @West Coast
🎚️ @East Coast
🔊 @Serge
🎼 @Buchla
📐 @DIY Builder
🔧 @Hardware
💻 @Software
🎨 @Design
📚 @Theory
🎵 @Composer
🎥 @Video Producer
```

---

## **⬡ CHANNEL STRUCTURE**

### **📋 INFO & RULES**

#### **#welcome**
- Read-only welcome message
- Server info and quick links
- How to get started

#### **#rules**
- Community guidelines
- Code of conduct
- Enforcement policy

#### **#announcements**
- Official PatchHive updates
- New feature releases
- Platform maintenance
- Admin/Mod only posting

#### **#getting-started**
- New user guide
- How to use PatchHive
- FAQ
- Link to documentation

### **💬 GENERAL**

#### **#general**
- General discussion
- Off-topic allowed
- Casual chat

#### **#introductions**
- New member introductions
- Share your setup
- Tell your modular story

#### **#lounge** (AFK channel)
- Voice chat text channel
- Casual hangout

### **🎛️ PATCHHIVE**

#### **#patches**
- Share your PatchHive patches
- Discuss patch designs
- Voting and feedback

#### **#racks**
- Share your rack designs
- Case recommendations
- Module selection advice

#### **#modules**
- Module discussion
- Catalog additions
- Module requests

#### **#seeds**
- SEED sharing
- Interesting generation results
- Deterministic discussion

#### **#feedback**
- PatchHive platform feedback
- Feature requests
- Bug reports

#### **#support**
- Technical support
- Account issues
- How-to questions

### **🎹 SYNTHESIS**

#### **#techniques**
- Patching techniques
- Signal flow discussion
- Synthesis theory

#### **#west-coast**
- West Coast synthesis
- Buchla discussion
- Complex oscillators

#### **#east-coast**
- East Coast synthesis
- Moog-style subtractive
- Classic techniques

#### **#modulation**
- CV techniques
- LFO tricks
- Envelope shaping

#### **#effects**
- Effects processing
- Reverb/delay patches
- Creative FX

#### **#sequencing**
- Sequencer discussion
- Generative patches
- Rhythm and timing

### **🛠️ HARDWARE**

#### **#gear**
- Hardware discussion
- Gear photos
- Setup showcase

#### **#diy**
- DIY builds
- Circuit design
- Build logs

#### **#manufacturers**
- Manufacturer discussion
- Module recommendations
- Industry news

#### **#buying-selling**
- Buy/sell/trade (with rules)
- Price checks
- Deal alerts

### **🎵 MUSIC & MEDIA**

#### **#your-music**
- Share your tracks
- Music feedback
- Eurorack compositions

#### **#videos**
- Video sharing
- Tutorials
- Live streams

#### **#inspiration**
- Inspiring patches
- Cool techniques
- Artist showcases

### **💻 DEVELOPMENT**

#### **#beta-testing** (Private)
- Beta tester only
- Test new features
- Report bugs

#### **#api-discussion**
- API usage
- Integration projects
- Developer chat

#### **#open-source**
- Contributing to PatchHive
- GitHub discussions
- Code review

### **🔧 MODERATION**

#### **#mod-chat** (Private)
- Moderator discussion
- Moderation actions
- Team coordination

#### **#mod-log** (Private)
- Automated mod actions
- Audit log
- Bot actions

---

## **⬡ VOICE CHANNELS**

### **General Voice**

```
🔊 Voice Lounge
🔊 Patch Session 1
🔊 Patch Session 2
🔊 Music Production
🔊 AFK Lounge
```

### **Community Events**

```
🎤 Community Meetup
🎤 Patch Showcase
🎤 Tutorial / Workshop
🎤 Listening Party
```

### **Private Rooms** (Stage Channels)

```
🎭 Stage: Community Event
   └── Text: #stage-chat
```

---

## **⬡ CUSTOM EMOJIS**

Upload all emojis from `docs/assets/discord/emojis.svg`:

```
:patchhive:      - Mini PatchHive logo
:vco:            - Oscillator module
:vcf:            - Filter module
:vca:            - Amplifier module
:patch:          - Patch cable
:seed:           - SEED identifier
:upvote:         - Upvote indicator
:downvote:       - Downvote indicator
:signal:         - Signal active
:module:         - Generic module
:rack:           - Eurorack case
:hex:            - Hexagon symbol
:cv:             - CV signal
:gate:           - Gate signal
:waveform:       - Waveform
:community:      - Community
:abx:            - ABX-Core compliance
:deterministic:  - Deterministic generation
```

**Category Organization:**
- PatchHive: :patchhive:, :seed:, :hex:, :abx:, :deterministic:
- Modules: :vco:, :vcf:, :vca:, :module:, :rack:
- Signals: :patch:, :cv:, :gate:, :signal:, :waveform:
- Actions: :upvote:, :downvote:, :community:

---

## **⬡ BOT SETUP**

### **Recommended Bots**

#### **1. MEE6** (Leveling & Moderation)
- Setup XP system (10-20 XP per message, 1 min cooldown)
- Level roles: @Level 5, @Level 10, @Level 25
- Auto-moderation:
  - Spam detection (5 messages/5 seconds)
  - Link filtering in select channels
  - Bad word filter (configurable)
- Commands: !rank, !leaderboard

#### **2. Carl-bot** (Reaction Roles & Utilities)
- Reaction role setup in #getting-started for interest roles
- Embeds for rules and welcome
- Auto-posting from Reddit (r/modular)
- Scheduled messages
- Commands: !rr, !embed, !poll

#### **3. Dyno** (Backup Moderation)
- Auto-responder for common questions
- Custom commands (!patch, !docs, !api)
- Purge commands for cleanup
- Auto-role on join: @Verified
- Commands: !ban, !kick, !mute, !warn

#### **4. PatchHive Bot** (Custom)
*To be developed - integrates with PatchHive API*
- Fetch patch by ID: `/patch 12345`
- Share rack: `/rack 67`
- Random patch: `/random [category]`
- SEED lookup: `/seed ABCD1234`
- User stats: `/stats @username`

#### **5. Statbot** (Server Analytics)
- Member growth tracking
- Message activity graphs
- Channel statistics
- Export reports

---

## **⬡ COMMUNITY GUIDELINES**

### **Rules** (Post in #rules)

```markdown
# PatchHive Community Rules

Welcome to the PatchHive Discord! Please read and follow these rules.

## 1. **Be Respectful**
Treat all members with respect. No harassment, hate speech, discrimination, or personal attacks.

## 2. **Stay On Topic**
Keep discussions relevant to the channel. Use #general for off-topic chat.

## 3. **No Spam**
Don't spam messages, emojis, or mentions. No advertising without permission.

## 4. **Share Constructively**
Give constructive feedback. Criticize ideas, not people.

## 5. **Follow Discord ToS**
Follow Discord's Terms of Service and Community Guidelines.

## 6. **Use Appropriate Channels**
Post content in the correct channel. Check descriptions and pinned messages.

## 7. **No NSFW Content**
Keep all content safe for work. This is a professional community.

## 8. **Respect Intellectual Property**
Don't share pirated content or violate copyright. Give credit for others' work.

## 9. **Moderators Have Final Say**
Respect moderator decisions. Discuss issues privately via DM.

## 10. **Have Fun!**
Be curious, share knowledge, and enjoy the community.

**Violations may result in warnings, timeout, kick, or ban.**

Questions? Ask in #support or DM a moderator.
```

### **Code of Conduct**

- **Be kind and welcoming** to newcomers
- **Share knowledge freely** and help others learn
- **Give credit** where credit is due
- **Assume good intentions** in ambiguous situations
- **Focus on what's best for the community**

### **Moderation Policy**

**Three-strike system:**
1. **Warning** - Verbal/written warning from moderator
2. **Timeout** - 1-7 day timeout depending on severity
3. **Ban** - Permanent ban from server

**Immediate ban for:**
- Harassment or threats
- Hate speech
- Spamming/raiding
- Sharing illegal content
- Ban evasion

**Appeals:**
- Contact @Admin via DM
- Provide appeal within 30 days
- Final decision by server owner

---

## **⬡ WELCOME MESSAGE**

Post in #welcome (use embed):

```markdown
# Welcome to PatchHive! 🎛️

**PatchHive** is a deterministic Eurorack system design and patch exploration platform.

## **Quick Start**

1. Read the #rules and agree to continue
2. Introduce yourself in #introductions
3. Grab some roles in #getting-started
4. Check out the #patches channel to see what the community is creating
5. Visit [patchhive.io](https://patchhive.io) to start designing

## **Links**

🌐 Website: [patchhive.io](https://patchhive.io)
📖 Docs: [docs.patchhive.io](https://docs.patchhive.io)
🐙 GitHub: [github.com/yourusername/Patch-Hive](https://github.com/yourusername/Patch-Hive)
🐦 Twitter: [@patchhive](https://twitter.com/patchhive)

## **What is PatchHive?**

PatchHive is a web platform for:
- 🎛️ Designing Eurorack systems
- 🧬 Generating deterministic patches (same seed = same patch)
- 🔍 Exploring community patch designs
- 📊 Visualizing signal flow and waveforms
- 📄 Exporting patch books (PDF)

Built with ABX-Core v1.2 for full determinism and SEED provenance.

**Welcome to the hive! 🐝⬡**
```

---

## **⬡ EVENTS & ACTIVITIES**

### **Weekly Events**

#### **Patch Challenge** (Every Monday)
- Theme announced in #announcements
- Create patch based on theme
- Share in #patches with tag `#patch-challenge`
- Community voting throughout week
- Winner announced following Monday

#### **Office Hours** (Every Wednesday 7pm ET)
- Voice: Community Meetup
- Q&A with PatchHive team
- Feature demos
- Community feedback

#### **Listening Party** (Every Friday 9pm ET)
- Voice: Listening Party
- Members share tracks
- Discuss techniques
- Casual hangout

### **Monthly Events**

#### **Patch Showcase** (First Saturday)
- Stage event
- Selected members present patches
- Live patching demonstrations
- Q&A session

#### **Community Meetup** (Last Sunday)
- Voice: Community Meetup
- Open discussion
- Roadmap updates
- Feature voting

### **Special Events**

- **Launch Party** - Initial server launch
- **Milestone Celebrations** - 1K members, 10K patches, etc.
- **Modular Meetups** - Regional meetup coordination
- **Superbooth Watchparty** - Industry event discussions

---

## **⬡ ONBOARDING FLOW**

### **New Member Journey**

1. **Join Server** → See #welcome only
2. **Read #rules** → Click "✅ I agree" reaction
3. **Auto-assigned @Verified** → All channels unlock
4. **Welcome DM from Bot** → Quick start guide
5. **Post in #introductions** → Get welcomed by community
6. **Select Roles** → React in #getting-started for interests
7. **Explore Channels** → Start participating

### **Verification Gate**

Use Carl-bot reaction roles in #rules:
- Message: "React with ✅ to agree to the rules and access the server"
- Reaction: ✅ → Add role @Verified
- @Verified role has read/send permissions for all channels

---

## **⬡ SERVER BOOST REWARDS**

### **Level 1** (2 Boosts)
- 128 kbps audio quality
- Animated server icon
- Custom server invite background

### **Level 2** (15 Boosts)
- 256 kbps audio quality
- Server banner (1440×576px)
- 50 custom emoji slots
- Screen share in voice channels

### **Level 3** (30 Boosts)
- 384 kbps audio quality
- Vanity URL (discord.gg/patchhive)
- 100 custom emoji slots
- HD video in voice channels

**Booster Perks:**
- @Server Booster role (special color)
- Exclusive #booster-chat channel
- Early access to features
- Highlighted in community

---

## **⬡ ANALYTICS & METRICS**

Track with Statbot:
- Member growth over time
- Active users (daily/weekly/monthly)
- Messages per channel
- Most active times
- Voice channel usage

**KPIs to monitor:**
- New member retention (% still active after 30 days)
- Average messages per user
- Response time in #support
- Event attendance
- Patch shares per week

---

## **⬡ INTEGRATION WITH PATCHHIVE**

### **Discord → PatchHive**
- Link Discord account on patchhive.io
- Show Discord tag on profile
- "Join our Discord" button in app

### **PatchHive → Discord**
- Webhook: New patches posted to #patches
- Webhook: Trending patches to #inspiration
- Bot: Fetch patch data with `/patch` command
- Rich embeds with waveform thumbnails

---

## **⬡ SETUP CHECKLIST**

- [ ] Configure basic server settings
- [ ] Upload server icon and banner
- [ ] Create all roles with colors/permissions
- [ ] Set up channel categories and channels
- [ ] Write and post rules in #rules
- [ ] Create welcome message in #welcome
- [ ] Upload all custom emojis
- [ ] Install and configure bots (MEE6, Carl-bot, Dyno)
- [ ] Set up reaction roles in #getting-started
- [ ] Configure verification gate
- [ ] Test moderation tools
- [ ] Create event schedule
- [ ] Set up webhooks from PatchHive
- [ ] Announce launch on social media
- [ ] Invite initial members (beta testers, contributors)

---

**Built with ⬡ by the PatchHive community**

Version: 1.0 | Last Updated: 2025-11-25
