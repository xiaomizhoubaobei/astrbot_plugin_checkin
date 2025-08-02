import datetime
import hashlib
import json
import logging
import os
import random

from astrbot.api.all import *
from astrbot.api.event.filter import command, event_message_type, EventMessageType

from messages import get_random_message

logger = logging.getLogger("pluginCheckIn")

# 数据存储路径
DATA_DIR = os.path.join("data", "plugins", "astrbot_plugin_checkin")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "checkin_data.json")


def _load_data() -> dict:
    """加载签到数据"""
    try:
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}")
        return {}


def _save_data(data: dict):
    """保存签到数据"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"数据保存失败: {str(e)}")


def _get_context_id(event: AstrMessageEvent) -> str:
    """多平台兼容的上下文ID生成（已修复QQ官方Webhook问题）"""
    try:
        # 优先处理QQ官方Webhook结构
        if hasattr(event, 'message') and hasattr(event.message, 'source'):
            source = event.message.source
            if hasattr(source, 'group_id') and source.group_id:
                return f"group_{source.group_id}"
            if hasattr(source, 'user_id') and source.user_id:
                return f"private_{source.user_id}"

        # 处理标准事件结构
        if hasattr(event, 'group_id') and event.group_id:
            return f"group_{event.group_id}"
        if hasattr(event, 'user_id') and event.user_id:
            return f"private_{event.user_id}"

        # 生成唯一备用ID
        event_str = f"{event.get_message_id()}-{event.get_time()}"
        return f"ctx_{hashlib.md5(event_str.encode()).hexdigest()[:6]}"

    except Exception as e:
        logger.error(f"上下文ID生成异常: {str(e)}")
        return "default_ctx"


def _generate_rewards() -> int:
    """生成100-300之间的整十位随机星之碎片/积分"""
    # 生成10-30之间的随机数，然后乘以10，确保结果是10的倍数
    return random.randint(10, 30) * 10


@register("签到插件", "祁筱欣", "一个签到插件", "1.0.0",
          "https://github.com/Meguminlove/astrbot_checkin_plugin")
class CheckInPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data = _load_data()

    @command("琼哗台签到", alias=["琼哗台打卡"])
    async def check_in(self, event: AstrMessageEvent):
        """每日签到"""
        try:
            ctx_id = _get_context_id(event)
            user_id = event.get_sender_id()
            today = datetime.date.today().isoformat()

            # 初始化数据结构（新增username字段）
            ctx_data = self.data.setdefault(ctx_id, {})
            user_data = ctx_data.setdefault(user_id, {
                "username": event.get_sender_name(),  # 确保存储的是用户昵称
                "total_days": 0,
                "continuous_days": 0,
                "month_days": 0,
                "total_rewards": 0,
                "month_rewards": 0,
                "last_checkin": None
            })

            # 更新用户名（防止用户改名）
            user_data['username'] = event.get_sender_name()

            # 检查重复签到
            if user_data["last_checkin"] == today:
                yield event.plain_result("⚠️ 今日已完成打卡/签到并签订契约，请勿重复操作")
                return

            # 计算连续签到
            last_date = user_data["last_checkin"]
            current_month = today[:7]

            if last_date:
                last_day = datetime.date.fromisoformat(last_date)
                if (datetime.date.today() - last_day).days == 1:
                    user_data["continuous_days"] += 1
                else:
                    user_data["continuous_days"] = 1

                # 跨月重置月数据
                if last_date[:7] != current_month:
                    user_data["month_days"] = 0
                    user_data["month_rewards"] = 0
            else:
                user_data["continuous_days"] = 1

            # 生成奖励
            rewards = _generate_rewards()
            user_data.update({
                "total_days": user_data["total_days"] + 1,
                "month_days": user_data["month_days"] + 1,
                "total_rewards": user_data["total_rewards"] + rewards,
                "month_rewards": user_data["month_rewards"] + rewards,
                "last_checkin": today
            })

            _save_data(self.data)

            # 构造响应
            selected_msg = get_random_message()
            yield event.plain_result(
                f"✨【契约成立】\n"
                f"🎉 {event.get_sender_name()}，感谢您的签到！\n"
                f"📅 今日日期: {today}\n"
                f"👤 用户名: {user_data['username']}\n"
                f"📈 累计签到天数: {user_data['total_days']}\n"
                f"\n📆 本月签到天数: {user_data['month_days']}\n"
                f"💎 累计获得星之碎片/积分: {user_data['total_rewards']}\n"
                f"🌟 本月获得星之碎片/积分: {user_data['month_rewards']}\n"
                f"📅 连续签订契约: {user_data['continuous_days']}天\n"
                f"🎁 获得星之碎片/积分: {rewards}个\n"
                f"💬 契约签订寄语: {selected_msg}"
            )

        except Exception as e:
            logger.error(f"签到处理异常: {str(e)}", exc_info=True)
            yield event.plain_result("🔧 签到and契约服务暂时不可用，请联系管理员/群主")

    def _get_rank(self, event: AstrMessageEvent, key: str) -> list:
        """获取当前上下文的排行榜"""
        ctx_id = _get_context_id(event)
        ctx_data = self.data.get(ctx_id, {})
        return sorted(
            ctx_data.items(),
            key=lambda x: x[1][key],
            reverse=True
        )[:10]

    @command("琼哗台签到排行榜", alias=["琼哗台签到排行"])
    async def show_rank_menu(self, event: AstrMessageEvent):
        """排行榜导航菜单"""
        yield event.plain_result(
            "📊 排行榜类型：\n"
            "/签到总奖励排行榜 - 累计获得星之碎片/积分\n"
            "/签到月奖励排行榜 - 本月获得星之碎片/积分\n"
            "/签到总天数排行榜 - 历史签到总天数\n"
            "/签到月天数排行榜 - 本月签到天数\n"
            "/签到今日排行榜 - 今日签到用户榜"
        )

    @command("琼哗台签到总奖励排行榜", alias=["琼哗台签到总排行"])
    async def total_rewards_rank(self, event: AstrMessageEvent):
        """总奖励排行榜"""
        ranked = self._get_rank(event, "total_rewards")
        msg = ["🏆 累计星之碎片/积分排行榜"] + [
            f"{i + 1}.签到者/契约者 {data.get('username', '未知')} - {data['total_rewards']}个"
            for i, (uid, data) in enumerate(ranked)
        ]
        yield event.plain_result("\n".join(msg))

    @command("琼哗台签到月奖励排行榜", alias=["琼哗台签到月排行"])
    async def month_rewards_rank(self, event: AstrMessageEvent):
        """月奖励排行榜"""
        ranked = self._get_rank(event, "month_rewards")
        msg = ["🏆 本月星之碎片/积分排行榜"] + [
            f"{i + 1}. 签到者/契约者 {data.get('username', '未知')} - {data['month_rewards']}个"
            for i, (uid, data) in enumerate(ranked)
        ]
        yield event.plain_result("\n".join(msg))

    @command("琼哗台签到总天数排行榜", alias=["琼哗台签到总天数排行"])
    async def total_days_rank(self, event: AstrMessageEvent):
        """总天数排行榜"""
        ranked = self._get_rank(event, "total_days")
        msg = ["🏆 累计契约天数榜"] + [
            f"{i + 1}. 契约者 {data.get('username', '未知')} - {data['total_days']}天"
            for i, (uid, data) in enumerate(ranked)
        ]
        yield event.plain_result("\n".join(msg))

    @command("琼哗台签到月天数排行榜", alias=["琼哗台签到月天数排行"])
    async def month_days_rank(self, event: AstrMessageEvent):
        """月天数排行榜"""
        ranked = self._get_rank(event, "month_days")
        msg = ["🏆 本月契约/签到天数榜"] + [
            f"{i + 1}. 契约/签到者 {data.get('username', '未知')} - {data['month_days']}天"
            for i, (uid, data) in enumerate(ranked)
        ]
        yield event.plain_result("\n".join(msg))

    @command("琼哗台签到今日排行榜", alias=["琼哗台签到今日排行", "琼哗台签到日排行"])
    async def today_rank(self, event: AstrMessageEvent):
        """今日签到榜"""
        ctx_id = _get_context_id(event)
        today = datetime.date.today().isoformat()

        ranked = sorted(
            [(uid, data) for uid, data in self.data.get(ctx_id, {}).items()
             if data["last_checkin"] == today],
            key=lambda x: x[1]["continuous_days"],
            reverse=True
        )[:10]

        msg = ["🏆 今日契约/签到榜"] + [
            f"{i + 1}. 契约/签到者 {data.get('username', '未知')} - 连续 {data['continuous_days']}天"
            for i, (uid, data) in enumerate(ranked)
        ]
        yield event.plain_result("\n".join(msg))