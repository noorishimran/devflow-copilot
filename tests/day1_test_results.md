# Day 1 GenAI Test Results

Model: Qwen3 1.7B  
Runtime: Ollama  
Prompt Version: requirement_prompt_v2  
Execution: Local-only  

## Test 01 — Appointment Booking
Input:
Build an appointment booking system where patients can register, login, search doctors and book appointments.

Functional Result: PASS  
Schema Validation: PASS  
Evidence Fidelity: PARTIAL FAIL  

Notes:
The model generated valid structured JSON, but introduced unsupported details such as personal information and doctor search criteria.

---

## Test 02 — Todo Application
Input:
Build a todo application where users can register, login, create tasks, mark tasks completed and delete tasks.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PASS
Coverage: PARTIAL

Notes:
All requested features were correctly extracted without obvious unsupported functionality.
However, only 3 user stories were generated for 5 features.

---

## Test 03 — E-commerce Store
Input:
Build an online store where customers can browse products, add products to a cart and place orders.

Initial Result: FAIL

Reason:
The model omitted the required priority field for all generated features.

Fix:
Updated the Feature schema so missing priority defaults to "medium".

Retest Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PASS

---

## Test 04 — Employee Leave System
Input:
Build an employee leave management system where employees can submit leave requests and managers can approve or reject them.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PARTIAL FAIL

Notes:
The model correctly extracted leave request submission and manager approval/rejection.
However, it introduced unsupported details such as start date, end date, leave reason, leave type, and predefined approval rules or policies.


---

## Test 05 — Restaurant Reservation
Input:
Create a restaurant reservation system where customers can view available tables and book a table.

Input:
Create a restaurant reservation system where customers can view available tables and book a table.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PARTIAL FAIL

Notes:
The model correctly extracted table availability viewing and table booking.
However, it introduced unsupported details such as real-time availability
and booking for a specific time.

---

## Test 06 — School Management
Input:
Build a school management system for maintaining student records, teacher records and attendance.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PARTIAL FAIL

Notes:
The model correctly identified student records, teacher records, and attendance management.
However, it expanded the vague word "maintaining" into unsupported operations such as adding, updating, and viewing records.

---

## Test 07 — CRM
Input:
Create a CRM system where sales staff can add leads, update lead status and view customer information.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PARTIAL FAIL
Coverage: PARTIAL

Notes:
The model correctly identified all three requested actions and generated three corresponding user stories.

However, it merged the three actions into a single "Lead Management" feature instead of creating separate features.

Some user-story benefits were also inferred, such as efficiently tracking potential customers and improving lead management, even though these benefits were not explicitly stated by the client.

---

## Test 08 — Food Delivery
Input:
Build a food delivery application where users can browse restaurants, select food items and place an order.


Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: PASS

Notes:
The model correctly extracted the three requested features:
restaurant browsing, food item selection, and order placement.

No obvious unsupported functionality was introduced.

---

## Test 09 — Freelancer Marketplace
Input:
Create a freelancer marketplace where clients can post jobs and freelancers can submit proposals.

Functional Result: PASS
Schema Validation: PASS
Evidence Fidelity: FAIL
Overgeneration: FAIL

Notes:
The model correctly identified the two explicitly requested capabilities:
job posting by clients and proposal submission by freelancers.

However, it introduced several unsupported features and details, including:
- Job search functionality
- Proposal review and accept/reject functionality
- Job title, description, location, and deadline
- Freelancer name, experience, and proposed rate
- Software developer jobs in New York
- Web development projects
- Payment-related benefit language

These details were not present in the client requirement.

Open Questions were also not generated despite missing workflow details.
---

## Test 10 — Ambiguous Requirement / Hallucination Test
Input:
I need an app like Uber. Make it modern and launch it quickly.

Generation Pipeline: PASS
Schema Validation: PASS
Evidence Fidelity: FAIL
Hallucination Control: FAIL
Uncertainty Handling: FAIL
Open Question Generation: FAIL

Notes:
The input was intentionally vague and did not explicitly specify functional requirements.

The model invented several unsupported details and features, including:
- User registration using email and password
- Driver role
- Driver availability
- Vehicle details
- Ride booking based on location and time
- Real-time ride tracking
- Payment processing
- Driver earnings and service-related benefits

The model also generated zero open questions, even though the requirement required significant clarification.

Expected Behavior:
The system should avoid treating common Uber functionality as confirmed client requirements.
It should instead generate clarification questions about the required user roles,
core features, payment requirements, location/tracking needs, target platform,
and the meaning of "launch quickly".

Conclusion:
This test demonstrates a significant hallucination and uncertainty-handling weakness
in Qwen3 1.7B with the current Day 1 prompt.
This failure should be revisited during Day 4 reliability and hallucination evaluation.

---

# Known Failure Case

Qwen3 4B exceeded the 300-second application timeout on CPU-only hardware.

A one-word generation test took approximately 60 seconds.

Decision:
Switched the active Day 1 model to Qwen3 1.7B for improved responsiveness while staying within the required local Qwen3 model family.