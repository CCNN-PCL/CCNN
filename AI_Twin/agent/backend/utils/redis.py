# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Redis 工具类
提供 Redis 数据库操作封装，供服务层调用
"""

import redis
from redis import ConnectionPool
import json
from typing import List, Dict, Any, Optional, Union
import logging
from functools import wraps

# 配置日志
logger = logging.getLogger(__name__)

class RedisManager:
    """
    Redis 管理器
    封装常用的 Redis 操作
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, max_connections: int = 20):
        if not hasattr(self, '_initialized'):
            self.host = host
            self.port = port
            self.db = db
            self.password = password
            self.max_connections = max_connections
            self._initialize_pool()
            self._initialized = True
    
    def _initialize_pool(self):
        """初始化连接池"""
        try:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=True,  # 自动解码为字符串
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            with self._get_connection() as r:
                if r.ping():
                    logger.info(f"✅ Redis连接成功: {self.host}:{self.port}/{self.db}")
                else:
                    raise ConnectionError("Redis连接测试失败")
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            raise
    
    def _get_connection(self):
        """获取 Redis 连接"""
        if not self._pool:
            self._initialize_pool()
        return redis.Redis(connection_pool=self._pool)
    
    def handle_redis_errors(func):
        """Redis操作错误处理装饰器"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except redis.ConnectionError as e:
                logger.error(f"Redis连接错误: {e}")
                raise
            except redis.TimeoutError as e:
                logger.error(f"Redis操作超时: {e}")
                raise
            except redis.RedisError as e:
                logger.error(f"Redis操作错误: {e}")
                raise
            except Exception as e:
                logger.error(f"未知错误: {e}")
                raise
        return wrapper
    
    # ==================== 字符串操作 ====================
    
    @handle_redis_errors
    def set_value(self, key: str, value: Union[str, Dict, List], expire: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值（支持字符串、字典、列表，会自动序列化）
            expire: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        with self._get_connection() as r:
            # 如果是复杂类型，序列化为 JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                result = r.setex(key, expire, value)
            else:
                result = r.set(key, value)
            
            logger.debug(f"设置键: {key}, 过期时间: {expire}秒")
            return result
    
    @handle_redis_errors
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            default: 默认值
            
        Returns:
            Any: 键值，如果键不存在返回默认值
        """
        with self._get_connection() as r:
            value = r.get(key)
            if value is None:
                return default
            
            # 尝试反序列化 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    # ==================== 列表操作 ====================
    
    @handle_redis_errors
    def list_append(self, key: str, *values: Union[str, Dict, List]) -> int:
        """
        向列表尾部添加一个或多个元素
        
        Args:
            key: 列表键名
            *values: 要添加的值
            
        Returns:
            int: 添加后列表的长度
        """
        with self._get_connection() as r:
            # 序列化复杂类型
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            result = r.rpush(key, *serialized_values)
            logger.debug(f"向列表 '{key}' 添加了 {len(values)} 个元素，新长度: {result}")
            return result
    
    @handle_redis_errors
    def list_prepend(self, key: str, *values: Union[str, Dict, List]) -> int:
        """
        向列表头部添加一个或多个元素
        
        Args:
            key: 列表键名
            *values: 要添加的值
            
        Returns:
            int: 添加后列表的长度
        """
        with self._get_connection() as r:
            # 序列化复杂类型
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            result = r.lpush(key, *serialized_values)
            logger.debug(f"向列表 '{key}' 头部添加了 {len(values)} 个元素，新长度: {result}")
            return result
    
    @handle_redis_errors
    def list_get_all(self, key: str, deserialize: bool = True) -> List[Any]:
        """
        获取列表所有元素
        
        Args:
            key: 列表键名
            deserialize: 是否尝试反序列化 JSON
            
        Returns:
            List[Any]: 列表中的所有元素
        """
        with self._get_connection() as r:
            values = r.lrange(key, 0, -1)
            
            if deserialize:
                result = []
                for value in values:
                    try:
                        result.append(json.loads(value))
                    except (json.JSONDecodeError, TypeError):
                        result.append(value)
                return result
            else:
                return values
    
    @handle_redis_errors
    def list_get_range(self, key: str, start: int = 0, end: int = -1, deserialize: bool = True) -> List[Any]:
        """
        获取列表指定范围的元素
        
        Args:
            key: 列表键名
            start: 起始索引
            end: 结束索引
            deserialize: 是否尝试反序列化 JSON
            
        Returns:
            List[Any]: 指定范围的元素
        """
        with self._get_connection() as r:
            values = r.lrange(key, start, end)
            
            if deserialize:
                result = []
                for value in values:
                    try:
                        result.append(json.loads(value))
                    except (json.JSONDecodeError, TypeError):
                        result.append(value)
                return result
            else:
                return values
    
    @handle_redis_errors
    def list_length(self, key: str) -> int:
        """
        获取列表长度
        
        Args:
            key: 列表键名
            
        Returns:
            int: 列表长度
        """
        with self._get_connection() as r:
            return r.llen(key)
    
    @handle_redis_errors
    def list_trim(self, key: str, start: int = 0, end: int = -1) -> bool:
        """
        修剪列表，只保留指定范围内的元素
        
        Args:
            key: 列表键名
            start: 起始索引
            end: 结束索引
            
        Returns:
            bool: 是否修剪成功
        """
        with self._get_connection() as r:
            result = r.ltrim(key, start, end)
            logger.debug(f"修剪列表 '{key}'，范围: {start}~{end}")
            return result
    
    @handle_redis_errors
    def list_pop_left(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """
        从列表左侧弹出元素
        
        Args:
            key: 列表键名
            deserialize: 是否尝试反序列化 JSON
            
        Returns:
            Any: 弹出的元素，如果列表为空返回 None
        """
        with self._get_connection() as r:
            value = r.lpop(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                return value
    
    @handle_redis_errors
    def list_pop_right(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """
        从列表右侧弹出元素
        
        Args:
            key: 列表键名
            deserialize: 是否尝试反序列化 JSON
            
        Returns:
            Any: 弹出的元素，如果列表为空返回 None
        """
        with self._get_connection() as r:
            value = r.rpop(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                return value
    
    # ==================== 哈希操作 ====================
    
    @handle_redis_errors
    def hash_set(self, key: str, field: str, value: Union[str, Dict, List]) -> bool:
        """
        设置哈希字段值
        
        Args:
            key: 哈希键名
            field: 字段名
            value: 字段值
            
        Returns:
            bool: 是否设置成功
        """
        with self._get_connection() as r:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = r.hset(key, field, value)
            logger.debug(f"设置哈希字段: {key}.{field}")
            return result > 0
    
    @handle_redis_errors
    def hash_get(self, key: str, field: str, default: Any = None) -> Any:
        """
        获取哈希字段值
        
        Args:
            key: 哈希键名
            field: 字段名
            default: 默认值
            
        Returns:
            Any: 字段值，如果字段不存在返回默认值
        """
        with self._get_connection() as r:
            value = r.hget(key, field)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    @handle_redis_errors
    def hash_get_all(self, key: str, deserialize: bool = True) -> Dict[str, Any]:
        """
        获取哈希所有字段和值
        
        Args:
            key: 哈希键名
            deserialize: 是否尝试反序列化 JSON
            
        Returns:
            Dict[str, Any]: 所有字段和值
        """
        with self._get_connection() as r:
            values = r.hgetall(key)
            
            if deserialize:
                result = {}
                for field, value in values.items():
                    try:
                        result[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[field] = value
                return result
            else:
                return values
    
    # ==================== 通用操作 ====================
    
    @handle_redis_errors
    def delete(self, *keys: str) -> int:
        """
        删除一个或多个键
        
        Args:
            *keys: 要删除的键名
            
        Returns:
            int: 成功删除的键数量
        """
        with self._get_connection() as r:
            result = r.delete(*keys)
            logger.debug(f"删除 {len(keys)} 个键，成功删除 {result} 个")
            return result
    
    @handle_redis_errors
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键是否存在
        """
        with self._get_connection() as r:
            return r.exists(key) > 0
    
    @handle_redis_errors
    def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 键名
            seconds: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        with self._get_connection() as r:
            return r.expire(key, seconds)
    
    @handle_redis_errors
    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间
        
        Args:
            key: 键名
            
        Returns:
            int: 剩余过期时间（秒），-1表示永不过期，-2表示键不存在
        """
        with self._get_connection() as r:
            return r.ttl(key)
    
    @handle_redis_errors
    def keys(self, pattern: str = "*") -> List[str]:
        """
        查找匹配模式的键
        
        Args:
            pattern: 匹配模式
            
        Returns:
            List[str]: 匹配的键列表
        """
        with self._get_connection() as r:
            return r.keys(pattern)
    
    @handle_redis_errors
    def flush_db(self) -> bool:
        """
        清空当前数据库
        
        Returns:
            bool: 是否清空成功
        """
        with self._get_connection() as r:
            result = r.flushdb()
            logger.warning("清空当前Redis数据库")
            return result

# 创建全局实例
redis_client = RedisManager()

# 提供快捷函数
def get_redis_client() -> RedisManager:
    """获取Redis客户端实例"""
    return redis_client