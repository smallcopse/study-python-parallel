import multiprocessing
import time
import concurrent
from concurrent.futures.process import ProcessPoolExecutor
import random
import datetime
import os


class testclass:
    def __init__(self):
        pass

class APIStressReporter:
    def __init__(self, name, result_dict, lock):
        self.name = name
        self.result_dict = result_dict
        # self.lock = self.manager.Lock()
        self.lock = lock
        # self.reset()
        # with open("./d.txt" , 'a') as f:
        #     now = datetime.datetime.now()
        #     f.write(str(now) + "\n")
        # self.result_dict["cwd"] = os.getcwd()
    
    def run(self):
        # self.result_dict["cwd"] = os.getcwd()
        # print('getcwd:      ', os.getcwd())
        # print('__file__:    ', __file__)

        # with open("C:\\Users\\Daisuke\\Documents\\GitHub\\study-python-parallel\\src\\a.txt" , 'a') as f:
        #     now = datetime.datetime.now()
        #     f.write(str(now) + "\n")

        with open("./hoge.txt" , 'a') as f:
            while True:
                result = self.get_result()
                now = datetime.datetime.now()
                # print(result + str(now))
                f.write(str(now) + "\t" + result + "\n")
                f.flush()  # ←ここでflush!!
                time.sleep(1)
        return 0
    
    def get_result(self):
        result = ""

        num_executed = 0
        num_succeed = 0
        num_error = 0
        num_connection_error = 0
        sum_response_time = 0
        min_response_time = 0
        max_response_time = 0

        self.lock.acquire()
        try:
            # num_executed = self.result_dict["num_executed"]
            # num_succeed = self.result_dict["num_succeed"]
            # num_error = self.result_dict["num_error"]
            # num_connection_error = self.result_dict["num_connection_error"]
            # sum_response_time = self.result_dict["sum_response_time"]
            # min_response_time = self.result_dict["min_response_time"]
            # max_response_time = self.result_dict["max_response_time"]

            result = "{}\t{}\t{}\t{}\t{:3.2f}\t{:3.2f}\t{:3.2f}".format(
                self.result_dict["num_executed"], self.result_dict["num_succeed"],
                self.result_dict["num_error"], self.result_dict["num_connection_error"],
                self.result_dict["sum_response_time"],
                self.result_dict["min_response_time"], self.result_dict["max_response_time"]
            )
        finally:
            self.lock.release()

        # result = "{},{},{},{},{},{},{}".format(
        #     num_executed, num_succeed, num_error, num_connection_error,
        #     sum_response_time, min_response_time, max_response_time
        # )
        return result

class APIStressWorker:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"

    def __init__(self, name, result_dict, lock):
        self.name = name
        self.result_dict = result_dict
        # self.lock = self.manager.Lock()
        self.lock = lock
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
        for i in range(100):
            x = random.uniform(0, 10)
            self.add_report(APIStressWorker.SUCCESS, x)
            time.sleep(0.5)
        # print("s", value, i, x)
        # api_result.add_report(APIStressResult.SUCCESS, x)
        # print("e", value, i, x)
        # time.sleep(100)
        return 0

class APIStressManager:

    def __init__(self, name):
        self.name = name
        self.manager = multiprocessing.Manager()
        self.result_dict = self.manager.dict()
        self.lock = self.manager.Lock()
        self.reset()
    
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

        num_workers = 20

        with ProcessPoolExecutor(max_workers=num_workers+1) as executor:
            # Future作成
            futures = []
            now = datetime.datetime.now()
            print("s " + str(now))
            for index in range(num_workers):
                worker = APIStressWorker(self.name, self.result_dict, self.lock)
                future = executor.submit(worker.run)
                # future = executor.submit(test, index)
                futures.append(future)
                # print("f", index)
            # API処理の途中経過を報告する
            now = datetime.datetime.now()
            print("w " + str(now))
            reporter = APIStressReporter(self.name, self.result_dict, self.lock)
            future = executor.submit(reporter.run)
            futures.append(future)
            now = datetime.datetime.now()
            print("a " + str(now))
            # 実行
            try:
                timeout = 20
                for future in concurrent.futures.as_completed(futures, timeout):
                    # print("g", future)
                    result = future.result()
                    # print(result)

            except concurrent.futures.TimeoutError as _:
                # 現在のfutureの状態を表示
                print("Timeout -----")
                for future in futures:
                    print(id(future), f"running: {future.running()}", f"cancelled: {future.cancelled()}")

                # Futureをキャンセル
                for future in futures:
                    if not future.running():
                        future.cancel()

                # プロセスをKill
                # !! ここを追加 !!
                for process in executor._processes.values():
                    process.kill()

        # 実行後のfutureの状態を確認
        print("Executor Shutdown -----")
        for future in futures:
            print(id(future), f"running: {future.running()}", f"cancelled: {future.cancelled()}")

        now = datetime.datetime.now()
        print("e " + str(now))
        print(self.result_dict)

if __name__ == '__main__':
    manager = APIStressManager("test")
    manager.start_test()