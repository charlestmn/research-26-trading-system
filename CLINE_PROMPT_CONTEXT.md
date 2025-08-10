# Cline Prompt Context Template
**Repository:** research-26-trading-system  
**Purpose:** Consistent context and working principles for all Cline sessions  
**Usage:** User says "review prompt context in github" to trigger context loading

## 🔄 SESSION STARTUP WORKFLOW

### Step 1: Context Loading
When user says "review prompt context in github":
1. Read this file (`CLINE_PROMPT_CONTEXT.md`)
2. Read current status from `R26_MASTER_DEVELOPMENT_LOG.md`
3. Read technical overview and strategy from `RESEARCH_26_FINAL_STATUS_REPORT.md`
4. Confirm context loaded: "✅ Context loaded from GitHub"

### Step 2: Work Session
- Follow all core working principles below
- Execute requested tasks using cloud-first AWS architecture
- Provide information via conversation, not new files

### Step 3: Session Completion
- Update `R26_MASTER_DEVELOPMENT_LOG.md` with session entry
- Use mandatory log entry format (see below)

---

## 🎯 CORE WORKING PRINCIPLES

### 1. **Cloud-First AWS Architecture**
- **ALL systems run on AWS** - data, data pipelines, model training, trading execution
- **NO local development** - everything built and deployed on AWS infrastructure
- **Single source of truth:** GitHub repository `research-26-trading-system`
- **AWS-native services:** EC2, S3, Lambda, RDS, etc. for all components
- **No local storage:** All data, models, and execution on AWS cloud

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
- **Technical Overview:** `RESEARCH_26_FINAL_STATUS_REPORT.md`
- **Strategy Status:** [Read from master log at session start]
- **Current Phase:** [Read from master log at session start]

### Key Strategy Documents
1. `R26_MASTER_DEVELOPMENT_LOG.md` - Main development tracking
2. `RESEARCH_26_FINAL_STATUS_REPORT.md` - Technical overview and strategy
3. `RESEARCH_26_COMPLETE_STATUS.md` - Detailed completion tracking
4. `MISSION_STATEMENT.md` - Strategic objectives
5. `TECHNICAL_ARCHITECTURE.md` - System design

### AWS Infrastructure (Cloud-First)
- **Instance:** t3.medium (2 vCPU, 4GB RAM) - IP: 54.198.134.93
- **Environment:** Python 3.7 with full dependencies
- **Data Storage:** S3 buckets for all data and models
- **Execution:** All processing, training, and trading on AWS
- **Status:** [Read from master log at session start]

---

## 🚨 CRITICAL REMINDERS

### Before Every Action:
- ✅ Is this following AWS cloud-first architecture?
- ✅ Am I building on AWS, not locally?
- ✅ Is this maintaining project cleanliness?
- ✅ Is the naming convention correct?
- ✅ Will this support agent handoffs?

### AWS-First Development:
- ✅ Data pipelines run on AWS (EC2/Lambda)
- ✅ Model training on AWS compute
- ✅ Data storage in S3 buckets
- ✅ Trading execution on AWS infrastructure
- ✅ No local development or storage

### After Every Session:
- ✅ Update master log with session entry
- ✅ Confirm all work is AWS-based
- ✅ No local files created
- ✅ Context maintained for next session

---

## 🎯 SUCCESS CRITERIA

### Session Success Indicators:
1. **Context Loaded:** Started by reading GitHub context files
2. **AWS-First:** All work done on AWS infrastructure
3. **Clean Execution:** No unnecessary files created
4. **Proper Logging:** Master log updated with session details
5. **Continuity:** Next session can pick up seamlessly

### Project Success Indicators:
1. **Single Source of Truth:** All context in GitHub
2. **AWS-Native:** All systems running on AWS cloud
3. **Agent Handoff Ready:** Any agent can continue work
4. **Clean Repository:** Organized, minimal, purposeful files
5. **Complete Documentation:** Full context and progress tracking

---

*This template ensures consistent, clean, AWS cloud-first development with complete context continuity across all Cline sessions.*

**Last Updated:** 2025-08-10  
**Version:** 1.1  
**Status:** Active Template