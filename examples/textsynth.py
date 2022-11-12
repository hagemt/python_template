"""try out some patterns for async HTTP requests

using aiohttp/etc. from PyPi and TextSynth API
"""
import asyncio
import re
import sys
import time
import warnings

import aiohttp
import pydantic
import typed_dotenv
import typer


class TorTimer(pydantic.BaseModel):
    """for capturing stats before/after a single HTTP round-trip

    e.g. TorTimer(now=..., req=url).elapsed => small number (in ns)
    """

    now: int
    req: str

    @property
    def elapsed(self) -> int:
        now = time.perf_counter_ns()
        return now - self.now

    @property
    def url(self) -> str:
        self.now = time.perf_counter_ns()
        return self.req


class Config(pydantic.BaseModel):
    """for applications using TextSynth, etc.

    (compatible with aiohttp or requests module)
    """

    # https://textsynth.com/settings.html
    TEXTSYNTH_KEY: str  # put yours in .env
    TEXTSYNTH_DEFAULT_ENGINE_NAME: str = "gptj_6B"
    TEXTSYNTH_BASE_URL: str = "https://api.textsynth.com"
    # https://textsynth.com/documentation.html

    def req_session(self):
        # if using requests, return requests
        return aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.TEXTSYNTH_KEY}",
            }
        )

    def res_post_timer(self, res, timer: TorTimer) -> str:
        elapsed = timer.elapsed / 1e9  # conversion from ns to seconds
        return f"POST {timer.url} -> {res.status} ({elapsed:.3f}s elapsed)"

    def timer(self, cmd: str) -> TorTimer:
        engine_name = self.TEXTSYNTH_DEFAULT_ENGINE_NAME
        url = f"{self.TEXTSYNTH_BASE_URL}/v1/engines/{engine_name}/{cmd}"
        return TorTimer(now=0, req=url)


async def auth(cfg: Config) -> int:
    async with cfg.req_session() as api:
        async with api.get(f"{cfg.TEXTSYNTH_BASE_URL}/v1/credits") as res:
            data = await res.json()
            num = data.get("credits", 0)
            print(f"Got TextSynth credits: in USD ~ {num/1e9:12.6f}")
            return num


async def post(cfg: Config, txt: str, cmd="tokenize", **kwargs) -> dict:
    """the default command=tokenize consumes zero credits, other commands:

    Commands:
    - completions: obtain a single response to text provided (English)
    - translate: requires a target_lang (default: en, for English)
    TextSynth also provides some "logprob" APIs for more-advanced usage.

    Each command will expend a certain number of credits, which varies.
    """
    async with cfg.req_session() as api:
        if cmd == "completions":
            body = dict(**kwargs)
            body.update(prompt=txt)
        elif cmd == "tokenize":
            body = dict(text=txt)
        elif cmd == "translate":
            body = dict(source_lang="auto", target_lang="en")
            body.update(**kwargs)
            body.update(text=txt)
        else:
            body = {}

        timer = cfg.timer(cmd)
        async with api.post(timer.url, json=body) as res:
            summary = cfg.res_post_timer(res, timer)
            print("--- You wrote:")
            print(txt)
            print("---", summary)
            try:
                if res.status != 200:
                    print(await res.text())
                    raise ValueError("Bad Request?")
                data = await res.json()
            except ValueError as err:
                print(f"Got TextSynth {cmd}:", err)
                data = {}

            if cmd == "completions":
                print(data.get("text", ""))
            elif cmd == "tokenize":
                munge(cmd, body, data)
            elif cmd == "translate":
                for translation in data.get("translations", []):
                    lang = translation.get("detected_source_lang", "N/A")
                    text = translation.get("text", "")
                    print(f"{lang} -> {body.get('target_lang', 'en')}: {text}")
            else:
                print("--- JSON:")
                print(data)
            return data


def split(text: str) -> list[str]:
    return [t for t in re.findall(r"\w+|\W+", text) if t.strip()]


def munge(_cmd: str, body: dict, data: dict) -> None:
    parsed = split(body.get("text", ""))
    tokens: list[int] = data.get("tokens", [])
    for token, raw in zip(tokens, parsed):
        print(f"{token:>10d}: {raw}")


def main():
    cfg = typed_dotenv.load_into(Config, filename=".env")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        text = sys.stdin.read().strip() or "Hello, World!"
        # print("input:", split(text))
        asyncio.run(auth(cfg))
        with warnings.catch_warnings(record=True) as group:
            asyncio.run(post(cfg, text))
            # NOTE: each call below may cost money!
            # asyncio.run(post(cfg, text, cmd="completions"))

            # setattr(cfg, "TEXTSYNTH_DEFAULT_ENGINE_NAME", "m2m100_1_2B")
            # asyncio.run(post(cfg, text, cmd="translate", target_lang="es"))
            # ^ translate input into Spanish
            for warning in group:
                print("--- WARNING:", warning.message)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    typer.run(main)
