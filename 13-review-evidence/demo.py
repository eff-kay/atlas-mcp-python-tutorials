"""Prepare local evidence; this is NOT a directory submission or an upload-ready plugin."""

import asyncio
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    root = Path(__file__).resolve().parent
    output = root / "output"
    output.mkdir(exist_ok=True)
    scenarios = json.loads((root / "scenarios.json").read_text())
    require(
        sum(not x["expect_error"] for x in scenarios) == 5, "Need five positive cases"
    )
    require(sum(x["expect_error"] for x in scenarios) == 3, "Need three negative cases")
    results = []
    async with stdio(__file__) as client:
        tools = await client.list_tools()
        inventory = [
            t.model_dump(by_alias=True, exclude_none=True) for t in tools.tools
        ]
        for tool in inventory:
            hints = tool["annotations"]
            require(
                all(
                    isinstance(hints.get(k), bool)
                    for k in ["readOnlyHint", "destructiveHint", "openWorldHint"]
                ),
                "Explicit hints required",
            )
        for case in scenarios:
            result = await client.call_tool(case["tool"], case["arguments"])
            require(
                result.is_error == case["expect_error"],
                case["name"] + " did not match expected error behavior",
            )
            actual = show(case["name"], result)
            require(
                case["expected_fragment"] in json.dumps(actual),
                "Unexpected fixture result: " + case["name"],
            )
            results.append(
                {**case, "actual": actual, "observed_error": result.is_error}
            )
    (output / "tool-inventory.json").write_text(json.dumps(inventory, indent=2))
    (output / "review-results.json").write_text(json.dumps(results, indent=2))
    with zipfile.ZipFile(output / "review-evidence.zip", "w") as archive:
        for name in ["tool-inventory.json", "review-results.json"]:
            archive.write(output / name, arcname=name)
    print(
        "Created output/review-evidence.zip — evidence only, not an installable plugin or approval guarantee."
    )


if __name__ == "__main__":
    asyncio.run(main())
