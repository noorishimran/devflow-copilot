import html
from textwrap import dedent

import streamlit as st

from app.services.requirement_service import generate_specification
from app.services.multimodal_service import generate_multimodal_specification
from app.services.engineering_service import generate_engineering_artifacts


st.set_page_config(
    page_title="MoinSystems AI - DevFlow Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top right, #eef2ff 0%, transparent 25%),
            #f8fafc;
    }
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    section[data-testid="stSidebar"] {
        background: #111827;
    }
    section[data-testid="stSidebar"] * {
        color: #f9fafb;
    }
    .hero {
        padding: 32px 36px;
        border-radius: 22px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #312e81 100%);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 35px rgba(15, 23, 42, 0.15);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 13px;
        margin-bottom: 14px;
    }
    .hero h1 {
        margin: 0;
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1.2px;
    }
    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        color: #d1d5db;
        font-size: 16px;
        max-width: 900px;
    }
    .section-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 5px 20px rgba(15,23,42,0.04);
        margin-bottom: 14px;
    }
    .summary-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4f46e5;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 20px;
    }
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        min-height: 150px;
        box-shadow: 0 5px 16px rgba(15,23,42,0.04);
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #111827;
    }
    .feature-description {
        color: #4b5563;
        font-size: 14px;
        line-height: 1.55;
        margin-top: 10px;
    }
    .priority-high, .priority-medium, .priority-low {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }
    .priority-high { background: #fee2e2; color: #991b1b; }
    .priority-medium { background: #fef3c7; color: #92400e; }
    .priority-low { background: #dcfce7; color: #166534; }
    .story-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .story-id {
        color: #4f46e5;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.6px;
    }
    .story-role {
        margin-top: 8px;
        font-size: 15px;
        font-weight: 700;
        color: #111827;
    }
    .story-line {
        color: #475569;
        margin-top: 6px;
        font-size: 14px;
    }
    .empty-box {
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 14px;
        padding: 18px;
        color: #64748b;
    }
    .draft-notice {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        border-radius: 14px;
        padding: 13px 16px;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .runtime-box {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .runtime-label {
        color: #9ca3af;
        font-size: 12px;
        margin-bottom: 3px;
    }
    .runtime-value {
        color: white;
        font-weight: 700;
        font-size: 14px;
    }
    .evidence-card {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-left: 5px solid #2563eb;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }
    .mode-note {
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 15px;
        color: #3730a3;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 48px;
        font-weight: 700;
        border: none;
    }
    textarea {
        border-radius: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe(value: str) -> str:
    return html.escape(str(value))


def render_html(content: str) -> None:
    normalized = " ".join(dedent(content).split())
    st.markdown(normalized, unsafe_allow_html=True)


for key, default in {
    "specification": None,
    "image_evidence": None,
    "normalized_context": None,
    "engineering_artifacts": None,
    "engineering_error": None,
    "last_error": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with st.sidebar:
    st.markdown("## ⚡ DevFlow Copilot")
    st.caption("MoinSystems AI")
    st.markdown("---")
    st.markdown("### Runtime")

    st.markdown(
        """
        <div class="runtime-box">
            <div class="runtime-label">TEXT MODEL</div>
            <div class="runtime-value">Qwen3 1.7B</div>
        </div>
        <div class="runtime-box">
            <div class="runtime-label">VISION MODEL</div>
            <div class="runtime-value">Qwen3-VL 2B Instruct</div>
        </div>
        <div class="runtime-box">
            <div class="runtime-label">MODEL RUNTIME</div>
            <div class="runtime-value">Ollama</div>
        </div>
        <div class="runtime-box">
            <div class="runtime-label">PROMPTS</div>
            <div class="runtime-value">requirement_prompt_v2 + image_analysis_prompt_v1 + engineering_artifacts_prompt_v1</div>
        </div>
        <div class="runtime-box">
            <div class="runtime-label">EXECUTION</div>
            <div class="runtime-value">Local-only</div>
        </div>
        <div class="runtime-box">
            <div class="runtime-label">PAID API</div>
            <div class="runtime-value">None</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Day 3 • Engineering Artifacts + Multimodal Requirements")


render_html(
    """
    <div class="hero">
        <div class="hero-badge">DAY 3 • ENGINEERING ARTIFACT GENERATOR</div>
        <h1>DevFlow Copilot</h1>
        <p>
            Analyze client text, UI screenshots, or both. Generate a schema-validated
            software specification, then convert it into acceptance criteria,
            implementation plans, QA test cases, and a developer implementation prompt.
        </p>
    </div>
    """
)

render_html(
    """
    <div class="draft-notice">
        ⚠️ <b>AI-generated draft:</b>
        Screenshot observations and generated requirements require human review.
        The system must not treat assumptions as confirmed client facts.
    </div>
    """
)

st.markdown("## Input")

mode = st.radio(
    "Choose evidence source",
    ["Text only", "Image only", "Text + Image"],
    horizontal=True,
)

mode_map = {
    "Text only": "text_only",
    "Image only": "image_only",
    "Text + Image": "combined",
}
selected_mode = mode_map[mode]

client_text = ""
uploaded_image = None

left, right = st.columns([2.2, 1], gap="large")

with left:
    if selected_mode in {"text_only", "combined"}:
        st.markdown("### Client Requirement")
        client_text = st.text_area(
            "Requirement text",
            label_visibility="collapsed",
            height=190,
            placeholder=(
                "Paste client requirements or meeting notes here...\n\n"
                "Example:\n"
                "Build a login page where users can enter email and password."
            ),
            key="day2_client_text",
        )

    if selected_mode in {"image_only", "combined"}:
        st.markdown("### Requirement Screenshot / Wireframe")
        uploaded_image = st.file_uploader(
            "Upload PNG, JPG or JPEG",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key="day2_image",
        )

        if uploaded_image is not None:
            st.image(
                uploaded_image,
                caption="Uploaded screenshot",
                use_container_width=True,
            )

with right:
    st.markdown("### Day 2 analysis")
    render_html(
        """
        <div class="section-card">
            <b>👁 Observed UI Evidence</b><br><br>
            <span style="color:#64748b;">Components, labels, visible states and screenshot-supported facts.</span><br><br>
            <b>🖱 Possible Interactions</b><br><br>
            <span style="color:#64748b;">Interactions suggested by visible controls without inventing outcomes.</span><br><br>
            <b>⚠ Assumptions</b><br><br>
            <span style="color:#64748b;">Plausible but unconfirmed information kept separate from evidence.</span><br><br>
            <b>❓ Open Questions</b><br><br>
            <span style="color:#64748b;">Missing information that needs client clarification.</span>
        </div>
        """
    )

if selected_mode == "text_only":
    render_html('<div class="mode-note"><b>Text-only mode:</b> Uses the Day 1 text pipeline.</div>')
elif selected_mode == "image_only":
    render_html('<div class="mode-note"><b>Image-only mode:</b> Qwen3-VL analyzes the screenshot first, then the evidence is normalized before requirement generation.</div>')
else:
    render_html('<div class="mode-note"><b>Combined mode:</b> Client text and screenshot evidence are analyzed together while keeping observed facts separate from assumptions.</div>')

generate_button = st.button(
    "✨ Analyze Evidence & Generate Specification",
    type="primary",
    use_container_width=True,
)

if generate_button:
    st.session_state.last_error = None
    st.session_state.specification = None
    st.session_state.image_evidence = None
    st.session_state.normalized_context = None
    st.session_state.engineering_artifacts = None
    st.session_state.engineering_error = None

    try:
        if selected_mode == "text_only":
            if not client_text.strip():
                raise ValueError("Please enter a client requirement before generating.")

            with st.spinner("Local Qwen text model is analyzing the requirement..."):
                specification = generate_specification(client_text)

            st.session_state.specification = specification

        else:
            if uploaded_image is None:
                raise ValueError("Please upload a screenshot or image before generating.")

            image_bytes = uploaded_image.getvalue()

            if selected_mode == "combined" and not client_text.strip():
                raise ValueError("Combined mode requires both client text and an image.")

            with st.spinner(
                "Qwen3-VL is analyzing the screenshot, then the text model will generate the structured specification..."
            ):
                specification, image_evidence, normalized_context = (
                    generate_multimodal_specification(
                        client_text=client_text,
                        image_bytes=image_bytes,
                    )
                )

            st.session_state.specification = specification
            st.session_state.image_evidence = image_evidence
            st.session_state.normalized_context = normalized_context

        st.success("Analysis completed and specification schema validated successfully.")

    except ValueError as exc:
        st.session_state.last_error = f"Input Error: {exc}"
    except RuntimeError as exc:
        st.session_state.last_error = f"Generation Error: {exc}"
    except Exception as exc:
        st.session_state.last_error = f"Unexpected Error: {exc}"


if st.session_state.last_error:
    st.error(st.session_state.last_error)


image_evidence = st.session_state.image_evidence
context = st.session_state.normalized_context

if image_evidence is not None:
    st.markdown("---")
    st.markdown("## Screenshot Evidence Analysis")

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("UI Components", len(image_evidence.observed_components))
    metric2.metric("Visible States", len(image_evidence.visible_states))
    metric3.metric("Assumptions", len(image_evidence.assumptions))
    metric4.metric("Open Questions", len(image_evidence.open_questions))

    evidence_tab, interactions_tab, uncertainty_tab, context_tab = st.tabs(
        [
            "👁 Observed Evidence",
            "🖱 Interactions",
            "⚠ Observed vs Assumed",
            "🧩 Normalized Context",
        ]
    )

    with evidence_tab:
        st.markdown("### Observed UI Components")

        if image_evidence.observed_components:
            for index, component in enumerate(image_evidence.observed_components, start=1):
                label = component.label or "(no visible label)"
                state = component.state or "not specified"

                render_html(
                    f"""
                    <div class="evidence-card">
                        <b>{index}. {safe(component.component_type.title())}</b><br>
                        <b>Label:</b> {safe(label)}<br>
                        <b>State:</b> {safe(state)}<br>
                        <b>Visible text:</b> {safe(component.visible_text or "None")}<br>
                        <b>Evidence:</b> {safe(component.evidence)}
                    </div>
                    """
                )
        else:
            st.info("No UI components were confidently observed.")

        st.markdown("### Visible States")
        if image_evidence.visible_states:
            for item in image_evidence.visible_states:
                st.success(item)
        else:
            st.info("No explicit UI states were identified.")

        st.markdown("### Observed Facts")
        if image_evidence.observed_facts:
            for item in image_evidence.observed_facts:
                st.write(f"- {item}")
        else:
            st.info("No additional observed facts were returned.")

    with interactions_tab:
        st.markdown("### Possible Interactions")
        st.caption(
            "These interactions are suggested by visible controls. Their outcomes are not treated as confirmed."
        )

        if image_evidence.possible_interactions:
            for item in image_evidence.possible_interactions:
                st.write(f"- {item}")
        else:
            st.info("No supported interactions were identified.")

    with uncertainty_tab:
        observed_col, assumed_col = st.columns(2, gap="large")

        with observed_col:
            st.markdown("### ✅ Observed")
            observed_items = list(image_evidence.observed_facts)
            observed_items.extend(
                component.evidence
                for component in image_evidence.observed_components
            )

            if observed_items:
                for item in observed_items:
                    st.success(item)
            else:
                st.info("No observed evidence returned.")

        with assumed_col:
            st.markdown("### ⚠ Assumed / Inferred")
            if image_evidence.assumptions:
                for item in image_evidence.assumptions:
                    st.warning(item)
            else:
                st.success("No assumptions were returned by the vision analysis.")

        st.markdown("### ❓ Open Questions")
        if image_evidence.open_questions:
            for question in image_evidence.open_questions:
                st.info(question)
        else:
            st.info("No open questions were returned.")

    with context_tab:
        if context is not None:
            st.markdown("### Normalized Context Object")
            st.caption(
                "This object combines client text and screenshot evidence while preserving uncertainty."
            )
            st.json(context.model_dump())
        else:
            st.info("Normalized context is not available.")


result = st.session_state.specification

if result is not None:
    st.markdown("---")
    st.markdown("## Generated Specification")

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Features", len(result.features))
    metric2.metric("User Stories", len(result.user_stories))
    metric3.metric("Assumptions", len(result.assumptions))
    metric4.metric("Open Questions", len(result.open_questions))

    overview_tab, stories_tab, review_tab, json_tab = st.tabs(
        ["📋 Overview", "👤 User Stories", "🔎 Review", "🧾 Validated JSON"]
    )

    with overview_tab:
        st.markdown("### Project Summary")
        render_html(
            f"""
            <div class="summary-card">
                {safe(result.project_summary)}
            </div>
            """
        )

        st.markdown("### Features")
        feature_columns = st.columns(2)

        for index, feature in enumerate(result.features):
            priority = feature.priority.lower()
            priority_class = f"priority-{priority}"

            with feature_columns[index % 2]:
                render_html(
                    f"""
                    <div class="feature-card">
                        <div class="feature-title">{safe(feature.name)}</div>
                        <span class="{priority_class}">{safe(feature.priority.upper())}</span>
                        <div class="feature-description">{safe(feature.description)}</div>
                    </div>
                    """
                )

    with stories_tab:
        st.markdown("### User Stories")
        if result.user_stories:
            for index, story in enumerate(result.user_stories, start=1):
                render_html(
                    f"""
                    <div class="story-card">
                        <div class="story-id">US-{index:03d}</div>
                        <div class="story-role">👤 {safe(story.role)}</div>
                        <div class="story-line"><b>Goal:</b> {safe(story.goal)}</div>
                        <div class="story-line"><b>Benefit:</b> {safe(story.benefit)}</div>
                    </div>
                    """
                )
        else:
            st.info("No user stories were generated.")

    with review_tab:
        assumption_col, question_col = st.columns(2, gap="large")

        with assumption_col:
            st.markdown("### Assumptions")
            if result.assumptions:
                for assumption in result.assumptions:
                    st.warning(assumption)
            else:
                render_html('<div class="empty-box">✓ No assumptions returned.</div>')

        with question_col:
            st.markdown("### Open Questions")
            if result.open_questions:
                for question in result.open_questions:
                    st.info(question)
            else:
                render_html('<div class="empty-box">No open questions returned.</div>')

        st.markdown("### Review Status")
        st.warning("Draft — human review required before approval.")

    with json_tab:
        st.markdown("### Schema-Validated Output")
        st.caption("This JSON successfully passed the project specification Pydantic schema.")
        st.json(result.model_dump())



# -------------------------------------------------------------------
# Day 3 — Engineering Artifacts
# -------------------------------------------------------------------

if result is not None:
    st.markdown("---")
    st.markdown("## Day 3 — Engineering Artifacts")

    render_html(
        """
        <div class="mode-note">
            <b>Engineering-ready output:</b>
            Convert the validated specification into acceptance criteria,
            a technology-neutral implementation plan, QA test cases, and
            a developer implementation prompt. Unsupported behavior is
            rejected by the evidence-fidelity safety layer.
        </div>
        """
    )

    engineering_button = st.button(
        "🛠 Generate Engineering Artifacts",
        type="primary",
        use_container_width=True,
        key="generate_engineering_artifacts",
    )

    if engineering_button:
        st.session_state.engineering_error = None
        st.session_state.engineering_artifacts = None

        try:
            with st.spinner(
                "Generating acceptance criteria, implementation plan, QA tests, "
                "and developer prompt with local Qwen..."
            ):
                engineering_artifacts = generate_engineering_artifacts(
                    result
                )

            st.session_state.engineering_artifacts = engineering_artifacts
            st.success(
                "Engineering artifacts generated, schema validated, "
                "and evidence-fidelity checked."
            )

        except ValueError as exc:
            st.session_state.engineering_error = (
                f"Engineering Input Error: {exc}"
            )

        except RuntimeError as exc:
            st.session_state.engineering_error = (
                f"Engineering Generation Error: {exc}"
            )

        except Exception as exc:
            st.session_state.engineering_error = (
                f"Unexpected Engineering Error: {exc}"
            )

    if st.session_state.engineering_error:
        st.error(st.session_state.engineering_error)


engineering = st.session_state.engineering_artifacts

if engineering is not None:
    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Acceptance Criteria",
        len(engineering.acceptance_criteria),
    )
    metric2.metric(
        "Implementation Steps",
        len(engineering.implementation_plan),
    )
    metric3.metric(
        "QA Test Cases",
        len(engineering.qa_test_cases),
    )
    metric4.metric(
        "Open Questions",
        len(engineering.open_questions),
    )

    (
        criteria_tab,
        plan_tab,
        qa_tab,
        developer_tab,
        engineering_review_tab,
        engineering_json_tab,
    ) = st.tabs(
        [
            "✅ Acceptance Criteria",
            "🧭 Implementation Plan",
            "🧪 QA Test Cases",
            "💻 Developer Prompt",
            "🔎 Review",
            "🧾 Validated JSON",
        ]
    )

    with criteria_tab:
        st.markdown("### Acceptance Criteria")

        if engineering.acceptance_criteria:
            for criterion in engineering.acceptance_criteria:
                render_html(
                    f"""
                    <div class="section-card">
                        <b>{safe(criterion.id)} • {safe(criterion.feature)}</b>
                        <br><br>
                        <b>Given:</b> {safe(criterion.given)}
                        <br>
                        <b>When:</b> {safe(criterion.when)}
                        <br>
                        <b>Then:</b> {safe(criterion.then)}
                    </div>
                    """
                )
        else:
            st.info(
                "No safe acceptance criteria were returned. "
                "Missing behavior may have been moved to open questions."
            )

    with plan_tab:
        st.markdown("### Implementation Plan")

        if engineering.implementation_plan:
            for step in engineering.implementation_plan:
                render_html(
                    f"""
                    <div class="section-card">
                        <b>Step {step.step_number}: {safe(step.title)}</b>
                        <br><br>
                        {safe(step.description)}
                    </div>
                    """
                )

                if step.files_or_components:
                    st.markdown("**Files / Components**")
                    for item in step.files_or_components:
                        st.write(f"- {item}")

                if step.dependencies:
                    st.markdown("**Dependencies**")
                    for item in step.dependencies:
                        st.write(f"- {item}")
        else:
            st.info("No safe implementation steps were returned.")

    with qa_tab:
        st.markdown("### QA Test Cases")

        if engineering.qa_test_cases:
            for test_case in engineering.qa_test_cases:
                render_html(
                    f"""
                    <div class="section-card">
                        <b>{safe(test_case.test_id)} • {safe(test_case.title)}</b>
                        <br>
                        <span class="priority-medium">{safe(test_case.test_type.upper())}</span>
                        <br><br>
                        <b>Expected Result:</b> {safe(test_case.expected_result)}
                    </div>
                    """
                )

                if test_case.preconditions:
                    st.markdown("**Preconditions**")
                    for item in test_case.preconditions:
                        st.write(f"- {item}")

                st.markdown("**Steps**")
                for index, item in enumerate(test_case.steps, start=1):
                    st.write(f"{index}. {item}")
        else:
            st.info(
                "No safe QA test cases were returned. "
                "Unsupported generated tests may have been removed by the safety layer."
            )

    with developer_tab:
        st.markdown("### Developer Implementation Prompt")

        render_html(
            f"""
            <div class="summary-card">
                <b>Objective</b><br><br>
                {safe(engineering.developer_prompt.objective)}
            </div>
            """
        )

        st.markdown("#### Implementation Instructions")
        for instruction in engineering.developer_prompt.implementation_instructions:
            st.write(f"- {instruction}")

        st.markdown("#### Constraints")
        if engineering.developer_prompt.constraints:
            for constraint in engineering.developer_prompt.constraints:
                st.warning(constraint)
        else:
            st.info("No additional constraints returned.")

        st.markdown("#### Unknowns")
        if engineering.developer_prompt.unknowns:
            for unknown in engineering.developer_prompt.unknowns:
                st.info(unknown)
        else:
            st.success("No developer unknowns returned.")

    with engineering_review_tab:
        assumption_col, question_col = st.columns(2, gap="large")

        with assumption_col:
            st.markdown("### Assumptions")
            if engineering.assumptions:
                for assumption in engineering.assumptions:
                    st.warning(assumption)
            else:
                render_html(
                    '<div class="empty-box">✓ No engineering assumptions returned.</div>'
                )

        with question_col:
            st.markdown("### Open Questions")
            if engineering.open_questions:
                for question in engineering.open_questions:
                    st.info(question)
            else:
                render_html(
                    '<div class="empty-box">No engineering open questions returned.</div>'
                )

        st.markdown("### Safety Status")
        st.success(
            "Output passed schema validation and the Day 3 "
            "evidence-fidelity safety check."
        )
        st.warning(
            "Draft — human review is still required before implementation."
        )

    with engineering_json_tab:
        st.markdown("### Schema-Validated Engineering Output")
        st.caption(
            "This JSON passed the EngineeringArtifacts Pydantic schema "
            "and the evidence-fidelity safety layer."
        )
        st.json(engineering.model_dump())


st.markdown("---")
st.caption(
    "MoinSystems AI • DevFlow Copilot • Day 3 Engineering Artifacts + "
    "Multimodal Local-first GenAI Internship MVP"
)
