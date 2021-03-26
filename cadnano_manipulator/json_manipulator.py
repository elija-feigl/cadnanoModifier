from core.manipulator import Manipulator
from version import __version__
import random
from pathlib import Path
import ipdb


def search_input_parse(searchterm):
    searchterm = searchterm.strip()
    if searchterm.find("-") < 0:
        return (searchterm.split(","))
    else:
        boundaries = searchterm.split("-")
        helixlist = str()
        for i in range(int(boundaries[0]), int(boundaries[1])+1):
            helixlist = helixlist+str(i)+","
        return (helixlist[0:len(helixlist)-1].split(","))


def main():
    menuchoice = str()
    while (menuchoice != "5"):
        print(f"json_modifier version {__version__}")
        print()
        print("--- Menu ---")
        print()
        print("1: Read file")
        print("2: Manipulate")
        print("    2a: Delete Helices")
        print("    2b: shift all helix-numbers")
        print("    2c: shift position")

        print("    2d: add another json file")
        print("    2e: replace staple color")
        print("    2f: erase scaffold loops")

        print("    2h: color all staples")
        print("    2i: erase all staples")
        print("3: save current file")
        print("4: fix old json_manipulator file")
        print()
        print("5: Exit")
        print()

        menuchoice = input("Please choose number: ").strip()
        # TODO: case
        if menuchoice == "1":
            while True:
                json = Path(input("file-name?: "))
                if json.exists() and json.suffix == ".json":
                    break
                else:
                    print("thats not a valid file...")
            manipulator = Manipulator(json)
            ipdb.set_trace()
            print("read {file}")

        if menuchoice == "2a":
            helixlist = input("Helix numbers? (comma separated): ")
            number_before = manipulator.number_of_helices()
            # search_list = helixlist.split(",")
            # print (search_list)
            selection = list
            for helix in search_input_parse(helixlist):
                selection.append(manipulator.find_helices("num", helix))

            manipulator.delete_helices(selection)
            number_after = manipulator.number_of_helices()
            print("Number of deleted helices: " +
                  str(number_before - number_after))
            input("<any key>: go back to menu ")

        if menuchoice == "2b":
            print(
                "all helices numbers will be shifted by the following number. This number has to be even. ")
            shiftnumber = int(input("number to shift?: "))
            manipulator.shift_all_helices(shiftnumber)

        if menuchoice == "2c":

            helixlist = input("Helix numbers? (comma separated): ")
            # number_before = manipulator.number_of_helices ()
            # search_list = helixlist.split(",")
            # print (search_list)
            for helix in search_input_parse(helixlist):
                manipulator.find_helices("num", helix)
            manipulator.shift_arrangement(
                input("number to shift helices rows?: "), "row")
            manipulator.shift_arrangement(
                input("number to shift helices cols?: "), "col")

        if menuchoice == "2d":
            manipulator.add_file(input("filename of the file to add?: "))

        if menuchoice == "2e":
            old_color = input("old color (dec)?: ")
            new_color = input("new color (dec)?: ")
            manipulator.color_replace(old_color, new_color)

        if menuchoice == "2f":
            helixlist = input("Helix numbers? (comma separated): ")
            selection = list
            for helix in search_input_parse(helixlist):
                selection.append(manipulator.find_helices("num", helix))
            manipulator.erase_loops(selection)

        if menuchoice == "2h":
            manipulator.color_replace("all", input("new color (dec)?: "))

        if menuchoice == "2i":
            manipulator.erase_staples()

        if menuchoice == "3":
            while True:
                out_json = Path(input("file-name?: "))
                if not out_json.exists() and out_json.suffix == ".json":
                    break
                else:
                    print("file exists or not a valid file")
            manipulator.generate_json_file(out_json)

        if menuchoice == "4":
            manipulator.fix_legacy()

        if menuchoice == "0":
            manipulator.equalize_len()


if __name__ == "__main__":
    random.seed(16777215)
    main()
