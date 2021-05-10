#! /usr/bin/env python
# -*- coding: utf-8 -*-

def is_nonempty_(base) -> bool:
    return any(x != -1 for x in base)


def is_5p(b) -> bool:
    return (b[1] == -1) and (b[3] != -1)
