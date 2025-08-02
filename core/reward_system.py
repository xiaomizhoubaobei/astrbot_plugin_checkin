import random

class RewardSystem:
    @staticmethod
    def generate_rewards() -> int:
        """生成100-300之间的整十位随机星之碎片/积分"""
        return random.randint(10, 30) * 10

    @staticmethod
    def calculate_rewards(user_data: dict, rewards: int) -> dict:
        """计算并更新用户奖励数据"""
        today = user_data.get("last_checkin")
        current_month = user_data["last_checkin"][:7] if today else None
        
        # 更新总奖励
        user_data["total_rewards"] += rewards
        
        # 处理月奖励
        if today and current_month:
            if today[:7] != current_month:
                user_data["month_rewards"] = rewards
            else:
                user_data["month_rewards"] += rewards
        else:
            user_data["month_rewards"] = rewards
            
        return user_data