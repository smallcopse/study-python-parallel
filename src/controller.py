#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import concurrent
from concurrent.futures.process import ProcessPoolExecutor
import random
import datetime
import os
import logging
import logger
import yaml
from manager import APIStressManager

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
        apis = self.config["apis"]
        num_workers = len(apis)

        os.makedirs(APIStressController.LOG_DIR, exist_ok=True)
        os.makedirs(APIStressController.STATS_DIR, exist_ok=True)

        for api in apis:
            manager = APIStressManager(api)
            self.api_managers.append(manager)
        
        for manager in self.api_managers:
            manager.start_test()

        # with ProcessPoolExecutor(max_workers=num_workers) as executor:
        #     # Future作成
        #     futures = []
        #     now = datetime.datetime.now()
        #     print("s " + str(now))
        #     for index in range(num_workers):
        #         worker = APIStressWorker(self.name, self.result_dict, self.lock)
        #         future = executor.submit(worker.run)
        #         # future = executor.submit(test, index)
        #         futures.append(future)
        #         # print("f", index)
        #     # API処理の途中経過を報告する
        #     now = datetime.datetime.now()
        #     print("w " + str(now))
        #     reporter = APIStressReporter(self.name, self.result_dict, self.lock)
        #     future = executor.submit(reporter.run)
        #     futures.append(future)
        #     now = datetime.datetime.now()
        #     print("a " + str(now))
        #     # 実行
        #     try:
        #         timeout = 20
        #         for future in concurrent.futures.as_completed(futures, timeout):
        #             # print("g", future)
        #             result = future.result()
        #             # print(result)

        #     except concurrent.futures.TimeoutError as _:
        #         # 現在のfutureの状態を表示
        #         print("Timeout -----")
        #         for future in futures:
        #             print(id(future), f"running: {future.running()}", f"cancelled: {future.cancelled()}")

        #         # Futureをキャンセル
        #         for future in futures:
        #             if not future.running():
        #                 future.cancel()

        #         # プロセスをKill
        #         # !! ここを追加 !!
        #         for process in executor._processes.values():
        #             process.kill()

        # # 実行後のfutureの状態を確認
        # print("Executor Shutdown -----")
        # for future in futures:
        #     print(id(future), f"running: {future.running()}", f"cancelled: {future.cancelled()}")

        # now = datetime.datetime.now()
        # print("e " + str(now))
        # print(self.result_dict)

if __name__ == '__main__':
    config = None
    with open('config.yaml') as file:
        config = yaml.safe_load(file)
    # print(config)
    controller = APIStressController(config)
    controller.start_test()