# -*- coding: utf-8 -*-
# ! python3

# ======================================================================================================================
# Author: Half-Life.
# Description: Скрипт на автовзятие бодов.
# По умолчанию собирает боды и кузнеца и тейлора.
# Написан под RunUO.
# Тестировался на шарде UOAwakening.
# UOStealthClientVersion: 7.3.1;
# Warning! Будьте бдительны! - Администрация многих игровых серверов
# враждебно относится к использованию стелс клиента на своих серверах.
# Заподозрив вас в использовании стелс клиента и других неправославных программ
# они начинают сатанеть и в порыве слепой ярости могут попасть по вам Банхаммером;
# ======================================================================================================================


from datetime import datetime, timedelta
from time import sleep

from stealthapi import *

# ======================================================================================================================
# CONSTANTS
# ======================================================================================================================

TAILOR_VENDOR = 0x000B39E5  # ID NPC Тейлора.
BLACKSMITH_VENDOR = 0x003022E  # ID NPC Блексмитера.
VENDOR_CONTEXT_MENU = 1  # Номер пункта контекстного меню отвечающего за взятие бода тейлора.
BOD_TYPE = 0x2258  # Тип бода.
TAILOR_BOD_COLOR = 0x0483  # Цвет тейлор бодов.
BLACKSMITH_BOD_COLOR = 0x044E  # Цвет бс бодов.
TAKE_TAILOR = True  # Брать боды у тейлора. Чтобы отключить установите значение False.
TAKE_BLACKSMITH = False  # Брать боды у блексмитера. Чтобы отключить установите значение False.
TAILOR_BOOK = 0  # ID книги в которую слаживать тейлор боды. Если значение 0, то боды ложатся в бакпак.
BLACKSMITH_BOOK = 0  # ID книги в которую слаживать блексмит боды. Если значение 0, то боды ложатся в бакпак.
TAILOR_MSG = 'Taking Tailor BOD'
BLACKSMITH_MSG = 'Taking BS BOD'
WAIT_TIME = 500  # Время минимальной задержки. Лучше не менять.
WAIT_LAG_TIME = 10000  # Время кторое будет выжидаться при лаге. Лучше не менять.
MY_PROFILES = [
    'boder1-1', 'boder1-2', 'boder1-3', 'boder1-4', 'boder1-5', 'boder1-6', 'boder1-7',
    'boder2-1', 'boder2-2', 'boder2-3', 'boder2-4', 'boder2-5', 'boder2-6', 'boder2-7',
    'boder3-1', 'boder3-2', 'boder3-3', 'boder3-4', 'boder3-5', 'boder3-6', 'boder3-7',
    'boder4-1', 'boder4-2', 'boder4-3', 'boder4-4', 'boder4-5', 'boder4-6', 'boder4-7',
    'boder5-1', 'boder5-2', 'boder5-3', 'boder5-4', 'boder5-5', 'boder5-6', 'boder5-7',
    'boder6-1', 'boder6-2', 'boder6-3', 'boder6-4', 'boder6-5', 'boder6-6', 'boder6-7',
    'boder7-1', 'boder7-2', 'boder7-3', 'boder7-4', 'boder7-5', 'boder7-6', 'boder7-7',
    'boder8-1', 'boder8-2', 'boder8-3', 'boder8-4', 'boder8-5', 'boder8-6', 'boder8-7',
    'boder9-1', 'boder9-2', 'boder9-3', 'boder9-4', 'boder9-5', 'boder9-6', 'boder9-7',
    'boder10-1', 'boder10-2', 'boder10-3', 'boder10-4', 'boder10-5', 'boder10-6', 'boder10-7'
]

# ======================================================================================================================
# Variables
# ======================================================================================================================

tailor_bods, blacksmith_bods = 0, 0


# ======================================================================================================================
# Utils
# ======================================================================================================================

def wait_lag(wait_time=WAIT_TIME, lag_time=WAIT_LAG_TIME):
    Wait(wait_time)
    CheckLag(lag_time)
    return None


def close_gumps():
    while IsGump():
        if not Connected():
            return False
        if not IsGumpCanBeClosed(GetGumpsCount() - 1):
            return False
        CloseSimpleGump(GetGumpsCount() - 1)
    return True


# ======================================================================================================================
# Boder
# ======================================================================================================================

class Boder(object):
    def __init__(self, name):
        self.name = name
        self.time_order = datetime.datetime.now()
        self.backpack_item_count = 0

    @staticmethod
    def get_bods_count(bod_color):
        if bod_color == TAILOR_BOD_COLOR:
            global tailor_bods
            tailor_bods += CountEx(BOD_TYPE, bod_color, Backpack())
            AddToSystemJournal('Количество Тейлор бодов на чарах = {0}'.format(tailor_bods))
        else:
            global blacksmith_bods
            blacksmith_bods += CountEx(BOD_TYPE, bod_color, Backpack())
            AddToSystemJournal('Количество БС бодов на чарах = {0}'.format(blacksmith_bods))

    def check_backpack(self):
        backpack_item_count = GetToolTipRec(Backpack())
        for item in backpack_item_count:
            if len(item['Params']) == 4:
                self.backpack_item_count = int(item['Params'][0])
                break
        if self.backpack_item_count == 125:
            AddToSystemJournal('{0} Ваш рюкзак полон.'.format(self.name))
            return True
        return False

    def collect_bods(self, msg, vendor, menu, bod_color, bod_book):
        while True:
            start_time = datetime.datetime.now()
            AddToSystemJournal(msg)
            wait_lag(WAIT_TIME // 2)
            SetContextMenuHook(vendor, menu)
            wait_lag(WAIT_TIME // 2)
            RequestContextMenu(vendor)
            wait_lag()
            WaitGump('1')
            wait_lag()
            if bod_book:
                while FindTypeEx(BOD_TYPE, bod_color, Backpack(), False) > 1:
                    MoveItem(FindItem(), 1, bod_book, 0, 0, 0)
                    wait_lag()
                    close_gumps()
            if InJournalBetweenTimes('in your backpack|may be available in about', start_time,
                                     datetime.datetime.now()) > 0:
                break
        self.get_bods_count(bod_color)
        return None


if __name__ == '__main__':
    # ==================================================================================================================
    # Start Script
    # ==================================================================================================================
    ClearJournal()
    ClearSystemJournal()
    if not TAKE_TAILOR and not TAKE_BLACKSMITH:
        quit(AddToSystemJournal('Внимание ошибка! ' +
                                'Хотя бы один из параметров TAKE_TAILOR или TAKE_BLACKSMITH должен быть True.' +
                                'Скрипт остановлен.'))
    for i in range(len(MY_PROFILES)):
        MY_PROFILES[i] = Boder(MY_PROFILES[i])
    while True:
        for profile in MY_PROFILES:
            if datetime.datetime.now() > profile.time_order:
                ChangeProfile(profile.name)
                SetARStatus(True)
                Connect()
                Wait(2000)
                while not Connected():
                    Wait(500)
                if not profile.check_backpack():
                    close_gumps()
                    if TAKE_TAILOR:
                        profile.collect_bods(TAILOR_MSG,
                                             TAILOR_VENDOR,
                                             VENDOR_CONTEXT_MENU,
                                             TAILOR_BOD_COLOR,
                                             TAILOR_BOOK)
                    if TAKE_BLACKSMITH:
                        profile.collect_bods(BLACKSMITH_MSG,
                                             BLACKSMITH_VENDOR,
                                             VENDOR_CONTEXT_MENU,
                                             BLACKSMITH_BOD_COLOR,
                                             BLACKSMITH_BOOK)
                else:
                    profile.get_bods_count(TAILOR_BOD_COLOR)
                    profile.get_bods_count(BLACKSMITH_BOD_COLOR)
                    MY_PROFILES.remove(profile)
                SetARStatus(False)
                while Connected():
                    Disconnect()
                    Wait(500)
                profile.time_order = datetime.datetime.now() + timedelta(hours=1)
                if len(MY_PROFILES) == 0:
                    AddToSystemJournal('Скрипт остановлен, так как на всех чарах по 125 итемов')
                    quit('Stop')
                if profile == MY_PROFILES[-1]:
                    tailor_bods, blacksmith_bods = 0, 0

        sleep(60)
    # ==================================================================================================================
    # End Script
    # ==================================================================================================================
