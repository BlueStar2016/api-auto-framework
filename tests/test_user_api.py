import pytest
import json
from core.logger import logger


class TestUserAPI:

    # 数据驱动：从 JSON 文件读取测试数据
    @pytest.mark.parametrize("test_data", [
        {"case_name": "创建普通用户", "role": "user", "expected_status": 201},
        {"case_name": "创建管理员", "role": "admin", "expected_status": 201},
        # 可以从外部文件动态加载更多数据
    ])
    def test_create_user(self, api_client, enum_data, test_data):
        """
        创建用户接口测试
        使用了 enum_data 中的角色枚举值
        """
        # 假设 enum_data 包含 {'roles': ['user', 'admin', 'super_admin']}
        # 我们可以校验 test_data 中的 role 是否合法
        assert test_data['role'] in enum_data.get('roles', []), f"Invalid role: {test_data['role']}"

        payload = {
            "username": f"test_{test_data['role']}_{pytest.current_time}",  # 使用时间戳保证唯一
            "role": test_data['role'],
            "email": f"test@{test_data['role']}.com"
        }

        response = api_client.post("/users", json=payload)
        assert response.status_code == test_data['expected_status']

        result = response.json()
        assert result['role'] == test_data['role']
        logger.info(f"Test case '{test_data['case_name']}' passed.")

    # 另一种数据驱动方式：直接从外部文件读取
    @pytest.mark.parametrize("test_data",
                             json.load(open('data/test_cases/user_scenarios.json', 'r', encoding='utf-8'))
                             )
    def test_user_scenarios_from_file(self, api_client, test_data):
        """从 JSON 文件读取测试场景"""
        response = api_client.post(test_data['endpoint'], json=test_data['payload'])
        assert response.status_code == test_data['expected_status']
        # 进一步断言...