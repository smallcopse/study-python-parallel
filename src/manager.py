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
from worker import APIStressWorker
from reporter import APIStressReporter

class APIStressManager:
    LOG_DIR = "./log"

    def __init__(self, config):
        self.name = config["name"]
        self.manager = multiprocessing.Manager()
        self.config = self.manager.dict()
        self.result_dict = self.manager.dict()
        self.lock = self.manager.Lock()
        self.reset()

        for k, v in config.items():
            self.config[k] = v
    
    def reset(self):
        pass
        # self.num_executed = 0
        # self.num_succeed = 0
        # self.num_error = 0
        # self.num_connection_error = 0
        # self.sum_response_time = 0
        # self.min_response_time = 1e10
        # self.max_response_time = -1

    def start_test(self):
        path = "{}-manager.log".format(self.name)
        _logger = logger.create_basic_logger(path, path, stderr_level=logging.INFO)
        num_workers = self.config["workers"]
        test_time = self.config["time"] / 1000.0

        _logger.info("start manager {} (workers={})".format(self.name, num_workers))

        with ProcessPoolExecutor(max_workers=num_workers+1) as executor:
            # Future作成
            futures = []
            for index in range(num_workers):
                worker = APIStressWorker(self.config, self.result_dict, self.lock, index)
                future = executor.submit(worker.run)
                # future = executor.submit(test, index)
                futures.append(future)

            # API処理の途中経過を報告する
            reporter = APIStressReporter(self.config, self.result_dict, self.lock)
            future = executor.submit(reporter.run)
            futures.append(future)
            # 実行
            try:
                timeout = test_time + 5
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
                # !! ここを追加 !!
                for process in executor._processes.values():
                    process.kill()

        # 実行後のfutureの状態を確認
        _logger.info("Executor Shutdown")
        for future in futures:
            _logger.warning("{} running: {} cancelled: {}".format(
                id(future), future.running(), future.cancelled()))

        _logger.info("stop manager {}".format(self.name))

if __name__ == '__main__':
    manager = APIStressManager("test")
    manager.start_test()