import re

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.message import Message


class SourceAnswerComponent(Component):
    display_name = "Answer + Retrieved Sources"
    description = "Preserve the model answer and append filenames from actual retrieved context, not invented citations."
    icon = "file-text"
    name = "SourceAnswer"

    inputs = [
        MessageTextInput(name="answer", display_name="Model Answer"),
        MessageTextInput(name="context", display_name="Retrieved Context"),
    ]
    outputs = [Output(display_name="Answer with Sources", name="message", method="format_answer")]

    def format_answer(self) -> Message:
        if not str(self.answer).strip():
            raise ValueError("The answer model returned no text.")
        paths = re.findall(r"(?m)^\[source: ([^\r\n]+)\]$", str(self.context))
        if str(self.context).strip() and not paths:
            raise ValueError("Retrieved context is missing the expected source labels.")
        sources = list(dict.fromkeys(path.replace("\\", "/").rsplit("/", 1)[-1] for path in paths))
        if sources:
            references = "\n".join(f"- [source: {name}]" for name in sources)
            footer = f"Retrieved sources (check the evidence; this list does not validate every claim):\n{references}"
        else:
            footer = "No source passages were retrieved. The answer has no retrieved evidence."
        return Message(text=f"{self.answer}\n\n{footer}")
