# Approval Workflow - User Preview Before Submission 🎯

## Overview

The system now includes a **mandatory approval step** where users can review and edit AI-generated diary entries before submitting them to the VTU portal.

---

## 🔄 New Workflow

### Old Flow (Direct Submission)
```
Upload File → Generate Entries → Submit to Portal ❌
```

### New Flow (With Approval)
```
Upload File → Generate Preview → Review & Edit → Approve → Submit to Portal ✅
```

---

## 📋 Step-by-Step Process

### Step 1: Upload & Generate Preview
**Page:** `/` (index_bulk.html)

1. User uploads input file (Excel, PDF, audio, etc.)
2. User enters date range
3. Clicks **"🔥 Generate & Preview"**

**What Happens:**
- File uploaded via `POST /api/upload-file` → Returns `upload_id`
- Preview generated via `POST /api/generate-preview` → Returns preview entries
- User redirected to approval page

---

### Step 2: Review & Edit
**Page:** `/approval` (approval.html)

**Features:**
- ✅ **Visual Preview**: See all generated entries in card format
- ✅ **Confidence Indicators**: High/Medium/Low badges
- ✅ **Edit Capabilities**:
  - Modify activities text (with live word count)
  - Adjust hours (1-8 with 0.5 step)
  - Edit learnings and blockers
  - Update links
  - View assigned skills
- ✅ **Stats Dashboard**: Total entries, high confidence count, needs review
- ✅ **Warnings Display**: Show AI warnings if any

**User Actions:**
1. Review each entry
2. Edit any field that needs adjustment
3. Check word counts (120-180 recommended)
4. Optionally enable "Dry Run" checkbox
5. Click **"✅ Approve & Submit"**

---

### Step 3: Confirm & Submit
**API:** `POST /api/approve-and-submit`

**What Happens:**
- User confirms submission (browser confirmation dialog)
- Edited entries sent to API
- Background task starts submission
- User redirected to progress page

---

### Step 4: Track Progress
**Page:** `/progress` (progress.html)

**Features:**
- ✅ Circular progress indicator
- ✅ Real-time status updates
- ✅ Success/Failed counters
- ✅ Current action display
- ✅ Completion notification

**Display:**
- Total entries
- Successfully submitted
- Failed submissions
- Current status message

---

## 🛠️ API Endpoints

### 1. Upload File
```
POST /api/upload-file
```

**Request:**
```
Form Data:
- file: UploadFile
```

**Response:**
```json
{
  "upload_id": "uuid",
  "file_name": "example.xlsx",
  "file_size": 12345,
  "message": "File uploaded successfully"
}
```

---

### 2. Generate Preview
```
POST /api/generate-preview
```

**Request:**
```
Form Data:
- upload_id: string
- date_range: string (e.g., "2025-01-01 to 2025-01-31")
- skip_weekends: boolean (default: true)
- skip_holidays: boolean (default: true)
```

**Response:**
```json
{
  "session_id": "uuid",
  "entries": [
    {
      "id": "entry-uuid",
      "date": "2025-01-15",
      "hours": 7.0,
      "activities": "Detailed 150-word description...",
      "learnings": "Learning summary...",
      "blockers": "None",
      "links": "",
      "skills": ["Python", "Flask", "Git"],
      "confidence": 0.92,
      "editable": true
    }
  ],
  "total_entries": 22,
  "high_confidence_count": 18,
  "needs_review_count": 4,
  "warnings": []
}
```

---

### 3. Approve & Submit
```
POST /api/approve-and-submit
```

**Request:**
```json
{
  "session_id": "uuid",
  "approved_entries": [
    {
      "id": "entry-uuid",
      "date": "2025-01-15",
      "hours": 7.0,
      "activities": "User-edited text...",
      "learnings": "...",
      "blockers": "...",
      "links": "",
      "skills": ["Python", "Flask"]
    }
  ],
  "dry_run": false
}
```

**Response:**
```json
{
  "progress_id": "uuid",
  "total_entries": 22,
  "message": "Submission started",
  "dry_run": false
}
```

---

### 4. Get Progress
```
GET /api/progress/{progress_id}
```

**Response:**
```json
{
  "total": 22,
  "completed": 15,
  "failed": 0,
  "current": "Submitting 2025-01-16...",
  "status": "processing"  // or "completed", "failed"
}
```

---

## 💡 Key Features

### Editable Fields
- **Hours**: Number input (1-8, step 0.5)
- **Activities**: Textarea with live word counter
- **Learnings**: Textarea (flexible)
- **Blockers**: Textarea (defaults to "None")
- **Links**: Text input for URLs
- **Skills**: Read-only display (AI-selected)

### Validation
- **Word Count Warning**: Highlights if activities < 120 or > 180 words
- **Required Fields**: All fields pre-populated by AI
- **Confidence Scoring**: Visual badges (High/Medium/Low)

### User Experience
- **Visual Feedback**:
  - Edited cards get highlighted border
  - Word count changes color (green = good, red = warning)
  - Confidence badges color-coded
- **Bulk Actions**:
  - Approve all at once
  - Dry run option to validate without submitting
- **Progress Tracking**:
  - Circular progress indicator
  - Real-time status updates
  - Success/failure counters

---

## 🎨 UI Components

### Approval Page Layout
```
┌─────────────────────────────────────┐
│  Header: Stats & Summary            │
│  - Total Entries                    │
│  - High Confidence Count            │
│  - Needs Review Count               │
├─────────────────────────────────────┤
│  Warnings (if any)                  │
├─────────────────────────────────────┤
│  Entry Cards (scrollable)           │
│  ┌───────────────────────────────┐  │
│  │  Date | Confidence Badge      │  │
│  │  Hours: [7.0]                 │  │
│  │  Activities: [editable text]  │  │
│  │  Learnings: [editable text]   │  │
│  │  Blockers: [editable text]    │  │
│  │  Links: [editable]            │  │
│  │  Skills: [Python] [Flask]     │  │
│  └───────────────────────────────┘  │
│  ... more cards ...                 │
├─────────────────────────────────────┤
│  Actions Bar (sticky bottom)        │
│  [Dry Run ☐]  [← Back] [✅ Approve] │
└─────────────────────────────────────┘
```

### Progress Page Layout
```
┌─────────────────────────────────────┐
│         🚀 Submitting to Portal     │
├─────────────────────────────────────┤
│       Circular Progress Ring        │
│            [75%]                    │
├─────────────────────────────────────┤
│  Status: Submitting 2025-01-16...  │
├─────────────────────────────────────┤
│  Stats Grid:                        │
│  [Total: 22] [Success: 15] [Fail: 0]│
└─────────────────────────────────────┘
```

---

## 🔐 Data Flow

### Session Storage
```javascript
// Browser sessionStorage
{
  "preview_data": {
    "session_id": "uuid",
    "entries": [...],
    "total_entries": 22,
    "warnings": []
  }
}
```

### Server Storage
```python
# preview_sessions dict
{
  "session-uuid": {
    "entries": [...],  # Generated entries
    "original_upload_id": "upload-uuid",
    "warnings": []
  },
  "upload-uuid": {
    "file_path": "/tmp/vtu_uploads/...",
    "file_name": "example.xlsx",
    "file_size": 12345
  }
}
```

---

## 🚀 Usage Example

### CLI (Bypass Approval for Automation)
```bash
# Direct submission (skips approval for CLI)
python main_cli.py submit input.xlsx --dates "2025-01-01 to 2025-01-31"

# Preview only (equivalent to dry-run)
python main_cli.py submit input.xlsx --dates "..." --dry-run
```

### Web UI (Always Shows Approval)
```
1. Upload file
2. Enter date range
3. Click "Generate & Preview"
4. → Review entries on approval page
5. Edit as needed
6. Click "Approve & Submit"
7. → Watch progress
8. → View results
```

---

## 🎯 Benefits

✅ **User Control**: See exactly what will be submitted
✅ **Error Prevention**: Catch AI mistakes before submission
✅ **Customization**: Edit any field to match your needs
✅ **Confidence**: Visual indicators show entry quality
✅ **Safety**: Dry-run option to validate without submitting
✅ **Transparency**: Full visibility into generated content

---

## 📝 Next Steps

Users can now:
1. **Review** all generated entries
2. **Edit** any field that needs adjustment
3. **Validate** word counts and quality
4. **Approve** when satisfied
5. **Track** submission in real-time

**The approval workflow ensures users maintain full control while leveraging AI automation!** 🎉
