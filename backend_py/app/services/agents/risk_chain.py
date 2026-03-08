import json
from app.core.providers import get_llm_provider
from app.prompts.templates import RISK_CHAIN_PROMPT
from app.schemas.agents import RiskChainSchema, RiskChainNode


class RiskChainService:
    def __init__(self):
        self.llm = get_llm_provider()

    async def generate(self, title: str, summary: str | None) -> dict:
        prompt = RISK_CHAIN_PROMPT.format(title=title, summary=summary or "")
        try:
            content = await self.llm.chat([{"role": "user", "content": prompt}])
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()
            data = json.loads(content)
            first = [RiskChainNode(**n) for n in data.get("first_order", [])]
            second = [RiskChainNode(**n) for n in data.get("second_order", [])]
            third = [RiskChainNode(**n) for n in data.get("third_order", [])]
            return {
                "first_order": [n.model_dump() for n in first],
                "second_order": [n.model_dump() for n in second],
                "third_order": [n.model_dump() for n in third],
            }
        except Exception:
            return {
                "first_order": [{"implication": title, "asset_class": "Rates"}],
                "second_order": [{"implication": "Repricing of front-end rates and FX", "asset_class": "FX"}],
                "third_order": [{"implication": "EM and risk assets under pressure", "asset_class": "EM"}],
            }
