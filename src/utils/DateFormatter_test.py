from datetime import datetime, timedelta
import unittest
from DateFormatter import DateFormatter
from freezegun import freeze_time

class DateFormatterTest(unittest.TestCase):

    @freeze_time("2025-11-17 12:00:00")
    def test_date_formatter(self):
        #today datetime, 13:00
        today_expected_datetime = datetime.now(DateFormatter.timezone).replace(hour=13, minute=0, second=0, microsecond=0)
        today_result = DateFormatter.date_formatter('сьогодні о 13:00')
        self.assertEqual(today_expected_datetime, today_result)
        #yesterday datetime. 6.01
        yesterday_expected_datetime = datetime.now(DateFormatter.timezone).replace(hour=6, minute=1, second=0, microsecond=0) - timedelta(days=1)
        yesterday_result = DateFormatter.date_formatter('вчора о 6:01')
        self.assertEqual(yesterday_expected_datetime, yesterday_result)
        # 16th of november
        nvmb_16_expected_datetime = datetime.now(DateFormatter.timezone).replace(year=2025,month=11,day=16,hour=0, minute=0, second=0, microsecond=0)
        nvmb_16_result = DateFormatter.date_formatter('16 листопада')
        self.assertEqual(nvmb_16_expected_datetime, nvmb_16_result)
        # 25th of november
        nvmb_25_expected_datetime = datetime.now(DateFormatter.timezone).replace(year=2024,month=11,day=25,hour=0, minute=0, second=0, microsecond=0)
        nvmb_25_result = DateFormatter.date_formatter('25 листопада')
        self.assertEqual(nvmb_25_expected_datetime, nvmb_25_result)


if __name__ == '__main__':
    unittest.main()