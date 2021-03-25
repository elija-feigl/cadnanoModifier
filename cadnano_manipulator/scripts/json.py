from cadnano_manipulator.core.manipulator import Manipulator
from cadnano_manipulator.version import __version__
import random


menuchoice = str()


# for helix in json.helices:
##    print (helix["stap_colors"])
##    helix_color = helix["stap_colors"][2:len(helix["stap_colors"])-2].split("],[")
##    helix_color_new = str()
# print (helix_color)
# for color_info in helix_color:
# if len(color_info)>0:
##            color_split = color_info.split(",")
##            color_split[1] = "3407718"
##
##            mod_color_info = "["+color_split[0]+","+color_split[1]+"]"
##            helix_color_new = helix_color_new + mod_color_info + ","
# print (helix_color_new)
##    helix["stap_colors"] = "["+helix_color_new[0:len(helix_color_new)-1]+"]"
# print (helix["stap_colors"])
##
# sub_element[1] = "16711680";
# new_color="["+sub_element[0]+","+sub_element[1]+"]"
# helix_color_new = helix_color_new + new_color
# helix["stap_colors"] = "["+helix_color_new+"]"
# print (helix["stap_colors"])
##
###test.generate_json_file ("test_mod.json")

#json.color_replace ("1507550","3407718")

def search_input_parse(searchterm):
    searchterm = searchterm.strip()
    if searchterm.find("-") < 0:
        return (searchterm.split(","))
    else:
        bounderies = searchterm.split("-")
        helixlist = str()
        for i in range(int(bounderies[0]), int(bounderies[1])+1):
            helixlist = helixlist+str(i)+","
        return (helixlist[0:len(helixlist)-1].split(","))


random.seed(16777215)
while (menuchoice != "5"):
    print("json_modifier v1.6")
    print()
    print("--- Menu ---")
    print()
    print("1: Read file")
    print("2: Manipulate")
    print("    2a: Delete Helices")
    print("    2b: shift all helix-numbers")
    print("    2c: shift position")
    #print ("    2d: shift cols")
    #print ("    2e: shift helix numbers (dangerous!)")
    print("    2d: add another json file")
    print("    2e: replace staple color")
    print("    2f: erase scaffold loops")
    print("    2g: unset search")
    print("    2h: color all staples")
    print("    2i: erase all staples")
    print("3: save current file")
    print()
    print("5: Exit")
    print()
    menuchoice = input("Please choose number: ")

    if menuchoice == "1":
        json = Manipulator(input("file-name?: "))

    if menuchoice == "2a":
        # helix delete
        print()
        print()
        helixlist = input("Helix numbers? (comma separated): ")
        number_before = json.number_of_helices()
        #search_list = helixlist.split(",")
        #print (search_list)
        for helix in search_input_parse(helixlist):
            json.find_helices("num", helix)

        json.delete_helices()
        number_after = json.number_of_helices()
        print("Number of deleted helices: "+str(number_before - number_after))
        input("<any key>: go back to menu ")

    if menuchoice == "2b":
        print()
        print()
        print("all helices numbers will be shifted by the following number. This number has to be even. ")
        shiftnumber = int(input("number to shift?: "))
        json.shift_helices(shiftnumber)
        json.unset_search_list()

    if menuchoice == "2c":
        print()
        print()
        helixlist = input("Helix numbers? (comma separated): ")
        #number_before = json.number_of_helices ()
        #search_list = helixlist.split(",")
        #print (search_list)
        for helix in search_input_parse(helixlist):
            json.find_helices("num", helix)
        json.shift_arrangement(input("number to shift helices rows?: "), "row")
        json.shift_arrangement(input("number to shift helices cols?: "), "col")
        json.unset_search_list()

# if menuchoice == "2d":
##        print ()
##        print ()
##        json.shift_arrangement (input("number to shift helices col?: "), "col")

# if menuchoice == "2e":
##        print ()
##        print ()
##        json.shift_arrangement (input("number to shift helices number?: "), "num")

    if menuchoice == "2d":
        print()
        print()
        json.add_file(input("filename of the file to add?: "))

    if menuchoice == "2e":
        print()
        print()
        old_color = input("old color (dec)?: ")
        new_color = input("new color (dec)?: ")
        json.color_replace(old_color, new_color)

    if menuchoice == "2f":
        print()
        print()
        helixlist = input("Helix numbers? (comma separated): ")
        #number_before = json.number_of_helices ()
        #search_list = helixlist.split(",")
        #print (search_list)
        for helix in search_input_parse(helixlist):
            json.find_helices("num", helix)
        json.erase_loops()
        json.unset_search_list()

    if menuchoice == "2g":
        print()
        print()
        json.unset_search_list()

    if menuchoice == "2h":
        print()
        print()
        json.color_replace("all", input("new color (dec)?: "))

    if menuchoice == "2i":
        print()
        print()
        json.erase_staples()

    if menuchoice == "3":
        print()
        print()
        json.generate_json_file(input("Filename?: "))

    if menuchoice == "0":
        print()
        print()

        json.egalize_len()
        print("done")
##        print (json)
##
# for helix in json.helices:
###           print (len(helix["loop"]))
##
##        maxlen = 0
# for helix in json.helices:
##            loops = helix["loop"].split(",")
# if len(loops)>maxlen:
##                maxlen = len(loops)
##
# for helix in json.helices:
##            skips = helix["skip"].split(",")
# if len(skips)>maxlen:
##                maxlen = len(skips)
##
##
##        print (maxlen)
##        print ()
##        print ()
##
# for helix in json.helices:
# if len(helix["loop"].split(","))-maxlen != 0:
# unterschiedlich lang
##                oldlen = len(helix["loop"].split(","))
# print (maxlen-oldlen)
# for i in range(0, (maxlen-oldlen)):
# print (len(helix["loop"].split(",")))
# helix["loop"]=helix["loop"]+",0"
##                newlen = len(helix["loop"].split(","))
        #print (str(oldlen)+"  "+str(newlen))

        #searchterm = input("helices?: ")
        # search_input_parse(searchterm)
        #json.color_replace ("all", "65280")
        # for helix in json.helices:
        #    item = helix.items()
        #    for (pro, val) in item:
        #        print (pro+str(len(val)))


##        zufall_color = randint(0, 16777215)
##        json02 = Manipulator("ultimate_rc_08.json")
# json.parse_json_content(json.read_file ("ultimate_rc_08.json"))
# json02.color_replace("65280",str(zufall_color))
##        json02.generate_json_file ("ultimate_rc_09.json")


##test = Manipulator("test.json")
##
##print (test.number_of_helices())
##
##
##
##
##
# test.find_helices("num","16")
# test.find_helices("num","34")
##helix16 = test.helices[test.search_result[0]]
##helix34 = test.helices[test.search_result[1]]
##
##testitems = helix16.items()
# for test in testitems:
##    (a,b) = test
##    print (a,b)
#print (helix34["stap"])
