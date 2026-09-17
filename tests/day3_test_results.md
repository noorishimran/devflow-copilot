# Day 3 — Engineering Artifacts Test Results

## Test 01 — Underspecified Login Requirement

Input:
A simple login page where users can enter email and password and press Login,
without defining what happens after the Login action.

Result:
Pipeline: PASS
Engineering Schema Validation: PASS
Evidence-Fidelity Safety Guard: PASS
Automatic Correction / Safe Fallback: PASS
Unsupported Behavior Prevention: PASS

Observed:
- Acceptance criteria remained limited to confirmed login UI behavior.
- Technology-specific files and frameworks were not invented.
- Unsupported authentication, API, database, redirect, and server behavior
  were not treated as confirmed requirements.
- Unknown Login outcome was moved to open questions / developer unknowns.
- Unsafe generated QA behavior was removed by the safety layer.

Conclusion:
PASS — the Day 3 pipeline safely handled an underspecified requirement.


## Test 02 — Explicit Login Validation Rules

Input:
A login page with email and password fields.

Both fields are required.

If either field is empty when Login is pressed, show:
"Email and password are required."

If both fields contain values, allow the login request to be submitted.

No database, API, authentication provider, redirect, session, or destination
page should be assumed.

Result:
Pipeline: PASS
Engineering Schema Validation: PASS
Evidence-Fidelity Safety Check: PASS
Acceptance Criteria Generation: PASS
Implementation Plan Generation: PASS
QA Test Generation: PASS
Developer Prompt Generation: PASS
Unsupported Technology Invention: PASS
Open Question Quality: PARTIAL PASS

Generated:
- Acceptance Criteria: 1
- Implementation Steps: 1
- QA Test Cases: 3
- Open Questions: 3

QA Coverage:
- Login request submission with both fields populated
- Empty email validation
- Empty password validation
- Exact required-fields error message

Safety:
The output did not invent APIs, databases, sessions, redirects,
authentication providers, or unsupported destination behavior.

Known Minor Issue:
Some generated open questions were unnecessary or overly generic even though
the related validation behavior was already explicitly defined.

Conclusion:
PASS with a minor open-question quality limitation.


## Test 03 — Product Search Page

Input:
A product search page where users can search products by name, display matching
products, receive a defined no-results message, and clear the search field.

Result:
Pipeline: PASS
Engineering Schema Validation: PASS
Evidence-Fidelity Safety Check: PASS
Acceptance Criteria Generation: PASS
Implementation Plan Generation: PASS
QA Test Generation: PASS
Feature Coverage: PASS
Unsupported Technology Invention: PASS
Open Question Quality: PARTIAL PASS

Generated:
- Acceptance Criteria: 4
- Implementation Steps: 4
- QA Test Cases: 3
- Open Questions: 2

QA Coverage:
- Product search using entered text
- Search-field clearing
- No matching products behavior
- Exact no-results message

Safety:
No unsupported database, API, framework, pagination, authentication,
or external integration behavior was introduced.

Known Minor Issue:
The generated open questions repeated behavior already explicitly defined
by the requirement, especially the no-results behavior.

Conclusion:
PASS with minor redundant open-question generation.


## Test 04 — Support Dashboard

Input:
A support dashboard with Open Tickets, In Progress, and Resolved sections.

Each section displays the current ticket count.

Users can press Refresh to update ticket counts.

If refresh fails, display:
"Unable to refresh ticket data."

No database, API, authentication, permissions, notifications, framework,
or external integration should be assumed.

Result:
Pipeline: PASS
Engineering Schema Validation: PASS
Evidence-Fidelity Safety Check: PASS
Unsupported Technology Prevention: PASS
Acceptance Criteria Generation: PARTIAL PASS
Implementation Plan Generation: PARTIAL PASS
QA Test Generation: PARTIAL PASS
Feature Coverage: PARTIAL FAIL
Open Question Quality: PARTIAL FAIL

Generated:
- Acceptance Criteria: 1
- Implementation Steps: 1
- QA Test Cases: 1
- Open Questions: 1

Correctly Covered:
- Dashboard sections
- Ticket count display
- Refresh action
- Updated ticket counts after refresh

Missing Coverage:
- Refresh failure behavior
- Exact error message: "Unable to refresh ticket data."
- QA test for refresh failure

Open Question Issue:
The system asked what should happen after the Refresh button is pressed even
though the requirement already defined both successful refresh behavior and
the refresh-failure message.

Safety:
No unsupported database, API, authentication system, permissions,
notifications, framework, or external integration was introduced.

Conclusion:
PARTIAL PASS — the pipeline remained safe and schema-valid, but the engineering
artifacts did not fully preserve all explicitly supplied behavior.



## Test 05 — Task List

Input:
A simple task list where users can add a task title, receive a validation
message for an empty title, view added tasks, and delete visible tasks.

No database, API, authentication, cloud storage, framework, notifications,
user accounts, or external integrations should be assumed.

Result:
Pipeline: PASS
Engineering Schema Validation: PASS
Evidence-Fidelity Safety Check: PASS
Acceptance Criteria Generation: PASS
QA Test Generation: PASS
Task Addition Coverage: PASS
Empty-Title Validation Coverage: PASS
Task Deletion Coverage: PASS
Unsupported Technology Prevention: PASS
Open Question Quality: PARTIAL PASS

Generated:
- Acceptance Criteria: 3
- Implementation Steps: 1
- QA Test Cases: 3
- Open Questions: 2

QA Coverage:
- Add a task with a valid title
- Empty task-title validation
- Exact "Task title is required." message
- Delete a visible task

Safety:
No unsupported database, API, authentication, cloud storage, framework,
notification system, user-account behavior, or external integration
was introduced.

Known Minor Issue:
The system asked what should happen after Add Task is pressed even though
the requirement already explicitly defined the successful add behavior.

Conclusion:
PASS with a minor redundant open-question limitation.