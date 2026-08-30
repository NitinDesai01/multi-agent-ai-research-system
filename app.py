import streamlit as st

from pipeline import run_research_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent AI Research System",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔎 Multi-Agent AI Research System")

st.caption(
    "Tavily + BeautifulSoup + Groq + LangChain"
)

st.divider()


# ============================================================
# INPUT
# ============================================================

with st.form("research_form"):

    topic = st.text_input(
        "Research topic",
        placeholder=(
            "e.g. What are the latest applications "
            "of Generative AI in healthcare in 2026?"
        )
    )

    submitted = st.form_submit_button(
        "🚀 Run Research",
        use_container_width=True
    )


# ============================================================
# RUN PIPELINE
# ============================================================

if submitted:

    if not topic.strip():

        st.warning(
            "Please enter a research topic."
        )

    else:

        try:

            with st.status(
                "Running multi-agent research pipeline...",
                expanded=True
            ) as status:

                def update_status(message):
                    status.write(message)

                result = run_research_pipeline(
                    topic.strip(),
                    progress_callback=update_status
                )

                status.update(
                    label="🎉 Research pipeline completed!",
                    state="complete",
                    expanded=False
                )

            # =================================================
            # STEP 1 — SEARCH RESULTS
            # =================================================

            st.divider()

            st.header("🔎 Step 1 — Search Results")

            st.caption(
                "Tavily searched the web and returned "
                "verified sources."
            )

            sources = result.get(
                "sources",
                []
            )

            if sources:

                for index, source in enumerate(
                    sources,
                    start=1
                ):

                    with st.container(
                        border=True
                    ):

                        st.subheader(
                            f"{index}. {source['title']}"
                        )

                        st.markdown(
                            f"**URL:** "
                            f"[{source['url']}]"
                            f"({source['url']})"
                        )

                        if source.get("snippet"):

                            st.write(
                                source["snippet"]
                            )

            else:

                st.warning(
                    "No valid sources were found."
                )

            # =================================================
            # STEP 2 — READER
            # =================================================

            st.divider()

            st.header(
                "🌐 Step 2 — Reader Agent"
            )

            st.caption(
                "The Reader Agent reads verified webpages "
                "and extracts evidence."
            )

            reader_summaries = result.get(
                "reader_summaries",
                []
            )

            if reader_summaries:

                for index, item in enumerate(
                    reader_summaries,
                    start=1
                ):

                    with st.expander(
                        f"{index}. {item['title']}",
                        expanded=index == 1
                    ):

                        st.markdown(
                            f"**Source URL:** "
                            f"[{item['url']}]"
                            f"({item['url']})"
                        )

                        st.markdown(
                            item["summary"]
                        )

            else:

                st.warning(
                    "No Reader Agent summaries were generated."
                )

            # =================================================
            # SCRAPED CONTENT
            # =================================================

            st.divider()

            st.header(
                "📖 Scraped Web Content"
            )

            scraped_sources = result.get(
                "scraped_sources",
                []
            )

            for index, item in enumerate(
                scraped_sources,
                start=1
            ):

                with st.expander(
                    f"{index}. {item['title']}"
                ):

                    st.markdown(
                        f"**URL:** "
                        f"[{item['url']}]"
                        f"({item['url']})"
                    )

                    st.text(
                        item["content"]
                    )

            # =================================================
            # STEP 3 — REPORT
            # =================================================

            st.divider()

            st.header(
                "✍️ Step 3 — Research Report"
            )

            report = result.get(
                "report",
                ""
            )

            if report:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        report
                    )

                st.download_button(
                    label="⬇️ Download Research Report",
                    data=report,
                    file_name="research_report.md",
                    mime="text/markdown"
                )

            else:

                st.warning(
                    "No research report was generated."
                )

            # =================================================
            # STEP 4 — CRITIC
            # =================================================

            st.divider()

            st.header(
                "🧐 Step 4 — Critic Feedback"
            )

            st.caption(
                "The Critic Agent evaluates the factual "
                "quality and evidence of the report."
            )

            critic = result.get(
                "critic",
                ""
            )

            if critic:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        critic
                    )

            else:

                st.warning(
                    "No critic feedback was generated."
                )

        except Exception as e:

            st.error(
                "The research pipeline encountered an error."
            )

            st.exception(e)