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
import traceback

class APIStressWorker:
    LOG_DIR = "./log"

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT = "TIMEOUT"

    def __init__(self, config, result_dict, lock, worker_id):
        self.config = config
        self.name = config["name"]
        self.result_dict = result_dict
        # self.lock = self.manager.Lock()
        self.lock = lock
        self.worker_id = worker_id
        self.reset()
        # self.hoge = hoge

    def reset(self):
        # self.result_dict[self.name]["num_executed"] = 0
        # self.result_dict[self.name]["num_succeed"] = 0
        # self.result_dict[self.name]["num_error"] = 0
        # self.result_dict[self.name]["num_connection_error"] = 0
        # self.result_dict[self.name]["sum_response_time"] = 0
        # self.result_dict[self.name]["min_response_time"] = 1e10
        # self.result_dict[self.name]["max_response_time"] = -1
        self.result_dict["num_executed"] = 0
        self.result_dict["num_succeed"] = 0
        self.result_dict["num_error"] = 0
        self.result_dict["num_connection_error"] = 0
        self.result_dict["sum_response_time"] = 0
        self.result_dict["min_response_time"] = 1e10
        self.result_dict["max_response_time"] = -1

    def add_report(self, result, response_time):
        self.lock.acquire()
        try:
            self.result_dict["num_executed"] += 1
            self.result_dict["sum_response_time"] += response_time
            self.result_dict["min_response_time"] = min(self.result_dict["min_response_time"], response_time)
            self.result_dict["max_response_time"] = max(self.result_dict["max_response_time"], response_time)
            
            if result == APIStressWorker.SUCCESS:
                self.result_dict["num_succeed"] += 1
            elif result == APIStressWorker.ERROR:
                self.result_dict["num_error"] += 1
            elif result == APIStressWorker.CONNECTION_ERROR:
                self.result_dict["num_connection_error"] += 1
            else:
                raise Exception("unknown result: " + result)
        finally:
            self.lock.release()
            pass

    def run(self):
        log_path = f"{APIStressWorker.LOG_DIR}/{self.name}-worker-{self.worker_id}.log"
        _logger = logger.create_basic_logger(log_path, log_path, stderr_level=logging.WARNING)
        try:
            _logger.info("worker start")
            term = self.config["term"]
            test_time = self.config["time"]
            start = time.time()
            while True:
                begin = time.time()
                x = random.randint(0, 200)
                _logger.debug(f"x={x}")
                self.add_report(APIStressWorker.SUCCESS, x)

                now = time.time()
                wait_time = term - (now - begin) * 1000
                if wait_time > 0:
                    time.sleep(wait_time / 1000.0)
                now = time.time()
                if (now - start) * 1000 > test_time:
                    break
        except Exception as e:
            _logger.error(str(e))
            _logger.error(traceback.format_exc())
        _logger.info("worker stop")
        return 0