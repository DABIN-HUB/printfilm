"""LLM 分镜过少（长正文/多场只 1 镜）应判定不足并回退。"""

from app.services.drama.fragment_plan import llm_fragment_coverage_insufficient


def test_single_draft_ok_for_short_one_scene():
    body = "### 场1-1\n日内 厨房\n出场人物：甲\n甲推门进来。"
    drafts = [{"content": "@duration:8\n画面", "duration_sec": 8}]
    assert llm_fragment_coverage_insufficient(body, drafts) is False


def test_single_draft_insufficient_for_multi_scene():
    body = "\n".join(
        [
            "### 场2-1",
            "日内 厨房",
            "出场人物：甲、乙",
            "甲与乙对峙。",
            "### 场2-2",
            "夜外 巷口",
            "出场人物：甲",
            "甲独自离开。",
        ]
    )
    drafts = [{"content": "@duration:15\n开幕", "duration_sec": 15}]
    assert llm_fragment_coverage_insufficient(body, drafts) is True


def test_single_draft_insufficient_for_long_body():
    body = "旁白：" + ("这是很长的剧情叙述用于累计字数。" * 40)
    drafts = [{"content": "@duration:15\n一镜", "duration_sec": 15}]
    assert llm_fragment_coverage_insufficient(body, drafts) is True


def test_two_drafts_cover_two_scenes():
    body = "### 场1-1\n日内 A\n甲进。\n### 场1-2\n夜外 B\n乙走。"
    drafts = [
        {"content": "@duration:10\na", "duration_sec": 10},
        {"content": "@duration:10\nb", "duration_sec": 10},
    ]
    assert llm_fragment_coverage_insufficient(body, drafts) is False


def test_two_drafts_insufficient_for_three_scenes():
    body = "\n".join(
        [
            "### 场3-1",
            "日内 A",
            "出场人物：甲",
            "甲进门。",
            "### 场3-2",
            "夜外 B",
            "出场人物：乙",
            "乙离开。",
            "### 场3-3",
            "日外 C",
            "出场人物：甲、乙",
            "两人重逢。",
        ]
    )
    drafts = [
        {"content": "@duration:10\na", "duration_sec": 10},
        {"content": "@duration:10\nb", "duration_sec": 10},
    ]
    assert llm_fragment_coverage_insufficient(body, drafts) is True


def test_many_drafts_never_capped_as_insufficient():
    """镜数多不算不足；不设上限。"""
    body = "### 场1-1\n日内 A\n### 场1-2\n夜外 B\n" + ("旁白。" * 80)
    drafts = [{"content": f"@duration:8\n镜{i}", "duration_sec": 8} for i in range(12)]
    assert llm_fragment_coverage_insufficient(body, drafts) is False
