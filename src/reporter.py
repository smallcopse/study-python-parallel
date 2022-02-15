#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
from multiprocessing.connection import wait
import time
import concurrent
from concurrent.futures.process import ProcessPoolExecutor
import random
import datetime
import os
import logging
import logger
import traceback

class APIStressReporter:
    LOG_DIR = "./log"
    STATS_DIR = "./stats"

    OUTPUT_STATS = [
        "num_executed", "num_succeed", "num_error", "num_connection_error",
        "sum_response_time", "min_response_time", "max_response_time"
    ]

    def __init__(self, config, result_dict, lock):
        self.config = config
        self.name = config["name"]
        self.result_dict = result_dict
        # self.lock = self.manager.Lock()
        self.lock = lock
        self.stats_file = "{}.tsv".format(self.name)
        # self.reset()
        # with open("./d.txt" , 'a') as f:
        #     now = datetime.datetime.now()
        #     f.write(str(now) + "\n")
        # self.result_dict["cwd"] = os.getcwd()
    
    def run(self):
        log_path = "{}/{}-reporter.log".format(APIStressReporter.LOG_DIR, self.name)
        _logger = logger.create_basic_logger(log_path, log_path, stderr_level=logging.WARNING)

        try:
            stats_path = "{}/{}.tsv".format(APIStressReporter.STATS_DIR, self.name)
            interval = self.config["report_update_interval"]
            test_time = self.config["time"]
            start = time.time()
            next_time_to_report = start + interval
            _logger.info("reporter start")
            with open(stats_path, 'a') as f:
                header = "date\t" + "\t".join(APIStressReporter.OUTPUT_STATS) + "\n"
                f.write(header)
                f.flush()

                while True:
                    now = time.time()
                    wait_time = next_time_to_report - now
                    # _logger.info("{begin} {before} {wait_time}")
                    # _logger.info("{now} {next_time_to_report} {wait_time}")

                    if wait_time > 0:
                        time.sleep(wait_time)

                    result = self.get_result()
                    now_dt = datetime.datetime.now()
                    f.write(str(now_dt) + "\t" + result + "\n")
                    f.flush()

                    now = time.time()
                    if (now - start) * 1000 > test_time:
                        break
                    next_time_to_report += interval
        except Exception as e:
            _logger.error(str(e))
            _logger.error(traceback.format_exc())

        _logger.info("reporter stop")
        return 0
    
    def get_result(self):
        result = ""
        self.lock.acquire()
        try:
            result = "\t".join([str(self.result_dict[k]) for k in APIStressReporter.OUTPUT_STATS])
        finally:
            self.lock.release()
        return result
