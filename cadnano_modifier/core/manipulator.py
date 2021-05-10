#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .util import is_5p, is_nonempty_


@dataclass
class Manipulator:
    path: Path

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
        with self.path.open(mode="r") as f:
            self.data = json.load(f)
        self.helices: List[Dict] = self.data["vstrands"].copy()

    def number_of_helices(self):
        return len(self.helices)

    def generate_json_file(self, outfile):
        out_data = self.data.copy()
        out_data["vstrands"] = self.helices
        with outfile.open(mode='w') as f:
            json.dump(out_data, f)

    def find_helices(self, numbers=None) -> List:
        """ search for helix by number"""
        if numbers is None:
            return list(range(len(self.helices)))
        else:
            return [i for i, h in enumerate(self.helices) if h["num"] in numbers]

    def delete_helices(self, selection):
        """ delete all helices in selection from manipulator

            CHANGES self.helix
        """
        for idx in selection:
            del_helix = self.helices.pop(idx)
            # TODO: fix "broken" crossovers
            num = del_helix["num"]
            n_bases = len(1 for b in del_helix["scaf"] if is_nonempty_(b))
            self.logger.debug(f"Removed Helix {num} with {n_bases} bases")

    def _extend_helix(self, helix, n):
        extra = [(4 * [-1])] * n
        extra_loopskip = [0] * n

        for key in ["scaf", "stap", "skip", "loop"]:
            new = extra if key in ["scaf", "stap"] else extra_loopskip
            helix[key] = helix[key] + new
        return helix

    def shift_position(self, selection: List[int], shift: int):
        """ Shift the position of all selected helices.
            NOTE: scafLoop, stapLoop allways []

            CHANGES self.helix
        """
        def determine_helix_extension():
            def helical_ends(length):
                minmax = [length, 0]
                for helix in self.helices:
                    for strand in ["scaf", "stap"]:
                        for i, t in enumerate(minmax):
                            reverse = bool(i)
                            bases = reversed(
                                helix[strand]) if reverse else helix[strand]
                            idx = next(idx for idx, b in enumerate(
                                bases) if is_nonempty_(b))
                            idx = length-idx if reverse else idx
                            if reverse and (idx > t):
                                minmax[reverse] = idx
                            elif not reverse and (idx < t):
                                minmax[reverse] = idx
                return minmax

            len_helix = len(self.helices[0]["scaf"])
            minmax = helical_ends(len_helix)

            if (minmax[0] + shift) < 0:
                self.logger.error("Attempting to shift position below 0")
                sys.exit(1)

            elif (minmax[1] + shift) > len_helix:
                n_extra = (minmax[1] + shift) - len_helix
            else:
                return 0

            # NOTE: cadnano requires multiples of 32 bases for sq and 21 for hc
            HC, SQ = 21, 32
            n_multi = SQ if not len_helix % SQ else HC
            if len_helix % 32 and len_helix % HC:
                prompt = ""
                while prompt not in ["y", "n"]:
                    prompt = input("is this square lattice? [y/n]")
                    n_multi = SQ if prompt == "y" else HC
            n_extra = n_multi * (n_extra // n_multi + 1)
            return n_extra

        def adapt_overall_length():
            """ check if helices need to be extended with extra segments
                cadnano oly allows full segments

                CHANGES self.helix
            """
            n_extra = determine_helix_extension()
            if n_extra:
                self.logger.debug(f"adding {n_extra} bases")
                for helix in self.helices:
                    self._extend_helix(helix, n_extra)

        def shift_list(a_list, abs_shift, sign_shift):
            for _ in range(abs_shift):
                if sign_shift == 1:
                    a_list = [a_list[-1]] + a_list[:-1]
                else:
                    a_list = a_list[1:] + [a_list[0]]
            return a_list

        def _shift_base(base):
            """ CRITICAL: changes self.helices for helices not in selection!
                NOTE: dependent on outer scope: STRAND, SELECTION.
            """
            if base[0] != -1:
                co_idx = next(i for i, h in enumerate(
                    self.helices) if h["num"] == base[0])
                if co_idx in selection:  # origin helix will also be shifted
                    base[1] += shift
                else:  # a crossover points from here to an unselected helix
                    self.helices[co_idx][strand][base[1]][3] += shift
                    self.logger.debug(
                        f"fixed broken crossover at {(base[0], base[1])}")
            if base[2] != -1:
                co_idx = next(i for i, h in enumerate(
                    self.helices) if h["num"] == base[2])
                if co_idx in selection:  # target helix will also be shifted
                    base[3] += shift
                else:  # a crossover of an unselected helix point here
                    self.helices[co_idx][strand][base[3]][1] += shift
                    self.logger.debug(
                        f"fixed broken crossover at {(base[2], base[3])}")
            return base

        adapt_overall_length()
        abs_shift = abs(shift)
        sign_shift = abs(shift) // abs_shift
        for idx in selection:
            helix = self.helices[idx]
            for key in ["skip", "loop", "scaf", "stap"]:
                helix[key] = shift_list(helix[key], abs_shift, sign_shift)
            for strand in ["scaf", "stap"]:
                helix[strand] = [_shift_base(b) for b in helix[strand]]

            helix["stap_colors"] = [[p + shift, color]
                                    for p, color in helix["stap_colors"]]

    def shift_helix(self, selection: List[int], shift: int, direction: str):
        """ Shift the all selected helices either by row or column
        """
        if direction not in ["col", "row"]:
            self.logger.error("Can only shift a helix by row or col")
            sys.exit(1)

        helices = self.helices.copy()
        for idx in selection:
            helix = helices[idx]
            helix[direction] += shift

        helix_positions = [(h["row"], h["col"]) for h in helices]
        if len(helix_positions) != len(set(helix_positions)):
            self.logger.error("Shifting onto existing helix")
            sys.exit(1)

        self.helice = helices

    def color_replace(self, old_color, new_color):
        for helix in self.helices:
            helix["stap_colors"] = [[p, new_color]
                                    for p, color in helix["stap_colors"]
                                    if color == old_color]

    def erase_loops(self, selection):
        """ delete all loops for selected helices """
        len_helix = len(self.helices[0]["scaf"])
        for idx in selection:
            helix = self.helices[idx]
            helix["loop"] = [0] * len_helix

    def erase_skips(self, selection):
        """ delete all loops for selected helices """
        len_helix = len(self.helices[0]["scaf"])
        for idx in selection:
            helix = self.helices[idx]
            helix["skip"] = [0] * len_helix

    def express_skips_loops(self):
        """ convert loops to actual bases & remove skips.
            result will look wild.
        """
        return NotImplementedError

    def add_file(self, path_add: Path):
        with path_add.open(mode="r") as f:
            data_add = json.load(f)
            helices_add = data_add["vstrands"].copy()

        # check if they can be matched
        coor_add = {(h["row"], h["col"]) for h in helices_add}
        coor = {(h["row"], h["col"]) for h in self.helices}
        if not (coor - coor_add):
            self.logger.error("These designs overlap helices.")
            sys.exit(1)

        # make sure they have the same length
        len_helix = len(self.helices[0]["scaf"])
        len_helix_add = len(helices_add[0]["scaf"])
        len_add = abs(len_helix - len_helix_add)
        if len_add > 0:
            self.logger.debug(
                f"One of the designs needs to be extended by {len_add} bases.")
        helices_to_extend = self.helices if len_helix < len_helix_add else helices_add
        for helix in helices_to_extend:
            self._extend_helix(helix, len_add)

        # push helix num of 2nd
        num_add = max(h["num"] for h in self.helices) + 1
        if num_add % 2:
            num_add += 1

        for helix_add in helices_add:
            helix_add["num"] += num_add
            for strand in ["scaf", "stap"]:
                for base in helix_add[strand]:
                    for i in [0, 2]:
                        base[i] = base[i] + num_add if base[i] != -1 else - 1

        self.helices += helices_add
        self.data["name"] += " + " + data_add["name"]

    def fix_legacy(self):
        """ Files generated by json_manipulator < 0.7 might crash with cadnano2
                Fix errors with:
                * stap_color: p not updated
        """
        has_change = False
        length_max = len(self.helices[0]["stap"])
        need_reset_length = False
        for helix in self.helices:
            # reset position of staple_color list
            p5s = [p for p, b in enumerate(helix["stap"]) if is_5p(b)]
            p5s_legacy = [p for p, _ in helix["stap_colors"]]
            if p5s != p5s_legacy:
                self.logger.info("Resetting faulty staple_color dictionary")
                has_change = True
                helix["stap_colors"] = [[p, color]
                                        for p, (_, color) in zip(p5s, helix["stap_colors"])]

            length = len(helix["stap"])
            num = helix["num"]
            if not length % 32 and not length % 21:
                self.logger.info(
                    f"Incorrect length for either SQ or HC: helix {num}:{length} bases")
                # NOTE: might not need a fix, just info

            if length != length_max:
                need_reset_length = True
                self.logger.debug(
                    f"Length not matching for helix {num}:{length} bases")
            length_max = length if length > length_max else length_max

            length_scaf = len(helix["stap"])
            length_loop = len(helix["loop"])
            length_skip = len(helix["skip"])
            if not (length == length_scaf == length_loop == length_loop):
                length_log = (length_scaf, length, length_skip, length_loop)
                self.logger.debug(
                    f"Length of scaf, stap, loop, skips do not match for helix {num}:{length_log}")
                for strand in ["scaf", "stap"]:
                    if len(helix[strand]) < length_max:
                        add = length_max - len(helix[strand])
                        helix[strand] += [(4 * [-1])] * add
                        self.logger.debug(
                            f"Adding {add} empty bases to the end of {strand}")
                for mod in ["loop", "skip"]:
                    if len(helix[mod]) < length_max:
                        add = length_max - len(helix[mod])
                        helix[mod] += [0] * add
                        self.logger.debug(
                            f"Adding {add} empty bases to the end of {mod}")
                self.logger.info(
                    f"Fix length inconsistency of subelements for helix {num}")
                has_change = True

        if need_reset_length:
            self.logger.info(
                f"Resetting inconsistent helical length to {length_max}")
            has_change = True
            for helix in self.helices:
                length = len(helix["stap"])
                add = length_max - length
                if add > 0:
                    helix["stap"] += [(4 * [-1])] * add
                    helix["scaf"] += [(4 * [-1])] * add
                    helix["loop"] += [0] * add
                    helix["skip"] += [0] * add
        return has_change
