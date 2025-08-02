import json
import logging
import os
from typing import Dict, Any
from astrbot.api.star import StarTools

logger = logging.getLogger("pluginCheckIn")

class DataManager:
    def __init__(self):
        """初始化数据管理器"""
        self.DATA_DIR = StarTools.get_data_dir("astrbot_plugin_checkin")
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.DATA_FILE = os.path.join(self.DATA_DIR, "checkin_data.json")
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """加载签到数据"""
        try:
            if not os.path.exists(self.DATA_FILE):
                return {}
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            return {}

    def save_data(self):
        """保存签到数据"""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"数据保存失败: {str(e)}")

    def get_context_data(self, ctx_id: str) -> Dict[str, Any]:
        """获取指定上下文的数据"""
        return self.data.setdefault(ctx_id, {})

    def get_user_data(self, ctx_id: str, user_id: str, username: str) -> Dict[str, Any]:
        """获取用户数据，如果不存在则初始化"""
        ctx_data = self.get_context_data(ctx_id)
        return ctx_data.setdefault(user_id, {
            "username": username,
            "total_days": 0,
            "continuous_days": 0,
            "month_days": 0,
            "total_rewards": 0,
            "month_rewards": 0,
            "last_checkin": None
        })