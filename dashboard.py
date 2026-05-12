#!/usr/bin/env python3
import anthropic
import streamlit as st

SYSTEM_PROMPT = """You are an expert QA engineer and test case designer. Your job is to analyze software requirements and generate comprehensive manual test cases that provide thorough coverage.

For each set of requirements you receive, generate test cases that cover:
1. Happy path scenarios - the primary intended functionality works correctly
2. Edge cases - boundary values, empty inputs, maximum/minimum values
3. Negative test cases - invalid inputs, error conditions, unauthorized access
4. Boundary conditions - values at the limits of acceptable ranges
5. Integration scenarios - how components interact with each other when relevant

Each test case must include:
- Test Case ID: unique identifier (TC-001, TC-002, ...)
- Title: brief descriptive name
- Priority: High / Medium / Low
- Type: Positive / Negative / Boundary / Edge Case
- Preconditions: what must be true before the test runs
- Test Steps: numbered, clear action steps
- Expected Result: observable outcome when steps are executed correctly

Be thorough but practical - focus on what a QA tester would realistically execute manually."""

MARKDOWN_FORMAT_PROMPT = """Output the test cases as a Markdown table with these exact columns:
| Test Case ID | Title | Priority | Type | Preconditions | Test Steps | Expected Result |
Rules:
- In the Test Steps column, separate steps with semicolons: 1. Do X; 2. Do Y
- Keep cell content concise - avoid newlines inside cells
- After the table, add a ## Coverage Summary section"""

CSV_FORMAT_PROMPT = """Output the test cases in CSV format with this exact header:
Test Case ID,Title,Priority,Type,Preconditions,Test Steps,Expected Result
Rules:
- Wrap every field in double quotes
- Separate steps with semicolons in the Test Steps field
- After the CSV, add a coverage summary as comment lines starting with #"""

def generate_test_cases(requirements, output_format):
    client = anthropic.Anthropic()
    format_prompt = MARKDOWN_FORMAT_PROMPT if output_format == "markdown" else CSV_FORMAT_PROMPT
    user_message = f"Generate comprehensive test cases for the following requirements:\n\n---\n{requirements}\n---\n\n{format_prompt}"
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        result_text = ""
        placeholder = st.empty()
        for text in stream.text_stream:
            result_text += text
            placeholder.markdown(result_text + "...")
        placeholder.empty()
        final = stream.get_final_message()
    usage = final.usage
    cached = getattr(usage, "cache_read_input_tokens", 0) or 0
    return result_text, {"input": usage.input_tokens, "cached": cached, "output": usage.output_tokens}

st.set_page_config(page_title="Test Case Generator", page_icon="TC", layout="wide")
st.title("Test Case Generator")
st.caption("Generate manual test cases from software requirements using Claude AI.")

with st.sidebar:
    st.header("Settings")
    output_format = st.radio("Output format", ["markdown", "csv"], format_func=str.upper)
    st.divider()
    st.header("Load example")
    if st.button("User Authentication"):
        with open("examples/user_authentication.md", "r") as f:
            st.session_state["requirements"] = f.read()
    if st.button("Shopping Cart"):
        with open("examples/shopping_cart.md", "r") as f:
            st.session_state["requirements"] = f.read()
    st.divider()
    uploaded = st.file_uploader("Or upload a .md / .txt file", type=["md", "txt"])
    if uploaded:
        st.session_state["requirements"] = uploaded.read().decode("utf-8")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Requirements")
    requirements = st.text_area(
        label="Requirements",
        value=st.session_state.get("requirements", ""),
        height=400,
        placeholder="Paste your requirements here...",
        label_visibility="collapsed",
    )
    st.caption(f"{len(requirements.splitlines()) if requirements.strip() else 0} lines")
    generate = st.button("Generate Test Cases", type="primary", disabled=not requirements.strip())

with col2:
    st.subheader("Generated Test Cases")
    if generate and requirements.strip():
        with st.spinner("Calling Claude AI..."):
            try:
                result, usage = generate_test_cases(requirements.strip(), output_format)
                st.session_state["result"] = result
                st.session_state["usage"] = usage
                st.session_state["result_format"] = output_format
            except Exception as e:
                st.error(f"Error: {e}")
    if "result" in st.session_state:
        result = st.session_state["result"]
        usage = st.session_state["usage"]
        fmt = st.session_state.get("result_format", "markdown")
        m1, m2, m3 = st.columns(3)
        m1.metric("Input tokens", f"{usage['input']:,}")
        m2.metric("Cached tokens", f"{usage['cached']:,}")
        m3.metric("Output tokens", f"{usage['output']:,}")
        st.divider()
        if fmt == "markdown":
            st.markdown(result)
        else:
            st.code(result, language="text")
        ext = "md" if fmt == "markdown" else "csv"
        st.download_button(f"Download .{ext}", data=result, file_name=f"test_cases.{ext}", mime="text/plain")
