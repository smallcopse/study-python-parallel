import multiprocessing

class APIStressResult:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"

    def __init__(self, name):
        self.name = name
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.Lock()
        self.reset()
    
    def reset(self):
        self.num_executed = 0
        self.num_succeed = 0
        self.num_error = 0
        self.num_connection_error = 0
        self.sum_response_time = 0
        self.min_response_time = 1e10
        self.max_response_time = -1

    def add_report(self, result, response_time):
        self.lock.acquire()
        try:
            self.num_executed += 1
            self.sum_response_time += response_time
            self.min_response_time = min(self.min_response_time, response_time)
            self.max_response_time = max(self.max_response_time, response_time)
            
            if result == APIStressResult.SUCCESS:
                self.num_succeed += 1
            elif result == APIStressResult.ERROR:
                self.num_error += 1
            elif result == APIStressResult.CONNECTION_ERROR:
                self.num_connection_error += 1
            else:
                raise Exception("unknown result: " + result)
        finally:
            self.lock.release()

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
            num_executed = self.num_executed
            num_succeed = self.num_succeed
            num_error = self.num_error
            num_connection_error = self.num_connection_error
            sum_response_time = self.sum_response_time
            min_response_time = self.min_response_time
            max_response_time = self.max_response_time
        finally:
            self.lock.release()

        result = "{},{},{},{},{},{},{}".format(
            num_executed, num_succeed, num_error, num_connection_error,
            sum_response_time, min_response_time, max_response_time
        )
        return result