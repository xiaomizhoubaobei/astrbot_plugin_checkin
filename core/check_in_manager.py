import datetime
from typing import Dict, Any
from .data_manager import DataManager
from .reward_system import RewardSystem

class CheckInManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.reward_system = RewardSystem()

    def process_check_in(self, user_id: str, username: str, ctx_id: str) -> Dict[str, Any]:
        """处理签到逻辑"""
        today = datetime.date.today().isoformat()
        user_data = self.data_manager.get_user_data(ctx_id, user_id, username)
        
        # 检查重复签到
        if user_data["last_checkin"] == today:
            return {"status": "duplicate", "message": "⚠️ 今日已完成打卡/签到并签订契约，请勿重复操作"}
        
        # 更新连续签到天数
        self._update_continuous_days(user_data, today)
        
        # 生成并分配奖励
        rewards = self.reward_system.generate_rewards()
        self._update_user_stats(user_data, rewards, today)
        
        # 保存数据
        self.data_manager.save_data()
        
        return {
            "status": "success",
            "user_data": user_data,
            "rewards": rewards,
            "today": today
        }

    def _update_continuous_days(self, user_data: Dict[str, Any], today: str) -> None:
        """更新连续签到天数"""
        last_date = user_data["last_checkin"]
        if last_date:
            last_day = datetime.date.fromisoformat(last_date)
            if (datetime.date.today() - last_day).days == 1:
                user_data["continuous_days"] += 1
            else:
                user_data["continuous_days"] = 1
        else:
            user_data["continuous_days"] = 1

    def _update_user_stats(self, user_data: Dict[str, Any], rewards: int, today: str) -> None:
        """更新用户统计数据"""
        # 更新总天数
        user_data["total_days"] += 1
        
        # 处理月天数
        if user_data["last_checkin"] and user_data["last_checkin"][:7] != today[:7]:
            user_data["month_days"] = 1
        else:
            user_data["month_days"] += 1
        
        # 更新奖励
        self.reward_system.calculate_rewards(user_data, rewards)
        user_data["last_checkin"] = today