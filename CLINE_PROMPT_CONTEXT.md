# Cline Prompt Context Template
**Repository:** research-26-trading-system  
**Purpose:** Consistent context and working principles for all Cline sessions  
**Usage:** User says "review prompt context in github" to trigger context loading

## 🔄 SESSION STARTUP WORKFLOW

### Step 1: Context Loading
When user says "review prompt context in github":
1. Read this file (`CLINE_PROMPT_CONTEXT.md`)
2. Read current status from `R26_MASTER_DEVELOPMENT_LOG.md`
3. Confirm context loaded: "✅ Context loaded from GitHub"

### Step 2: Work Session
- Follow all core working principles below
- Execute requested tasks using cloud-first approach
- Provide information via conversation, not new files

### Step 3: Session Completion
- Update `R26_MASTER_DEVELOPMENT_LOG.md` with session entry
- Use mandatory log entry format (see below)

---

## 🎯 CORE WORKING PRINCIPLES

### 1. **Cloud-First Architecture**
- **ALL work stored in GitHub using MCP** - never create local files
- **Single source of truth:** GitHub repository `research-26-trading-system`
- **No local storage:** Everything lives in the cloud

### 2. **Single Log System**
- **Master Log:** `R26_MASTER_DEVELOPMENT_LOG.md` contains ALL progress
- **All updates go here:** Status, progress, changes, decisions
- **Continuous context:** Maintains history for future sessions

### 3. **Project Cleanliness Obsession**
- **Avoid excess files:** Build within existing systems
- **Reuse existing structure:** Don't create new files unless absolutely necessary
- **Agent-friendly organization:** Any agent should be able to pick up the project

### 4. **Strict Naming Conventions**
- **Model files:** `r26_pillarA_strategy1_strategyname` format
- **Version tracking:** Always include relevant versions in file names
- **Descriptive names:** Clear naming for posterity and handoffs

### 5. **GitHub Organization Standards**
- **Logical folder structure:** Tests, docs, code in appropriate directories
- **Consistent patterns:** Maintain existing directory organization
- **Easy navigation:** Structure supports quick agent onboarding

### 6. **Information Sharing Protocol**
- **Conversational responses:** Explain information in chat, don't create files
- **Status updates:** Provide via conversation, not new documents
- **File creation:** Only when absolutely necessary, and in existing systems

---

## 📝 MANDATORY LOG ENTRY FORMAT

Every session MUST end with updating `R26_MASTER_DEVELOPMENT_LOG.md`:

```markdown
### [YYYY-MM-DD HH:MM] - Session Entry
**Requested:** [What user asked for]
**Completed:** [What was accomplished]
**Next Steps:** [Any follow-up items]
```

---

## 🏗️ CURRENT PROJECT CONTEXT

### Repository Information
- **GitHub Repo:** `charlestmn/research-26-trading-system`
- **Master Log:** `R26_MASTER_DEVELOPMENT_LOG.md`
- **Strategy Status:** [Read from master log at session start]
- **Current Phase:** [Read from master log at session start]

### Key Strategy Documents
1. `R26_MASTER_DEVELOPMENT_LOG.md` - Main development tracking
2. `RESEARCH_26_FINAL_STATUS_REPORT.md` - System status and achievements
3. `RESEARCH_26_COMPLETE_STATUS.md` - Detailed completion tracking
4. `MISSION_STATEMENT.md` - Strategic objectives
5. `TECHNICAL_ARCHITECTURE.md` - System design

### AWS Infrastructure
- **Instance:** t3.medium (2 vCPU, 4GB RAM)
- **IP:** 54.198.134.93
- **Environment:** Python 3.7 with full dependencies
- **Status:** [Read from master log at session start]

---

## 🚨 CRITICAL REMINDERS

### Before Every Action:
- ✅ Is this following cloud-first principles?
- ✅ Am I building within existing systems?
- ✅ Is the naming convention correct?
- ✅ Will this maintain project cleanliness?

### After Every Session:
- ✅ Update master log with session entry
- ✅ Confirm all work is stored in GitHub
- ✅ No local files created
- ✅ Context maintained for next session

---

## 🎯 SUCCESS CRITERIA

### Session Success Indicators:
1. **Context Loaded:** Started by reading GitHub context
2. **Cloud-First:** All work done via GitHub MCP
3. **Clean Execution:** No unnecessary files created
4. **Proper Logging:** Master log updated with session details
5. **Continuity:** Next session can pick up seamlessly

### Project Success Indicators:
1. **Single Source of Truth:** All context in GitHub
2. **Agent Handoff Ready:** Any agent can continue work
3. **Clean Repository:** Organized, minimal, purposeful files
4. **Complete Documentation:** Full context and progress tracking

---

*This template ensures consistent, clean, cloud-first development with complete context continuity across all Cline sessions.*

**Last Updated:** 2025-08-10  
**Version:** 1.0  
**Status:** Active Template