#!/usr/bin/env python3
"""Test Case Generator — generates manual test cases from requirements using Claude AI."""

import sys
import click
import anthropic

SYSTEM_PROMPT = """You are an expert QA engineer and test case designer. Your job is to analyze software requirements and generate comprehensive manual test cases that provide thorough coverage.

For each set of requirements you receive, generate test cases that cover:
1. Happy path scenarios — the primary intended functionality works correctly
2. Edge cases — boundary values, empty inputs, maximum/minimum values
3. Negative test cases — invalid inputs, error conditions, unauthorized access
4. Boundary conditions — values at the limits of acceptable ranges
5. Integration scenarios — how components interact with each other when relevant

Each test case must include:
- Test Case ID: unique identifier (TC-001, TC-002, ...)
- Title: brief descriptive name
- Priority: High / Medium / Low
- Type: Positive / Negative / Boundary / Edge Case
- Preconditions: what must be true before the test runs
- Test Steps: numbered, clear action steps
- Expected Result: observable outcome when steps are executed correctly

Be thorough but practical — focus on what a QA tester would realistically execute manually."""

MARKDOWN_FORMAT_PROMPT = """Output the test cases as a Markdown table with these exact columns (pipe-separated):

| Test Case ID | Title | Priority | Type | Preconditions | Test Steps | Expected Result |

Rules:
- In the "Test Steps" column, separate steps with semicolons: "1. Do X; 2. Do Y; 3. Observe Z"
- Keep cell content concise — avoid newlines inside cells
- After the table, add a "## Coverage Summary" section with a brief bullet-point breakdown"""

CSV_FORMAT_PROMPT = """Output the test cases in CSV format with this exact header row:

Test Case ID,Title,Priority,Type,Preconditions,Test Steps,Expected Result

Rules:
- Wrap every field in double quotes
- In the "Test Steps" field, separate steps with semicolons: "1. Do X; 2. Do Y; 3. Observe Z"
- Escape any double quotes inside fields by doubling them ("")
- After the CSV block, add a coverage summary as comment lines starting with #"""


def stream_test_cases(requirements: str, output_format: str) -> str:
    """Call Claude API with streaming and return the generated test cases."""
    client = anthropic.Anthropic()

    format_prompt = (
        MARKDOWN_FORMAT_PROMPT if output_format == "markdown" else CSV_FORMAT_PROMPT
    )

    user_message = (
        f"Generate comprehensive test cases for the following requirements:\n\n"
        f"---\n{requirements}\n---\n\n"
        f"{format_prompt}"
    )

    click.echo("Calling Claude AI (streaming)...", err=True)

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        # Print progress dots to stderr while streaming
        for _ in stream.text_stream:
            pass
        final = stream.get_final_message()

    # Report token usage to stderr
    usage = final.usage
    cached = getattr(usage, "cache_read_input_tokens", 0) or 0
    click.echo(
        f"Done. Tokens — input: {usage.input_tokens} | "
        f"cached: {cached} | output: {usage.output_tokens}",
        err=True,
    )

    return next(
        (block.text for block in final.content if block.type == "text"), ""
    )


@click.command()
@click.argument(
    "requirements_file",
    type=click.Path(exists=True, readable=True),
    required=False,
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "csv"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format for the generated test cases.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default=None,
    help="Write output to this file instead of stdout.",
)
@click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read requirements from stdin.",
)
def main(requirements_file: str, output_format: str, output: str, stdin: bool) -> None:
    """Generate manual test cases from software requirements using Claude AI.

    Reads requirements from REQUIREMENTS_FILE (a .txt or .md file),
    or from stdin with the --stdin flag.

    \b
    Examples:
      # Generate Markdown test cases from a file
      python test_case_generator.py examples/user_authentication.md

    \b
      # Generate CSV and save to a file
      python test_case_generator.py requirements.txt --format csv -o test_cases.csv

    \b
      # Pipe requirements directly
      echo "Users can register with email and password" | python test_case_generator.py --stdin
    """
    # --- Read requirements ---
    if stdin:
        if sys.stdin.isatty():
            click.echo(
                "Reading requirements from stdin (press Ctrl+D when done):", err=True
            )
        requirements = sys.stdin.read()
    elif requirements_file:
        with open(requirements_file, "r", encoding="utf-8") as f:
            requirements = f.read()
    else:
        raise click.UsageError(
            "Provide a REQUIREMENTS_FILE argument or use the --stdin flag.\n"
            "Run with --help for usage information."
        )

    requirements = requirements.strip()
    if not requirements:
        raise click.ClickException("Requirements content is empty.")

    click.echo(
        f"Generating {output_format.upper()} test cases from "
        f"{len(requirements.splitlines())} lines of requirements...",
        err=True,
    )

    # --- Generate test cases ---
    result = stream_test_cases(requirements, output_format)

    if not result:
        raise click.ClickException("Claude returned an empty response. Please try again.")

    # --- Write output ---
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        click.echo(f"Test cases written to: {output}", err=True)
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
