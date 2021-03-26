from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import json


@dataclass
class Manipulator:
    json: Path

    def __post_init__(self):
        with self.json.open(mode="r") as f:
            self.data = json.load(f)
        self.helices: List[Dict] = self.data["vstrands"].copy()

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
            return self.helices.copy()
        else:
            return [h for h in self.helices if h[propname] == propvalue]

    def delete_helices(self, helices):
        """ delete all helices in selection from manipulator """
        while helices:
            self.helices.remove(helices.pop())

    def shift_all_helices(self, shiftnumber):
        """ shifts the helix NUMBERS by the given shiftnumber
            affects all (!) helices
            this is the "correct" shifting mode as it affects the staple and scaffold indices as well"""

        print("shifting...")
        self.shift_arrangement(shiftnumber, "num")
        # self.shift_arrangement(shiftnumber, "row")

        for helix in self.helices:
            helix["scaf"] = "[" + \
                self._shift_bases(helix["scaf"], shiftnumber)+"]"
            helix["stap"] = "[" + \
                self._shift_bases(helix["stap"], shiftnumber) + "]"
        # TODO: shift color dict!!!
        print("done")

    def _shift_bases(self, base_seq, shift):
        # base seq as string in the format "[1,2,3,3],[....],[n,n,n,n]"
        # return string has the same format
        base_seq = base_seq[2:len(base_seq)-2]
        # print (base_seq)
        # stap_seq = stap_seq[1:len(stap_seq)-1]
        base_seq = base_seq.split("],[")

        # final_list = list()

        return_staple_list = str()

        for base in base_seq:
            base_list = base.split(",")
            # print (base_list)
            if (int(base_list[0])) > -1:
                base_list[0] = str(int(base_list[0])+shift)
            if (int(base_list[2])) > -1:
                base_list[2] = str(int(base_list[2])+shift)
            shifted_base_seq = str()
            for element in base_list:
                shifted_base_seq = shifted_base_seq+element+","
            shifted_base_seq = "[" + \
                shifted_base_seq[0:len(shifted_base_seq)-1]+"]"
            return_staple_list = return_staple_list+shifted_base_seq+","

        return (return_staple_list[0:len(return_staple_list)-1])

    def shift_arrangement(self, helices, shift, direction="col"):
        # affects only helices in the "search_result", run find_helices first
        # print (shift)
        # print (direction)
        print("moving...")
        for helix in helices:
            # print (helix[direction])
            helix[direction] = str(int(helix[direction])+int(shift))
        print("done")
        # self.search_result = list()

    def add_file(self, filename):
        add_helices = list()
        add_helices = self.parse_json_content(self.read_file(filename)[1])
        number_of_helices_new = len(add_helices)
        if number_of_helices_new % 2 != 0:
            number_of_helices_new = number_of_helices_new+1
        # in order to prevent position(row, col) conflict, the rows of the old helices should be moved first
        self.shift_all_helices(number_of_helices_new)
        self.helices = self.helices + add_helices
        # for helix in self.helices:
        # print (helix["num"])

    def color_replace(self, old_color, new_color):
        print("replacing color...")
        for helix in self.helices:
            # print (helix["stap_colors"])
            helix_color = helix["stap_colors"][2:len(
                helix["stap_colors"])-2].split("],[")
            helix_color_new = str()
            # print (helix_color)
            for color_info in helix_color:
                if len(color_info) > 0:
                    color_split = color_info.split(",")
                    if (old_color == "all"):
                        color_split[1] = new_color
                    else:
                        if color_split[1] == old_color:
                            color_split[1] = new_color

                    mod_color_info = "["+color_split[0]+","+color_split[1]+"]"
                    helix_color_new = helix_color_new + mod_color_info + ","
            # print (helix_color_new)
            helix["stap_colors"] = "[" + \
                helix_color_new[0:len(helix_color_new)-1]+"]"
        print("done")

    def erase_loops(self, helices):
        # deletes loops in the helices of search_result
        print("eraseing scaffold loops...")
        for helix in helices:
            localloops = helix["loop"][1:len(helix["loop"])-1].split(",")
            returnloop = str()
            for loop in localloops:
                if (int(loop) > 0):
                    loop = "0"
                returnloop = returnloop + str(loop)+","
            loopprop = "["+returnloop[0:len(returnloop)-1]+"]"
            helix["loop"] = loopprop
        print("done")

    def erase_staples(self):
        print("erasing staples...")
        for helix in self.helices:
            helix["stap"]
            level01 = helix["stap"][2:len(helix["stap"])-2].split("],[")
            stap_info_deleted = str()

            for _ in range(0, len(level01)):
                stap_info_deleted = stap_info_deleted+"[-1,-1,-1,-1],"
            helix["stap"] = "[" + \
                stap_info_deleted[0:len(stap_info_deleted)-1]+"]"
        print("done")

    def equalize_len(self):
        # equalizes the length of all helices (i.e. the raster)
        maxlen = 0
        maxdnalen = 0
        for helix in self.helices:
            loops = helix["loop"].split(",")
            if len(loops) > maxlen:
                maxlen = len(loops)

        for helix in self.helices:
            skips = helix["skip"].split(",")
            if len(skips) > maxlen:
                maxlen = len(skips)

        restlen = maxlen % 21
        if restlen != 0:
            maxlen = maxlen + restlen

        restdnalen = maxdnalen % 21
        if restdnalen != 0:
            maxdnalen = maxdnalen + restdnalen

        for helix in self.helices:
            staps = helix["stap"].split("],[")
            if len(staps) > maxdnalen:
                maxdnalen = len(staps)

        for helix in self.helices:
            scaffolds = helix["scaf"].split("],[")
            if len(scaffolds) > maxdnalen:
                maxdnalen = len(scaffolds)

        for helix in self.helices:

            print("loop: "+str(len(helix["loop"].split(","))))
            print(len(helix["skip"].split(",")))
            print(len(helix["scaf"].split("],[")))
            print(len(helix["stap"].split("],[")))

            if len(helix["loop"].split(","))-maxlen != 0:
                # different length
                oldlen = len(helix["loop"].split(","))
                # print (maxlen-oldlen)
                for _ in range(0, (maxlen-oldlen)):
                    # print (len(helix["loop"].split(",")))
                    helix["loop"] = helix["loop"]+",0"
                # newlen = len(helix["loop"].split(","))
                # print (str(oldlen)+"  "+str(newlen))

            if len(helix["skip"].split(","))-maxlen != 0:
                # different length
                oldlen = len(helix["skip"].split(","))
                for _ in range(0, (maxlen-oldlen)):
                    helix["skip"] = helix["skip"]+",0"

            if len(helix["stap"].split("],["))-maxdnalen != 0:
                # different length
                oldlen = len(helix["stap"].split("],["))
                # print (oldlen)
                for _ in range(0, (maxdnalen-oldlen)):
                    helix["stap"] = helix["stap"]+",[-1,-1,-1,-1]"
                # newlen = len(helix["stap"].split("],["))
                # print (str(oldlen)+"  "+str(newlen))

            if len(helix["scaf"].split("],["))-maxdnalen != 0:
                # different length
                oldlen = len(helix["scaf"].split("],["))
                for _ in range(0, (maxdnalen-oldlen)):
                    helix["scaf"] = helix["scaf"]+",[-1,-1,-1,-1]"

            # print ("loop: "+str(len(helix["loop"].split(","))))
            # print (len(helix["skip"].split(",")))
            # print (len(helix["scaf"].split("],[")))
            # print (len(helix["stap"].split("],[")))

    def fix_legacy(self):
        """ Files generated by json_manipulator < 0.7 might crash with cadnano2
                Fix errors with:
                * stap_color: p not updated
        """
        # TODO: reset staple_color list
        raise NotImplementedError
