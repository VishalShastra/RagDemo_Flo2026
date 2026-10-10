from __future__ import annotations

import json
import re

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, MultilineInput, Output
from lfx.schema.message import Message


class GroundingGateComponent(Component):
    display_name = "Grounding Gate"
    description = (
        "Reads the LLM-as-judge verdict. Releases the answer only if it is supported by the retrieved context, "
        "otherwise returns a safe fallback."
    )
    icon = "shield-check"
    name = "GroundingGate"

    inputs = [
        MessageTextInput(name="answer", display_name="Draft Answer"),
        MessageTextInput(name="verdict", display_name="Judge Verdict", info="JSON from the grounding-check LLM."),
        MultilineInput(
            name="fallback",
            display_name="Fallback Message",
            value=(
                "I could not find a well-supported answer in the onboarding documents. "
                "Please check with the IT Help Desk (#it-helpdesk) or People Ops (#people-ops)."
            ),
        ),
    ]

    outputs = [Output(display_name="Final Answer", name="final_answer", method="gate")]

    @staticmethod
    def _parse(verdict: str) -> tuple[bool, str]:
        match = re.search(r"\{.*\}", verdict, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                grounded = str(parsed.get("grounded", "")).strip().lower() in {"true", "yes", "1"}
                return grounded, str(parsed.get("reason", ""))
            except json.JSONDecodeError:
                pass
        upper = verdict.upper()
        return ("NOT_GROUNDED" not in upper and "GROUNDED" in upper), verdict.strip()

    def gate(self) -> Message:
        grounded, reason = self._parse(str(self.verdict or ""))
        if grounded:
            text = f"{self.answer}\n\n---\nGrounding check: PASSED. {reason}".strip()
        else:
            text = f"{self.fallback}\n\n---\nGrounding check: FAILED. {reason}".strip()
        self.status = text
        return Message(text=text)
