import datetime
import logging

from astrbot.api.all import *
from astrbot.api.event.filter import command, event_message_type, EventMessageType

from .core.check_in_manager import CheckInManager
from .core.data_manager import DataManager
from .core.rank_system import RankSystem
from .messages import get_random_message

logger = logging.getLogger("pluginCheckIn")

@register("签到插件", "祁筱欣", "一个签到插件", "1.0.0",
          "https://github.com/xiaomizhoubaobei/astrbot_plugin_checkin")
class CheckInPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_manager = DataManager()
        self.check_in_manager = CheckInManager(self.data_manager)
        self.rank_system = RankSystem(self.data_manager)

    def _get_context_id(self, event: AstrMessageEvent) -> str:
        """多平台兼容的上下文ID生成"""
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

    @command("琼哗台签到", alias=["琼哗台打卡"])
    async def check_in(self, event: AstrMessageEvent):
        """每日签到"""
        try:
            ctx_id = self._get_context_id(event)
            user_id = event.get_sender_id()
            username = event.get_sender_name()

            result = self.check_in_manager.process_check_in(user_id, username, ctx_id)
            
            if result["status"] == "duplicate":
                yield event.plain_result(result["message"])
                return

            user_data = result["user_data"]
            yield event.plain_result(
                f"✨【契约成立】\n"
                f"🎉 {username}，感谢您的签到！\n"
                f"📅 今日日期: {result['today']}\n"
                f"👤 用户名: {user_data['username']}\n"
                f"📈 累计签到天数: {user_data['total_days']}\n"
                f"📆 本月签到天数: {user_data['month_days']}\n"
                f"💎 累计获得星之碎片/积分: {user_data['total_rewards']}\n"
                f"🌟 本月获得星之碎片/积分: {user_data['month_rewards']}\n"
                f"📅 连续签订契约: {user_data['continuous_days']}天\n"
                f"🎁 获得星之碎片/积分: {result['rewards']}个\n"
                f"💬 契约签订寄语: {get_random_message()}"
            )

        except Exception as e:
            logger.error(f"签到处理异常: {str(e)}", exc_info=True)
            yield event.plain_result("🔧 签到and契约服务暂时不可用，请联系管理员/群主")

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
        ctx_id = self._get_context_id(event)
        ranked = self.rank_system.get_rank(ctx_id, "total_rewards")
        yield event.plain_result(
            self.rank_system.format_rank(ranked, "累计星之碎片/积分排行榜", "total_rewards")
        )

    @command("琼哗台签到月奖励排行榜", alias=["琼哗台签到月排行"])
    async def month_rewards_rank(self, event: AstrMessageEvent):
        """月奖励排行榜"""
        ctx_id = self._get_context_id(event)
        ranked = self.rank_system.get_rank(ctx_id, "month_rewards")
        yield event.plain_result(
            self.rank_system.format_rank(ranked, "本月星之碎片/积分排行榜", "month_rewards")
        )

    @command("琼哗台签到总天数排行榜", alias=["琼哗台签到总天数排行"])
    async def total_days_rank(self, event: AstrMessageEvent):
        """总天数排行榜"""
        ctx_id = self._get_context_id(event)
        ranked = self.rank_system.get_rank(ctx_id, "total_days")
        yield event.plain_result(
            self.rank_system.format_rank(ranked, "累计契约天数榜", "total_days")
        )

    @command("琼哗台签到月天数排行榜", alias=["琼哗台签到月天数排行"])
    async def month_days_rank(self, event: AstrMessageEvent):
        """月天数排行榜"""
        ctx_id = self._get_context_id(event)
        ranked = self.rank_system.get_rank(ctx_id, "month_days")
        yield event.plain_result(
            self.rank_system.format_rank(ranked, "本月契约/签到天数榜", "month_days")
        )

    @command("琼哗台签到今日排行榜", alias=["琼哗台签到今日排行", "琼哗台签到日排行"])
    async def today_rank(self, event: AstrMessageEvent):
        """今日签到榜"""
        ctx_id = self._get_context_id(event)
        today = datetime.date.today().isoformat()
        ranked = self.rank_system.get_today_rank(ctx_id, today)
        yield event.plain_result(
            self.rank_system.format_rank(ranked, "今日契约/签到榜", "continuous_days")
        )