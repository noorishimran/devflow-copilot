import html
from textwrap import dedent
import streamlit as st

from app.services.requirement_service import generate_specification


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="MoinSystems AI - DevFlow Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

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
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 55%,
            #312e81 100%
        );
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
        max-width: 850px;
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
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #f8fafc 100%
        );
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

    .priority-high {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }

    .priority-medium {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }

    .priority-low {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }

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

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 48px;
        font-weight: 700;
        border: none;
        background: linear-gradient(
            90deg,
            #4f46e5,
            #7c3aed
        );
    }

    div.stButton > button:hover {
        border: none;
        transform: translateY(-1px);
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


def render_html(content: str):
    # Streamlit/Markdown can interpret indented multiline HTML as a code block.
    # Normalize the HTML to one line before rendering so tags are always parsed.
    normalized = " ".join(dedent(content).split())
    st.markdown(
        normalized,
        unsafe_allow_html=True
    )



# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## ⚡ DevFlow Copilot")
    st.caption("MoinSystems AI")

    st.markdown("---")

    st.markdown("### Runtime")

    render_html(
        """
        <div class="runtime-box">
            <div class="runtime-label">LOCAL MODEL</div>
            <div class="runtime-value">Qwen3 1.7B</div>
        </div>

        <div class="runtime-box">
            <div class="runtime-label">MODEL RUNTIME</div>
            <div class="runtime-value">Ollama</div>
        </div>

        <div class="runtime-box">
            <div class="runtime-label">PROMPT VERSION</div>
            <div class="runtime-value">requirement_prompt_v2</div>
        </div>

        <div class="runtime-box">
            <div class="runtime-label">EXECUTION</div>
            <div class="runtime-value">Local-only</div>
        </div>

        <div class="runtime-box">
            <div class="runtime-label">PAID API</div>
            <div class="runtime-value">None</div>
        </div>
        """
    )

    st.markdown("---")

    st.caption(
        "Day 1 • Text → Structured Requirements"
    )


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

render_html(
    """
    <div class="hero">
        <div class="hero-badge">
            DAY 1 • GENAI FOUNDATION
        </div>

        <h1>DevFlow Copilot</h1>

        <p>
            Convert messy client requirements into structured,
            reviewable software specifications using a fully local
            Generative AI pipeline.
        </p>
    </div>
    """
)


render_html(
    """
    <div class="draft-notice">
        ⚠️ <b>AI-generated draft:</b>
        Generated specifications require human review before
        they should be treated as approved project requirements.
    </div>
    """
)


# ---------------------------------------------------------
# INPUT AREA
# ---------------------------------------------------------

left, right = st.columns([2.2, 1], gap="large")

with left:

    st.markdown("### Client Requirement")

    client_requirement = st.text_area(
        "Requirement text",
        label_visibility="collapsed",
        height=230,
        placeholder=(
            "Paste client requirements or meeting notes here...\n\n"
            "Example:\n"
            "Build an appointment booking system where patients "
            "can register, login, search doctors and book appointments."
        ),
    )

    generate_button = st.button(
        "✨ Generate Structured Specification",
        type="primary",
        use_container_width=True,
    )


with right:

    st.markdown("### What DevFlow generates")

    render_html(
        """
        <div class="section-card">
            <div style="margin-bottom:20px;">
                <b>📌 Project Summary</b><br>
                <span style="color:#64748b;">
                    Concise understanding of the client request.
                </span>
            </div>

            <div style="margin-bottom:20px;">
                <b>🧩 Features</b><br>
                <span style="color:#64748b;">
                    Structured functional requirements.
                </span>
            </div>

            <div style="margin-bottom:20px;">
                <b>👤 User Stories</b><br>
                <span style="color:#64748b;">
                    Role, goal and business benefit.
                </span>
            </div>

            <div>
                <b>❓ Open Questions</b><br>
                <span style="color:#64748b;">
                    Missing information requiring clarification.
                </span>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------
# GENERATION
# ---------------------------------------------------------

if generate_button:

    if not client_requirement.strip():

        st.error(
            "Please enter a client requirement before generating."
        )

    else:

        try:

            with st.spinner(
                "Local Qwen model is analyzing the requirement..."
            ):

                result = generate_specification(
                    client_requirement
                )

            st.success(
                "Specification generated and schema validated successfully."
            )

            st.markdown("---")

            # -------------------------------------------------
            # RESULT HEADER
            # -------------------------------------------------

            st.markdown("## Generated Specification")

            metric1, metric2, metric3, metric4 = st.columns(4)

            metric1.metric(
                "Features",
                len(result.features)
            )

            metric2.metric(
                "User Stories",
                len(result.user_stories)
            )

            metric3.metric(
                "Assumptions",
                len(result.assumptions)
            )

            metric4.metric(
                "Open Questions",
                len(result.open_questions)
            )


            overview_tab, stories_tab, review_tab, json_tab = st.tabs(
                [
                    "📋 Overview",
                    "👤 User Stories",
                    "🔎 Review",
                    "🧾 Validated JSON",
                ]
            )


            # -------------------------------------------------
            # OVERVIEW TAB
            # -------------------------------------------------

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

                    priority_class = (
                        f"priority-{priority}"
                    )

                    with feature_columns[index % 2]:

                        render_html(
                            f"""
                            <div class="feature-card">

                                <div class="feature-title">
                                    {safe(feature.name)}
                                </div>

                                <span class="{priority_class}">
                                    {safe(feature.priority.upper())}
                                </span>

                                <div class="feature-description">
                                    {safe(feature.description)}
                                </div>

                            </div>
                            """
                        )


            # -------------------------------------------------
            # STORIES TAB
            # -------------------------------------------------

            with stories_tab:

                st.markdown("### User Stories")

                if result.user_stories:

                    for index, story in enumerate(
                        result.user_stories,
                        start=1
                    ):

                        render_html(
                            f"""
                            <div class="story-card">

                                <div class="story-id">
                                    US-{index:03d}
                                </div>

                                <div class="story-role">
                                    👤 {safe(story.role)}
                                </div>

                                <div class="story-line">
                                    <b>Goal:</b>
                                    {safe(story.goal)}
                                </div>

                                <div class="story-line">
                                    <b>Benefit:</b>
                                    {safe(story.benefit)}
                                </div>

                            </div>
                            """
                        )

                else:

                    st.info(
                        "No user stories were generated."
                    )


            # -------------------------------------------------
            # REVIEW TAB
            # -------------------------------------------------

            with review_tab:

                assumption_col, question_col = st.columns(
                    2,
                    gap="large"
                )

                with assumption_col:

                    st.markdown("### Assumptions")

                    if result.assumptions:

                        for assumption in result.assumptions:

                            st.warning(
                                assumption
                            )

                    else:

                        render_html(
                            """
                            <div class="empty-box">
                                ✓ No assumptions returned.
                            </div>
                            """
                        )


                with question_col:

                    st.markdown("### Open Questions")

                    if result.open_questions:

                        for question in result.open_questions:

                            st.info(
                                question
                            )

                    else:

                        render_html(
                            """
                            <div class="empty-box">
                                No open questions returned.
                            </div>
                            """
                        )


                st.markdown("### Review Status")

                st.warning(
                    "Draft — human review required before approval."
                )


            # -------------------------------------------------
            # JSON TAB
            # -------------------------------------------------

            with json_tab:

                st.markdown(
                    "### Schema-Validated Output"
                )

                st.caption(
                    "This JSON successfully passed the Day 1 Pydantic schema."
                )

                st.json(
                    result.model_dump()
                )


        except ValueError as exc:

            st.error(
                f"Input Error: {exc}"
            )

        except RuntimeError as exc:

            st.error(
                f"Generation Error: {exc}"
            )

        except Exception as exc:

            st.error(
                f"Unexpected Error: {exc}"
            )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "MoinSystems AI • DevFlow Copilot • "
    "Local-first GenAI Internship MVP"
)