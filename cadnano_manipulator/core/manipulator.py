from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import json
import logging


@dataclass
class Manipulator:
    path: Path

    def __post_init__(self):
        with self.path.open(mode="r") as f:
            self.data = json.load(f)
        self.helices: List[Dict] = self.data["vstrands"].copy()
        self.logger = self._get_logger(__name__)

    def _get_logger(self, name):
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(name)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def number_of_helices(self):
        return len(self.helices)

    def generate_json_file(self, outfile):
        if outfile.exists():
            print("not overwriting file!")
        out_data = self.data.copy()
        out_data["vstrands"] = self.helices
        with outfile.open(mode='w') as f:
            json.dump(out_data, f)

    def find_helices(self, propname="all", propvalue="") -> List:
        """ search for helix by property name"""
        if propname == "all":
            return list(range(len(self.helices)))
        else:
            return [i for i, h in enumerate(self.helices) if h[propname] == propvalue]

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

    def shift_position(self, selection: List[int], shift: int):
        """ Shift the position of all selected helices.
            NOTE: scafLoop, stapLoop allways []
            TODO: include warning if shifting against lattice

            CHANGES self.helix
        """
        def adapt_overall_length():
            """ check if helices need to be extended with extra segments
                cadnano oly allows full segments

                CHANGES self.helix
            """
            for helix in self.helices:
                len_helix = len(helix["scaf"])
                termini = [len_helix, 0]
                for strand in ["scaf", "stap"]:
                    for reverse, t in enumerate(termini):
                        bases = reversed(
                            helix[strand]) if reverse else helix[strand]
                        idx = next(idx for idx, b in enumerate(
                            bases) if is_nonempty_(b))
                        t = t if reverse * (t > idx) else idx

                if (termini[0] + shift) < 0:
                    n_extra = abs(termini[0] + shift)
                    extend_right = False
                elif (termini[1] + shift) > len_helix:
                    n_extra = (termini[1] + shift) - len_helix
                    extend_right = True
                else:
                    return

            # NOTE: cadnano only allows full segments 8 for sq, 7 for hc
            n_multi = 8 if not len_helix % 8 else 7
            if len_helix % 8 and len_helix % 7:
                prompt = ""
                while prompt not in ["y", "n"]:
                    prompt = input("is this square lattice? [y/n]")
                    n_multi = 8 if prompt == "y" else 7
            n_extra = n_multi * (n_extra // n_multi + 1)
            extra = [(4 * [-1])] * n_extra
            extra_loopskip = [0] * n_extra

            for helix in self.helices:
                if extend_right:
                    self.logger.debug(f"adding {n_extra} bases to the right")
                    for strand in ["scaf", "stap"]:
                        helix[strand] = +extra
                    for mod in ["skip", "loop"]:
                        helix[mod] = +extra_loopskip
                else:
                    self.logger.debug(f"adding {n_extra} bases to the left")
                    for strand in ["scaf", "stap"]:
                        helix[strand] = extra + helix[strand]
                    for mod in ["skip", "loop"]:
                        helix[mod] = extra_loopskip + helix[mod]

        def shift_list(a_list, abs_shift, sign_shift):
            for _ in range(abs_shift):
                if sign_shift == 1:
                    a_list = a_list[-1] + a_list[:-1]
                else:
                    a_list = a_list[1:] + a_list[0]
            return a_list

        def _shift_base(base):
            """ CRITICAL: changes self.helices for helices not in selection!
                NOTE: dependent on outer scope: STRAND, SELECTION.
            """
            if base[0] in selection:  # origin helix will also be shifted
                base[1] += shift
            else:  # a crossover points from here to an unselected helix
                self.helices[base[0]][strand][base[1]][3] += shift
                self.logger.debug(
                    f"fixed broken crossover at {(base[0], base[1])}")
            if base[2] in selection:  # target helix will also be shifted
                base[3] += shift
            else:  # a crossover of an unselected helix point here
                self.helices[base[2]][strand][base[3]][1] += shift
                self.logger.debug(
                    f"fixed broken crossover at {(base[2], base[3])}")
            return base

        adapt_overall_length()

        abs_shift = abs(shift)
        sign_shift = abs(shift) // abs_shift

        for idx in selection:
            helix = self.helices[idx]
            for key in ["skip", "loop", "scaf", "stap"]:
                shift_list(helix[key], abs_shift, sign_shift)
            for strand in ["scaf", "stap"]:
                helix[strand] = [_shift_base(b) for b in helix[strand]]

            helix["stap_colors"] = [[p + shift, color]
                                    for p, color in helix["stap_colors"]]

    def shift_helix(self, selection: List[int], shift: int, direction: str):
        """ Shift the all selected helices either by row or column
        """
        if direction not in ["col", "row"]:
            print("can only shift a helix by row or col")
            return

        helices = self.helices.copy()
        for idx in selection:
            helix = helices[idx]
            helix[direction] += shift

        helix_positions = [(h["row"], h["col"]) for h in helices]
        if len(helix_positions) != len(set(helix_positions)):
            print("ABORT: shifting onto existing helix")
            return

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
            print("ABORT: these designs overlap")
            return

        # make sure they have the same length
        len_helix = len(self.helices[0]["scaf"])
        len_helix_add = len(helices_add[0]["scaf"])
        len_add = abs(len_helix - len_helix_add)
        helices_to_extend = self.helices if len_helix > len_helix_add else helices_add
        for helix in helices_to_extend:
            for strand in ["scaf", "stap"]:
                helix[strand] = [(4 * [-1])] * len_add
            for mod in ["skip", "loop"]:
                helix[mod] = [0] * len_add

        # push helix num of 2nd
        max_num = max(h["num"] for h in self.helices)
        for h in helices_add:
            h["num"] += max_num

        self.helices += helices_add
        self.data["name"] += " + " + data_add["name"]

    def fix_legacy(self):
        """ Files generated by json_manipulator < 0.7 might crash with cadnano2
                Fix errors with:
                * stap_color: p not updated
        """
        # reset position of staple_color list
        for helix in self.helices:
            p5s = [p for p, b in enumerate(helix["stap"]) if b[1] == -1]
            helix["stap_colors"] = [[p, color]
                                    for p, (_, color) in zip(p5s, helix["stap_colors"])]


def is_nonempty_(base) -> bool:
    return any(x != -1 for x in base)
