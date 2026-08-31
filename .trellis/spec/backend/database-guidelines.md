# Backend Database & State Management Guidelines

> Storage architecture, state persistence, and data synchronization patterns.

---

## 1. Storage Architecture

The EnergyGraph-AI platform adopts a hybrid storage model:
1. **Moodle Database (MariaDB 10.11)**: System of record for users, course enrollments, chapters, core assignments, and official grades.
2. **In-Memory Thread-Safe State (`CourseStore`)**: High-performance runtime cache for active chat sessions, scenario state machines, transient submissions, and real-time learning metrics.
3. **Static Courseware Metadata (`course-data/normalized`)**: Version-controlled JSON manifests and knowledge graph baselines.
4. **File Persistence Snapshot**: Periodic atomic JSON file write for fast disaster recovery without requiring complex distributed database transactions.

---

## 2. In-Memory Store Conventions (`CourseStore`)

### Thread Safety Pattern
All write and read operations touching shared dictionaries must acquire `self._lock` (`threading.RLock()`):

```python
class CourseStore:
    def __init__(self, storage_path: Path | None = None):
        self._lock = threading.RLock()
        self._assignments = {}
        self._submissions = {}
        self._sessions = {}
        self._learning_profiles = {}
        self._storage_path = storage_path

    def record_submission(self, student_id: str, assignment_id: str, payload: dict) -> dict:
        with self._lock:
            key = f"{student_id}:{assignment_id}"
            record = {
                "id": str(uuid.uuid4()),
                "student_id": student_id,
                "assignment_id": assignment_id,
                "payload": payload,
                "timestamp": time.time(),
                "status": "submitted"
            }
            self._submissions[key] = record
            self._dirty = True
            return record
```

### Snapshot Persistence & Recovery
- The store serializes state to JSON atomically by writing to `.tmp` then renaming (`os.replace`).
- On service bootstrap (`lifespan`), `CourseStore.load_from_disk()` restores state gracefully if a snapshot file exists.

---

## 3. Moodle MariaDB Synchronization

- **Plugin Integration**: The Moodle plugin at `deploy/moodle/local/course_agent` interacts directly with Moodle core database tables (`mdl_user`, `mdl_course`, `mdl_grade_grades`).
- **Grade Sync**: When a teacher approves AI grading or a student finishes an automated exam, the adapter triggers grade sync via internal Moodle endpoint with secret token verification.
- **Backup & Restore**: Daily backups are automated via `scripts/backup.sh`, creating compressed SQL dumps of MariaDB with encrypted sensitive field masking.
