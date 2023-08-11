from datetime import datetime

date_format = "%d-%m-%Y-%H:%M"


class Date:
    """Класс получения текущей даты и времени"""
    @staticmethod
    def current_date():
        date = datetime.now()
        return date.strftime(date_format)
