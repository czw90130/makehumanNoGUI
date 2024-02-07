import logging

# 定义一个新的日志级别 NOTICE
NOTICE = logging.INFO + 5
logging.addLevelName(NOTICE, 'NOTICE')

# 配置日志器
logger = logging.getLogger('custom_logger')
logger.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 控制台日志处理器
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def message(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def notice(msg, *args, **kwargs):
    logger.log(NOTICE, msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)
