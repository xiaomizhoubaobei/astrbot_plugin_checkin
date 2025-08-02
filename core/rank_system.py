from typing import List, Tuple, Dict, Any

class RankSystem:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_rank(self, ctx_id: str, key: str) -> List[Tuple[str, Dict[str, Any]]]:
        """获取当前上下文的排行榜"""
        ctx_data = self.data_manager.get_context_data(ctx_id)
        return sorted(
            ctx_data.items(),
            key=lambda x: x[1][key],
            reverse=True
        )[:10]

    def get_today_rank(self, ctx_id: str, today: str) -> List[Tuple[str, Dict[str, Any]]]:
        """获取今日签到排行榜"""
        ctx_data = self.data_manager.get_context_data(ctx_id)
        return sorted(
            [(uid, data) for uid, data in ctx_data.items()
             if data["last_checkin"] == today],
            key=lambda x: x[1]["continuous_days"],
            reverse=True
        )[:10]

    @staticmethod
    def format_rank(ranked: List[Tuple[str, Dict[str, Any]]], title: str, key: str) -> str:
        """格式化排行榜输出"""
        msg = [f"🏆 {title}"] + [
            f"{i + 1}. {data.get('username', '未知')} - {data[key]}"
            for i, (uid, data) in enumerate(ranked)
        ]
        return "\n".join(msg)