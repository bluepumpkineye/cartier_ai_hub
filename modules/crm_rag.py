import streamlit as st
import pandas as pd
from utils.vector_store import search_vector_store, ensure_index_exists
from utils.llm_client import chat_completion, DEFAULT_MODEL
from utils.guardrails import check_input_guardrails, sanitize_response


def render_crm_rag():
    st.markdown("## 🔍 CRM Intelligence & RAG Assistant")
    st.markdown(
        "*Powered by Retrieval-Augmented Generation — "
        "grounded in Cartier APAC knowledge base*"
    )

    # ── Build index if missing ──
    with st.spinner("Loading knowledge base..."):
        ensure_index_exists()

    col1, col2 = st.columns([1.6, 1])

    with col1:
        st.markdown("### Client Intelligence Query")

        example_queries = [
            "What is the CRM strategy for VIP clients in China?",
            "How should I handle a client interested in High Jewellery who hasn't visited in 6 months?",
            "What are the digital channel targets for Japan in 2024?",
            "Explain the supply chain protocol for High Jewellery stockouts",
            "What is the churn prevention policy for Premium tier clients?",
        ]

        selected = st.selectbox(
            "💡 Example queries",
            ["— Select or type below —"] + example_queries
        )

        query = st.text_area(
            "Ask the Cartier APAC Knowledge Assistant",
            value=selected if selected != "— Select or type below —" else "",
            height=100,
            placeholder="e.g. What is our CRM approach for VIP clients in South Korea?"
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            tone = st.selectbox(
                "Response Tone",
                ["Executive Summary", "Detailed Brief", "Action-Oriented"]
            )
        with col_b:
            market_filter = st.selectbox(
                "Market Context",
                ["All APAC", "China", "Japan", "South Korea",
                 "Singapore", "Australia"]
            )
        with col_c:
            k_results = st.slider("Source Documents", 1, 4, 2)

        if st.button("🔴 Submit Query", type="primary", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a query.")
                return

            # Input guardrail
            is_safe, reason = check_input_guardrails(query)
            if not is_safe:
                st.error(reason)
                return

            with st.spinner("Retrieving context and generating response..."):

                # RAG retrieval
                docs = search_vector_store(query, k=k_results)

                context = "\n\n---\n\n".join([
                    f"**{d['title']}** (Category: {d['category']})\n{d['content']}"
                    for d in docs
                ])

                tone_instruction = {
                    "Executive Summary":  "Respond in 3-4 concise bullet points suitable for a senior executive.",
                    "Detailed Brief":     "Provide a comprehensive response with context and rationale.",
                    "Action-Oriented":    "Respond with clear numbered action steps a boutique manager can follow.",
                }[tone]

                system_prompt = (
                    "You are the Cartier APAC AI Intelligence Assistant — an expert "
                    "internal advisor for Cartier's Asia-Pacific business operations. "
                    "You embody Cartier's values of excellence, heritage, and client-centricity. "
                    "Respond only based on the provided context. "
                    "If information is not in the context, state that clearly rather than speculating. "
                    f"Market context: {market_filter}. "
                    f"Tone instruction: {tone_instruction} "
                    "Always maintain a professional, sophisticated tone befitting the Maison."
                )

                active_model = st.session_state.get("active_model", DEFAULT_MODEL)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ]

                response = chat_completion(
                    messages,
                    model=active_model,
                    temperature=0.2,
                    max_tokens=800
                )
                response = sanitize_response(response)

            # ── Display response ──
            st.markdown("---")
            st.markdown("### ✨ AI Response")
            st.markdown(response)

            # ── Source documents ──
            if docs:
                st.markdown("---")
                st.markdown("**📚 Source Documents Retrieved:**")
                for i, doc in enumerate(docs, 1):
                    with st.expander(
                        f"{i}. {doc['title']} — "
                        f"Relevance: {doc['relevance_score']:.2%}"
                    ):
                        st.markdown(f"**Category:** {doc['category']}")
                        st.markdown(doc["content"][:400] + "...")

            # ── Guardrail badge ──
            st.success(
                "✅ Guardrails: Input validated · "
                "Output sanitised · Source-grounded"
            )

    # ── Right column: CRM stats ──
    with col2:
        st.markdown("### CRM Quick Stats")
        try:
            df = pd.read_csv("data/crm_data.csv")

            total      = len(df)
            vip        = len(df[df["segment"] == "VIP (>$50K)"])
            high_churn = len(df[df["churn_risk"] == "High"])
            avg_clv    = df["lifetime_value_usd"].mean()

            st.metric("Total APAC Clients", f"{total:,}")
            st.metric(
                "VIP Clients",
                f"{vip:,}",
                delta=f"{vip/total:.1%} of base"
            )
            st.metric(
                "High Churn Risk",
                f"{high_churn}",
                delta=f"-{high_churn} need attention",
                delta_color="inverse"
            )
            st.metric("Avg Lifetime Value", f"${avg_clv:,.0f}")

            st.markdown("---")
            st.markdown("**Churn Risk Distribution**")
            churn_counts = df["churn_risk"].value_counts()
            st.bar_chart(churn_counts)

            st.markdown("**Top Markets by Client Count**")
            market_counts = df["market"].value_counts().head(5)
            st.bar_chart(market_counts)

        except FileNotFoundError:
            st.info("Run data generator to populate CRM stats.")