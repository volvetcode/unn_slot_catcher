# future functionality not sure if i will finish
import requests

import catcher.constants as const


class CatcherReport:
    def __init__(self):
        # self.psychologists_data = psychologists_data
        pass

    @staticmethod
    def send_msg(text):
        url_req = (
            "https://api.telegram.org/bot"
            + const.TELEGRAM_TOKEN
            + "/sendMessage"
            + "?chat_id="
            + const.CHAT_ID
            + "&text="
            + text
        )
        results = requests.get(url_req)

    def report_results(self):
        result = ""
        for psych in self.psychologists_data:
            if self.psychologists_data[psych] == True:
                planning = "is planning"
            else:
                planning = "not planning"

            message = const.MESSAGE_TEMPLATE.format(psy=psych, plan=planning)

            result += message

        return result
