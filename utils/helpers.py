#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import logging
import time


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(funcName)s():%(lineno)d] %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

log = get_logger(__name__)

def exe_time(func):
    def exeTime(*args, **args2):
        t0 = time.time()
        back = func(*args, **args2)
        log.info("Execute time %.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back
    return exeTime