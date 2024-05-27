from nlp.mongo_tools import get_active_channels
from sql import get_table


class ClientWrapper:
    """
    Схема остается: есть публичные каналы на 1 номер и приватные на другой. На каждой из машин есть свой urgent private: ProfitGateClub и rcbprivate
    """

    def __init__(self, app, api_id, api_hash: str, session_name: str, is_private: bool, non_urgent_channels: int,
                 sleep_time: float):
        self.api_id = api_id
        self.api_hash = api_hash
        self.app = app
        self.session_name = session_name
        self.sleep_time = sleep_time
        self.success_calls = 0
        self.non_urgent_channels = non_urgent_channels
        self.last_id = 0
        self.channels = get_active_channels(private=is_private)
        self.renumerate_channels()

    def print_channels(self):
        print(f"{self.session_name}: {self.channels}")

    def renumerate_channels(self):
        out_id = 0
        for item in self.channels:
            item['out_id'] = out_id
            out_id += 1

    def record_success_calls(self):
        self.success_calls += 1
        if self.success_calls >= 100:
            self.record_db_performance(timeout=0)
            self.success_calls = 0
            self.sleep_time = max(self.sleep_time * 0.99, 0.01)
            print(f"decreasing sleep time: {self.sleep_time=}")

    def record_db_performance(self, timeout):
        query = f"""insert into public.tgchannels_timeout(success_calls, sleep_time, timeout, session)
                    values({self.success_calls}, {self.sleep_time}, {timeout}, '{self.session_name}')
                """
        get_table.exec_query(query)
        if timeout > 0:
            self.success_calls = 0
            self.sleep_time = 1.05 * self.sleep_time
            print(f"increasing sleep time: {self.sleep_time=}")
