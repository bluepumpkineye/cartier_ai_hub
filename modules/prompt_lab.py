import streamlit as st
from utils.llm_client import chat_completion
from utils.guardrails import check_input_guardrails, check_output_guardrails, sanitize_response
from utils.llm_client import chat_completion, DEFAULT_MODEL

PROMPT_TEMPLATES = {
    "Client Re-engagement": {
        "system": "You are a Cartier Personal Stylist. Write an elegant, personalised re-engagement message for a client who hasn't visited in {days_inactive} days. Reference their preferred category: {preferred_category}. Market: {market}. Tone: warm, exclusive, not pushy. Max 120 words.",
        "variables": ["days_inactive", "preferred_category", "market"]
    },
    "Product Recommendation": {
        "system": "You are a Cartier product advisor. Recommend 2-3 pieces from our {category} collection for a client celebrating {occasion}, budget {budget_range}. Market: {market}. Be specific with product names and craft a compelling narrative.",
        "variables": ["category", "occasion", "budget_range", "market"]
    },
    "VIP Event Invitation": {
        "system": "Draft an exclusive VIP event invitation for a {segment} client in {market} for our upcoming {event_type}. Convey rarity, prestige, and personal connection. Keep under 150 words.",
        "variables": ["segment", "market", "event_type"]
    },
    "Sales Performance Commentary": {
        "system": "You are the Cartier APAC Head of Sales. Write a brief executive commentary on {market} performance for {period}: Revenue {revenue}, vs target {target}, key driver {driver}. Professional, data-led, 80 words max.",
        "variables": ["market", "period", "revenue", "target", "driver"]
    }
}

def render_prompt_lab():
    st.markdown("## 🧪 GenAI Prompt Laboratory")
    st.caption("Prompt engineering, evaluation, guardrails testing, and reusable prompt library")

    tab1, tab2 = st.tabs(["📝 Prompt Builder", "📊 Prompt Evaluation"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Prompt Template Library")
            template_name = st.selectbox("Select Template", list(PROMPT_TEMPLATES.keys()))
            template = PROMPT_TEMPLATES[template_name]
            
            st.markdown("**Template Variables:**")
            variable_values = {}
            for var in template["variables"]:
                variable_values[var] = st.text_input(
                    f"{var.replace('_', ' ').title()}",
                    value=get_default(var)
                )
            
            system_prompt_preview = template["system"]
            for var, val in variable_values.items():
                system_prompt_preview = system_prompt_preview.replace(f"{{{var}}}", val or f"[{var}]")
            
            st.markdown("**📋 System Prompt Preview:**")
            st.text_area("Compiled Prompt", system_prompt_preview, height=160, disabled=True)
            
            user_message = st.text_area(
                "User Message (Optional Override)",
                placeholder="Leave blank to use system prompt as primary instruction...",
                height=80
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                temperature  = st.slider("Temperature", 0.0, 1.0, 0.4, step=0.1)
            with col_b:
                max_tokens   = st.select_slider("Max Tokens", [256, 512, 768, 1024], value=512)
        
        with col2:
            st.markdown("#### Output")
            
            if st.button("🔴 Generate", type="primary", use_container_width=True):
                final_user_msg = user_message or "Please execute the above instructions."
                
                # Input guardrail
                is_safe, reason = check_input_guardrails(system_prompt_preview + " " + final_user_msg)
                if not is_safe:
                    st.error(reason)
                else:
                    with st.spinner("Generating..."):
                        messages = [
                            {"role": "system",  "content": system_prompt_preview},
                            {"role": "user",    "content": final_user_msg}
                        ]
                        response = chat_completion(messages, temperature=temperature, max_tokens=max_tokens)
                    
                    # Output guardrail
                    output_safe, output_result = check_output_guardrails(response)
                    clean_response = sanitize_response(response)
                    
                    st.markdown("**Generated Output:**")
                    st.markdown(
                        f'<div style="background:#1A1A1A;border:1px solid #C5A028;'
                        f'border-radius:8px;padding:16px;color:#E8E0D0;font-size:14px;'
                        f'line-height:1.7;">{clean_response}</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Guardrail status
                    st.markdown("---")
                    gcol1, gcol2, gcol3 = st.columns(3)
                    gcol1.success("✅ Input: Safe")
                    if output_safe:
                        gcol2.success("✅ Output: Brand-safe")
                    else:
                        gcol2.warning(f"⚠️ {output_result}")
                    gcol3.success("✅ PII: Sanitised")
                    
                    # Token estimate
                    token_est = len((system_prompt_preview + clean_response).split()) * 1.3
                    st.caption(f"Estimated tokens: ~{int(token_est)} | Est. cost: ~${token_est*0.000015:.4f}")

    with tab2:
        st.markdown("#### Prompt Evaluation Framework")
        st.caption("Evaluate prompt quality across key dimensions")
        
        eval_prompt = st.text_area("Prompt to Evaluate", height=100,
                                   placeholder="Paste a prompt or output to evaluate...")
        
        criteria = {
            "Brand Alignment":    "Does the content align with Cartier's values of luxury, heritage, and exclusivity?",
            "Clarity":            "Is the output clear and professionally written?",
            "Specificity":        "Does the output include specific, actionable details?",
            "Client-Centricity":  "Does it prioritise the client relationship and experience?",
            "Guardrail Safety":   "Is the content free from brand-unsafe, offensive, or restricted content?"
        }
        
        if st.button("Run Evaluation", type="primary") and eval_prompt:
            with st.spinner("Running multi-criteria evaluation..."):
                eval_results = {}
                for criterion, description in criteria.items():
                    eval_msg = [
                        {"role": "system", "content":
                         f"You are an expert evaluator for Cartier brand communications. "
                         f"Score the following content on '{criterion}': {description} "
                         f"Score from 1-10 and provide a one-sentence justification. "
                         f"Format: Score: X/10 | Justification: [text]"},
                        {"role": "user", "content": eval_prompt}
                    ]
                    result = chat_completion(eval_msg, temperature=0.1, max_tokens=100)
                    eval_results[criterion] = result
            
            st.markdown("**Evaluation Results:**")
            for criterion, result in eval_results.items():
                with st.expander(f"**{criterion}** — {result[:40]}..."):
                    st.write(result)

def get_default(var: str) -> str:
    defaults = {
        "days_inactive":       "180",
        "preferred_category":  "Watches",
        "market":              "Singapore",
        "category":            "High Jewellery",
        "occasion":            "10th anniversary",
        "budget_range":        "$15,000 - $30,000",
        "segment":             "VIP",
        "event_type":          "High Jewellery Private Preview",
        "period":              "Q2 2024",
        "revenue":             "$18.4M",
        "target":              "$17.0M",
        "driver":              "Watches category growth"
    }
    return defaults.get(var, "")