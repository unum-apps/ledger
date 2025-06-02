
## 📘 Ledger Model Glossary (Unifist Framework)

### **Unum**
- **What it is**: A group or collective of people working together under shared expectations and infrastructure.
- **Key fields**: `who` — External ID for identifying the Unum.
- **Why it matters**: Top-level container for all activity, entities, and operational logic.

---

### **Entity**
- **What it is**: A person participating in a Unum.
- **Key fields**: `unum_id` (group membership), `who` (external identity).
- **Why it matters**: The atomic unit of agency—every action or record ties back to an Entity.

---

### **Scat**
- **What it is**: A dropped or forgotten ball—tracks what “fell through the cracks."
- **Key fields**: `what` (payload), `when` (epoch), `who` (external reference).
- **Why it matters**: Holds accountability for missed, lost, or neglected responsibilities.

---

### **Task**
- **What it is**: A to-do or in-progress piece of work for an Entity.
- **Key fields**: `status` (e.g., `inprogress`, `done`, `blocked`), `what`, `when`.
- **Why it matters**: Core operational unit for work-in-motion or completed efforts.

---

### **Award**
- **What it is**: A record of recognition or achievement.
- **Key fields**: `what` (e.g., payout, badge), `when`, `who`.
- **Why it matters**: Documents contributions worth celebrating or rewarding.

---

### **Act**
- **What it is**: A request or command for future action—typically issued by an App.
- **Key fields**: `app_id`, `what`, `when`.
- **Why it matters**: Captures intent. These are "to be done" or "to be responded to."

---

### **Fact**
- **What it is**: A record of what happened, as seen by an Origin.
- **Key fields**: `origin_id`, `what` (abstract), `meta` (specific), `when`, `who`.
- **Why it matters**: These are source-of-truth logs. **Facts always come from Origins**.

---

### **App**
- **What it is**: A Unifist-native application (e.g., TehFeelz, GSD).
- **Key fields**: `who` (external ID), `status`, `meta`.
- **Why it matters**: Apps read Facts and write Acts—automating or guiding behavior.

---

### **Origin**
- **What it is**: An external system or platform (e.g., Discord, GitHub) where events actually happen.
- **Key fields**: `who`, `status`, `meta`.
- **Why it matters**: Origins generate Facts. They are the input pipes from the outside world.

---

### **Witness**
- **What it is**: Connects an Origin to an Entity. It allows Origins to write Facts and read Acts.
- **Key fields**: `who`, `status`, `what`, `meta`.
- **Why it matters**: Manages data permissions from outside the Unum (input/output boundary).

---

### **Herald**
- **What it is**: Connects an App to an Entity. It allows Apps to read Facts and write Acts.
- **Key fields**: `status`, `what`, `meta`.
- **Why it matters**: Allows internal tools (Apps) to operate on behalf of users inside the Unum.

---

### **Common Fields**

| Field    | Purpose                                                                 |
|----------|-------------------------------------------------------------------------|
| `who`    | External-facing unique identifier (e.g., Discord ID, GitHub handle).   |
| `what`   | Core payload; varies by context.                                        |
| `meta`   | Extra info; unstructured. For debugging, analytics, or future use.     |
| `when`   | Epoch time (seconds since UNIX start). Used for ordering.              |
| `status` | Current state of the model instance (e.g., `active`, `done`, `inactive`). |
