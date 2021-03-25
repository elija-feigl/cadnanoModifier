from dataclasses import dataclass


@dataclass
class Manipulator:
    filename: str

    def __post_init__(self, filename):
        self.helices = list()
        self.search_result = list()

        json_file_content = self.read_file(self.filename)

        self.file_start = json_file_content[0]
        self.file_end = json_file_content[2]

        self.helices = self.parse_json_content(json_file_content[1])

    def read_file(self, filename):
        json_file = open(filename, "r")
        content = json_file.read()

        json_file.close()

        content = content.replace("[{", "{filespliter}")
        content = content.replace("}]", "{filespliter}")
        return content.split("{filespliter}")

    def parse_json_content(self, file_content):
        helices = list()
        helices_file = file_content.split("},{")
        for helix_info in helices_file:
            #print (helix_info.rstrip(","))
            current_helix_info = helix_info.rstrip(",").split(","+chr(34))
            #print (current_helix_info)
            current_properties = dict()

            for current_property_info in current_helix_info:
                current_property_info = current_property_info.replace(
                    chr(34), "")
                current_property = current_property_info.split(":")

                current_properties[current_property[0]] = current_property[1]
                #print (current_property_info)
            helices.append(current_properties)
            #print (current_properties["col"])
            #print (current_properties["row"])
            #print (current_properties["num"])
        return helices

    def number_of_helices(self):
        return len(self.helices)

    def generate_json_file(self, filename):
        print("generating file...")
        file_string = str()
        file_string = file_string+self.file_start+"["
        for helix in self.helices:
            current_items = helix.items()
            file_string = file_string + "{"
            for item in current_items:
                (prop, val) = item
                file_string = file_string + \
                    chr(34) + prop + chr(34)+":"+val+","
                #print (file_string + chr(34) + prop + chr(34)+":"+val+",")
            file_string = file_string + "},"
        # erase last ",":
        file_string = file_string[0:len(file_string)-1]
        #print (file_string)

        file_string = file_string + "]" + self.file_end
        file_string = file_string.replace("},]", "}]")
        print("done")
        print("writing file...")
        write_file = open(filename, "w")
        write_file.write(file_string)
        write_file.close()
        print("done")

    def find_helices(self, propname="all", propvalue=""):
        # i=0
        if propname == "all":
            self.search_result = self.helices
        else:
            for helix in self.helices:
                #print ("i: "+str(i) + "   num: "+ helix["num"])
                if helix[propname] == propvalue:
                    # treffer
                    self.search_result.append(helix)
                # i=i+1

    def delete_helices(self):
        # delete the last found helices
        # after deleting, search_result will be reseted
        for foundhelix in self.search_result:
            self.helices.remove(foundhelix)
        self.unset_search_list()

    def shift_helices(self, shiftnumber):
        # shifts the helix numbers by the given shiftnumber
        # affects all (!) helices
        # this is the "correct" shifting mode as it affects the staple and scaffold indizes as well
        print("shifting...")

        self.find_helices("all")  # all helix numbers should be shifted
        self.shift_arrangement(shiftnumber, "num")
        #self.shift_arrangement(shiftnumber, "row")

        for helix in self.helices:
            helix["scaf"] = "[" + \
                self.shift_bases(helix["scaf"], shiftnumber)+"]"
            helix["stap"] = "[" + \
                self.shift_bases(helix["stap"], shiftnumber)+"]"
        #self.search_result = list()
        print("done")

    def shift_bases(self, base_seq, shift):
        # base seq as string in the format "[1,2,3,3],[....],[n,n,n,n]"
        # return string has the same format
        base_seq = base_seq[2:len(base_seq)-2]
        #print (base_seq)
        #stap_seq = stap_seq[1:len(stap_seq)-1]
        base_seq = base_seq.split("],[")

        final_list = list()

        return_staple_list = str()

        for base in base_seq:
            base_list = base.split(",")
            #print (base_list)
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

    def shift_arrangement(self, shift, direction="col"):
        # affects only helices in the "search_result", run find_helices first
        #print (shift)
        #print (direction)
        print("moving...")
        for helix in self.search_result:
            #print (helix[direction])
            helix[direction] = str(int(helix[direction])+int(shift))
        print("done")
        #self.search_result = list()

    def unset_search_list(self):
        self.search_result = list()

    def add_file(self, filename):
        add_helices = list()
        add_helices = self.parse_json_content(self.read_file(filename)[1])
        number_of_helices_new = len(add_helices)
        if number_of_helices_new % 2 != 0:
            number_of_helices_new = number_of_helices_new+1
        # in order to prevent position(row, col) conflict, the rows of the old helices should be moved first
        self.shift_helices(number_of_helices_new)
        self.helices = self.helices + add_helices
        # for helix in self.helices:
        #print (helix["num"])

    def color_replace(self, old_color, new_color):
        print("replacing color...")
        for helix in self.helices:
            #print (helix["stap_colors"])
            helix_color = helix["stap_colors"][2:len(
                helix["stap_colors"])-2].split("],[")
            helix_color_new = str()
            #print (helix_color)
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
            #print (helix_color_new)
            helix["stap_colors"] = "[" + \
                helix_color_new[0:len(helix_color_new)-1]+"]"
        print("done")

    def erase_loops(self):
        # deletes loops in the helices of search_result
        print("eraseing scaffold loops...")
        for helix in self.search_result:
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

            for staple in range(0, len(level01)):
                stap_info_deleted = stap_info_deleted+"[-1,-1,-1,-1],"
            helix["stap"] = "[" + \
                stap_info_deleted[0:len(stap_info_deleted)-1]+"]"
        print("done")

    def egalize_len(self):
        # equalizes the length of all helics (i.e. the raster)
        maxlen = 0
        maxdnalen = 0
        for helix in json.helices:
            loops = helix["loop"].split(",")
            if len(loops) > maxlen:
                maxlen = len(loops)

        for helix in json.helices:
            skips = helix["skip"].split(",")
            if len(skips) > maxlen:
                maxlen = len(skips)

        restlen = maxlen % 21
        if restlen != 0:
            maxlen = maxlen + restlen

        restdnalen = maxdnalen % 21
        if restdnalen != 0:
            maxdnalen = maxdnalen + restdnalen

        for helix in json.helices:
            staps = helix["stap"].split("],[")
            if len(staps) > maxdnalen:
                maxdnalen = len(staps)

        for helix in json.helices:
            scafs = helix["scaf"].split("],[")
            if len(scafs) > maxdnalen:
                maxdnalen = len(scafs)

        for helix in json.helices:

            print("loop: "+str(len(helix["loop"].split(","))))
            print(len(helix["skip"].split(",")))
            print(len(helix["scaf"].split("],[")))
            print(len(helix["stap"].split("],[")))

            if len(helix["loop"].split(","))-maxlen != 0:
                # unterschiedlich lang
                oldlen = len(helix["loop"].split(","))
                #print (maxlen-oldlen)
                for i in range(0, (maxlen-oldlen)):
                    #print (len(helix["loop"].split(",")))
                    helix["loop"] = helix["loop"]+",0"
                #newlen = len(helix["loop"].split(","))
                #print (str(oldlen)+"  "+str(newlen))

            if len(helix["skip"].split(","))-maxlen != 0:
                # unterschiedlich lang
                oldlen = len(helix["skip"].split(","))
                for i in range(0, (maxlen-oldlen)):
                    helix["skip"] = helix["skip"]+",0"

            if len(helix["stap"].split("],["))-maxdnalen != 0:
                # unterschiedlich lang
                oldlen = len(helix["stap"].split("],["))
                #print (oldlen)
                for i in range(0, (maxdnalen-oldlen)):
                    helix["stap"] = helix["stap"]+",[-1,-1,-1,-1]"
                #newlen = len(helix["stap"].split("],["))
                #print (str(oldlen)+"  "+str(newlen))

            if len(helix["scaf"].split("],["))-maxdnalen != 0:
                # unterschiedlich lang
                oldlen = len(helix["scaf"].split("],["))
                for i in range(0, (maxdnalen-oldlen)):
                    helix["scaf"] = helix["scaf"]+",[-1,-1,-1,-1]"

            #print ("loop: "+str(len(helix["loop"].split(","))))
            #print (len(helix["skip"].split(",")))
            #print (len(helix["scaf"].split("],[")))
            #print (len(helix["stap"].split("],[")))

