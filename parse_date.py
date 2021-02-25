import datetime

PERIODS = {
    "янв": (1, 2021),
    "фев": (2, 2021),
    "мар": (3, 2021),
    "апр": (4, 2021),
    "мая": (5, 2021),
    "июн": (6, 2021),
    "июл": (7, 2020),
    "авг": (8, 2020),
    "сен": (9, 2020),
    "окт": (10, 2020),
    "ноя": (11, 2020),
    "дек": (12, 2020),
}

def parse_date(date_template):
    list_of_elemens = date_template.split()
    print(list_of_elemens)
    print(datetime.datetime(year=PERIODS[list_of_elemens[2][:3]][1], day=int(list_of_elemens[1]), month=PERIODS[list_of_elemens[2][:3]][0]))
    print(datetime.datetime(year=PERIODS[list_of_elemens[5][:3]][1], day=int(list_of_elemens[4]), month=PERIODS[list_of_elemens[5][:3]][0]))


if __name__ == '__main__':
    template = '\nс 01 ноября\nдо 30 ноября\n'
    parse_date(template)

    # print(datetime.datetime.strftime(datetime.datetime.now(), '%a %b %d, %Y'))
    # month_number = datetime.datetime.strptime('ноября', '%b').month
    # print(month_number)