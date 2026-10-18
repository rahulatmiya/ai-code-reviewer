
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def print_result(title, result):
    print(f"\n--- {title} ---")

    if result.content:
        for item in result.content:
            if hasattr(item, "text"):
                print(item.text)
            else:
                print(item)

    if result.is_error:
        print(f"ERROR: {title} failed.")

    return not result.is_error


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server/server.py"],
    )

    try:
        async with stdio_client(server_params) as (
            read_stream,
            write_stream,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                # Initialize MCP connection.
                await session.initialize()

                # Step 1: Verify all four tools are registered.
                tools = await session.list_tools()

                print("\nAvailable MCP tools:")
                tool_names = []

                for tool in tools.tools:
                    tool_names.append(tool.name)
                    print(f"- {tool.name}: {tool.description}")

                expected_tools = [
                    "get_pull_request_details",
                    "get_pull_request_diff",
                    "analyze_pull_request_diff",
                    "ai_review_pull_request",
                ]

                missing_tools = [
                    name for name in expected_tools
                    if name not in tool_names
                ]

                if missing_tools:
                    print("\nERROR: Missing MCP tools:")
                    for name in missing_tools:
                        print(f"- {name}")
                    return

                print("\nSUCCESS: All four tools are registered.")

                # Step 2: Retrieve pull request details.
                details = await session.call_tool(
                    "get_pull_request_details",
                    arguments={"pr_number": 1},
                )

                if not await print_result(
                    "Pull Request Details",
                    details,
                ):
                    return

                # Step 3: Retrieve the pull request diff.
                diff = await session.call_tool(
                    "get_pull_request_diff",
                    arguments={"pr_number": 1},
                )

                if not await print_result(
                    "Pull Request Diff",
                    diff,
                ):
                    return

                # Step 4: Run basic rule-based checks.
                analysis = await session.call_tool(
                    "analyze_pull_request_diff",
                    arguments={"pr_number": 1},
                )

                if not await print_result(
                    "Basic Review Findings",
                    analysis,
                ):
                    return

                # Step 5: Run AI-powered code review.
                print(
                    "\nCalling OpenAI for AI-powered review. "
                    "This may incur API charges."
                )

                ai_review = await session.call_tool(
                    "ai_review_pull_request",
                    arguments={"pr_number": 1},
                )

                if not await print_result(
                    "AI-Powered Review",
                    ai_review,
                ):
                    return

                print("\nSUCCESS: All MCP tool tests completed.")

    except Exception as exc:
        print(f"\nERROR: {type(exc).__name__}: {exc}")
        print(
            "\nCheck the traceback and confirm you're running "
            "from C:\\ai-code-reviewer."
        )


if __name__ == "__main__":
    asyncio.run(main())
