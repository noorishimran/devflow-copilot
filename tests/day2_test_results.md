# Day 2 Multimodal Test Results

Models:
- Text Model: Qwen3 1.7B
- Vision Model: Qwen3-VL 2B Instruct
- Runtime: Ollama
- Execution: Local-only

---

## Image-Only Test 01 — Instagram Login Screen

Input:
Instagram login page screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
UI Component Extraction: PASS
Observed vs Assumed Handling: PARTIAL PASS

Observed Components:
- Username/mobile/email text field
- Password field
- Login button
- Log in with Facebook button
- Create new account button
- Login heading

Observed Facts:
- Instagram login page is visible.

Notes:
The vision model correctly extracted the major visible UI elements.

However, some visible states such as "button active" or "button inactive"
may not be fully supported by the screenshot and should be treated cautiously.

The downstream requirement model generated "Login functionality".
This is a reasonable inference from the visible login form, but image evidence
alone does not prove the backend login behavior.

Conclusion:
The multimodal pipeline works successfully, but evidence-fidelity review is
still required before treating inferred functionality as confirmed requirements.


## Image-Only Test 02 — Shopping Cart Page

Input:
Shopping cart / shopping bag screenshot containing products, quantities,
prices, checkout controls, order summary and promotional content.

Initial Result:
FAIL — the vision model returned malformed JSON.

Fix:
A local JSON repair step was added before Pydantic validation.

Retest Result:
Pipeline: PASS
Vision JSON Recovery: PASS
Vision Schema Validation: PASS
UI Component Extraction: PASS
Evidence Fidelity: PASS
Output Conciseness: PARTIAL FAIL
Uncertainty Handling: PARTIAL

Observed Evidence Included:
- Shopping bag heading
- Product table
- Product images
- Checkout button
- Order summary
- Item subtotal
- Estimated total
- Promotion code
- Apply button
- Customer support controls

Notes:
The vision model successfully extracted many visible UI elements from
the complex shopping cart screenshot.

However, it returned 26 UI components despite the prompt requesting no more
than 6 components. This demonstrates over-extraction and shows that prompt
instructions alone do not guarantee output limits.

The system successfully recovered from malformed model JSON using the local
JSON repair step.

No major unsupported backend behavior was visible in the extracted evidence.



## Image-Only Test 03 — Google Account Dashboard

Input:
Google Account dashboard screenshot showing recently used Google services.

Result:
Pipeline: PASS
Vision Schema Validation: PASS
Specification Schema Validation: PASS
Evidence Extraction: PASS
Evidence Fidelity: PASS
Output Conciseness: FAIL

Observed Evidence Included:
- Google Account heading
- Google Dashboard heading
- Recently used Google services section
- Gmail metrics
- Google Play metrics
- Settings controls
- Help Center controls
- Download controls

Generated Specification:
- View Recently Used Google Services
- View Service Metrics
- Access Service Actions

Notes:
The vision model correctly identified the main dashboard sections,
service cards, visible metrics and action controls.

However, it extracted 26 UI components despite the prompt requesting
a maximum of 6 components. This is an over-extraction limitation.

No obvious unsupported backend technology or hidden business rules
were introduced.



## Image-Only Test 04 — GitHub Dashboard

Input:
GitHub dashboard screenshot showing repository search, dashboard controls,
action buttons and repository-related navigation.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
Evidence Extraction: PASS
Evidence Fidelity: PARTIAL PASS
Output Conciseness: FAIL

Observed Evidence Included:
- Repository search field
- New button
- Home heading
- Ask control
- Create issue control
- Pull requests control
- Download for Windows control
- Star control
- Filter control

Generated Specification:
- Search Repositories

Notes:
The multimodal pipeline completed successfully without a runtime or JSON error.

The model correctly identified major visible GitHub dashboard controls and
generated a schema-validated specification.

However, the vision model over-extracted UI components and returned 29
components. Several button observations were repeated multiple times.

Some extracted controls should therefore be reviewed against the screenshot
before being treated as confirmed evidence.

Conclusion:
Core multimodal processing passed, but duplicate/over-extracted component
handling requires improvement.



## Image-Only Test 05 — Trello Landing Page

Input:
Trello landing page screenshot showing navigation, hero content,
call-to-action controls and a mobile product preview.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
UI Component Limit: PASS
Evidence Extraction: PASS
Evidence Fidelity: PARTIAL PASS

Observed Evidence Included:
- Browser address bar showing trello.com
- Main hero heading
- Trello mobile preview image
- Get Trello for free control
- Features navigation item
- Trello logo

Visible States:
- Address bar contains trello.com
- Get Trello for free control is visible
- Navigation content is visible

Generated Specification:
- Get Trello for free

Notes:
The multimodal pipeline completed successfully.

The component deduplication and maximum component cap worked correctly,
returning 6 UI components instead of the previous over-extracted outputs.

Some state descriptions such as whether a control is clickable or whether
a navigation menu is open are inferred rather than fully proven by the
static screenshot, so evidence fidelity is marked as partial pass.

Conclusion:
Image-only multimodal processing works successfully with bounded,
schema-validated output.


## Combined Test 01 — Instagram Login Page

Inputs:

Client Text:
Build a login page where users can enter their mobile number, username, or
email address and a password to log in. Also provide an option to create
a new account.

Image:
Instagram login page screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
UI Component Limit: PASS
Text + Image Combination: PASS
Evidence Separation: PASS
Evidence Fidelity: PARTIAL PASS

Vision Output:
- UI Components: 6
- Visible States: 3
- Assumptions: 4
- Open Questions: 0

Observed Evidence Included:
- Mobile number / username / email field
- Password field
- Login button
- Forgot password link
- Log in with Facebook button
- Create new account button

Generated Specification:
- Login Form
- Account Creation

Notes:
The system successfully combined client-provided text with screenshot evidence.

The screenshot supplied additional visible evidence such as the Forgot password
link and Log in with Facebook control.

Vision assumptions were kept separate from confirmed evidence and were not
promoted into the final specification.

Some state labels such as "active" and "inactive" are not fully provable from
a static screenshot, so evidence fidelity is marked as partial pass.

No unsupported backend technology, API, database, OTP flow, or password rules
were added.

Conclusion:
Combined text-and-image processing completed successfully with bounded,
schema-validated output.



## Combined Test 02 — Shopify Login Page

Inputs:

Client Text:
Build a store login page where existing users can log in, and new users can
access an option to start for free.

Image:
Shopify login page screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
Text + Image Combination: PASS
UI Component Limit: PASS
Evidence Separation: PASS
Evidence Fidelity: PASS
Feature Coverage: PARTIAL PASS

Vision Output:
- UI Components: 5
- Visible States: 2
- Assumptions: 2
- Open Questions: 0

Observed Evidence Included:
- Login button
- Log in to Shopify heading
- Shopify descriptive text
- Start for free button
- New to Shopify section

Generated Specification:
- Login Functionality

Notes:
The client text and screenshot evidence were consistent.

The system correctly generated a store login specification and retained
the visible Start for free option.

The final specification grouped login and the new-user start option into
one feature rather than two separate features, so feature coverage is
marked as partial pass.

No unsupported backend technology, API, database, payment logic, or
authentication implementation was added.

Conclusion:
Combined text-and-image processing completed successfully with
schema-validated output.



## Combined Test 03 — Google Account Dashboard

Inputs:

Client Text:
Build an account dashboard where users can view recently used services,
see service-related information, and access available actions such as
settings and help.

Image:
Google Account Dashboard screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
Text + Image Combination: PASS
UI Component Limit: PASS
Evidence Separation: PASS
Evidence Fidelity: PARTIAL PASS

Vision Output:
- UI Components: 6
- Visible States: 1
- Assumptions: 1
- Open Questions: 0

Observed Evidence Included:
- Google Dashboard heading
- Download your data control
- Delete a service control
- Recently used Google services section
- Gmail service information
- Google Play service information

Generated Specification:
- View Recently Used Services
- Access Service Information
- Manage Services

Final Specification:
- Features: 3
- User Stories: 1
- Assumptions: 1
- Open Questions: 1

Notes:
The system successfully combined client text with visible dashboard evidence.

The model correctly extracted recently used services and service-related
information from the screenshot.

The screenshot also contained visible controls for downloading data and
deleting a service, which were incorporated into the generated specification.

Some interpretation was placed into assumptions/open questions, therefore
evidence fidelity is marked as partial pass rather than full pass.

No unsupported backend technologies, APIs, payment systems, or hidden
implementation details were introduced.

Conclusion:
Combined Google Dashboard analysis completed successfully with
schema-validated multimodal output.



## Combined Test 04 — GitHub Developer Dashboard

Inputs:

Client Text:
Build a developer dashboard where users can search repositories, create issues,
view pull requests, and access repository-related actions.

Image:
GitHub dashboard screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
Text + Image Combination: PASS
UI Component Limit: PASS
Evidence Fidelity: PARTIAL PASS
Feature Coverage: PARTIAL FAIL

Vision Output:
- UI Components: 6
- Visible States: 3
- Assumptions: 2
- Open Questions: 0

Observed Evidence Included:
- Repository search field
- Repository list
- Home heading
- Ask control
- Download for Windows control
- GitHub Copilot card

Generated Specification:
- Search Repositories

Notes:
The multimodal pipeline executed successfully and produced schema-valid output.

The system correctly identified the repository search interface, but the final
specification did not fully preserve all client-requested capabilities.

Client-requested Create Issue and Pull Request capabilities were not represented
as separate generated features.

Some visible-state descriptions were also interpretive rather than clearly
supported by the static screenshot.

Conclusion:
Combined GitHub analysis is operational, but feature coverage remains incomplete.
This is a documented Day 2 limitation for later reliability improvements.



## Combined Test 05 — Trello Productivity Page

Inputs:

Client Text:
Build a productivity page where users can organize tasks and access an option
to get started for free.

Image:
Trello landing page screenshot.

Result:
Pipeline: PASS
Vision JSON Validation: PASS
Specification Schema Validation: PASS
Text + Image Combination: PASS
UI Component Limit: PASS
Evidence Separation: PASS
Evidence Fidelity: PARTIAL FAIL
Overall Result: PARTIAL PASS

Vision Output:
- UI Components: 6
- Visible States: 1
- Assumptions: 1
- Open Questions: 0

Correctly Observed Evidence:
- Productivity/to-do heading
- Trello mobile interface image
- Get Trello for free control
- Productivity-related descriptive text
- Trello website context

Unsupported / Incorrect Evidence:
- The model reported an "Allow" button that was not supported by the screenshot.
- The model reported that Chrome was "in the process of launching", which
  cannot be established from a static screenshot.

Generated Specification:
- Features: 1
- User Stories: 1
- Assumptions: 0
- Open Questions: 0

Notes:
The multimodal pipeline completed successfully and generated schema-valid output.

Most high-level screenshot evidence was extracted correctly, but the vision model
introduced unsupported UI/state details. These were identified during human review.

The generated specification remained limited and did not introduce backend APIs,
databases, notifications, team permissions, or hidden Trello functionality.

Conclusion:
The final Day 2 combined test demonstrates that the multimodal pipeline works
end-to-end, while also showing that vision-model hallucinations remain a known
limitation requiring human review and future reliability improvements.