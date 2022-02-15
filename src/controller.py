#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import concurrent
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
import random
import datetime
import os
import logging
import logger
import yaml
from manager import APIStressManager

def unwrap_manager_run(obj, *args, **kwargs):
    APIStressManager.start_test(obj)

class APIStressController:
    LOG_DIR = "./log"
    STATS_DIR = "./stats"

    def __init__(self, config):
        self.config = config
        # self.name = name
        self.mp_manager = multiprocessing.Manager()
        # self.config = self.mp_manager.dict()
        self.result_dict = self.mp_manager.dict()
        self.lock = self.mp_manager.Lock()
        self.reset()
    
    def reset(self):
        self.api_managers = []
        pass
        # self.num_executed = 0
        # self.num_succeed = 0
        # self.num_error = 0
        # self.num_connection_error = 0
        # self.sum_response_time = 0
        # self.min_response_time = 1e10
        # self.max_response_time = -1

    def start_test(self):
        path = "controller.log"
        _logger = logger.create_basic_logger(path, path, stderr_level=logging.INFO)

        _logger.info("controller start")
        apis = self.config["apis"]
        num_workers = len(apis)

        if not os.path.exists(APIStressController.LOG_DIR):
            os.makedirs(APIStressController.LOG_DIR)
        if not os.path.exists(APIStressController.STATS_DIR):
            os.makedirs(APIStressController.STATS_DIR)

        max_test_time = 0

        for api in apis:
            manager = APIStressManager(api)
            self.api_managers.append(manager)
            # 全てのAPIのテスト時間の中で最も長いものを探す
            max_test_time = max(max_test_time, api["time"])
        
        # for manager in self.api_managers:
        #     manager.start_test()

        # with ProcessPoolExecutor(max_workers=num_workers) as executor:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Future作成
            futures = []
            for manager in self.api_managers:
                future = executor.submit(unwrap_manager_run, manager)
                futures.append(future)

            # 実行
            try:
                timeout = max_test_time + 5
                for future in concurrent.futures.as_completed(futures, timeout):
                    # print("g", future)
                    result = future.result()
                    # print(result)

            except concurrent.futures.TimeoutError as _:
                # 現在のfutureの状態を表示
                _logger.warning("Timeout")
                for future in futures:
                    _logger.warning("{} running: {} cancelled: {}".format(
                        id(future), future.running(), future.cancelled()))

                # Futureをキャンセル
                for future in futures:
                    if not future.running():
                        future.cancel()

                # プロセスをKill
                # _logger.warning("kill")
                # for process in executor._processes:
                #     # _logger.warning(str(dir(process)))
                #     _logger.warning(str(process.pid))
                #     process.terminate()
                # for process in executor._processes.values():
                #     process.kill()
            _logger.warning("end of with")

        # 実行後のfutureの状態を確認
        _logger.info("Executor Shutdown")
        for future in futures:
            _logger.warning("{} running: {} cancelled: {}".format(
                id(future), future.running(), future.cancelled()))

        _logger.info("controller stop")

if __name__ == '__main__':
    config = None
    with open('config.yaml') as file:
        config = yaml.safe_load(file)
    # print(config)
    controller = APIStressController(config)
    controller.start_test()