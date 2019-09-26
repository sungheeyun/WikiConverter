import os
import sys
import datetime as dt


def timedelta_to_str(t):
    assert isinstance(t, dt.timedelta), t.__class__

    return (dt.datetime(1900, 1, 1, 0, 0, 0) + t).strftime("%H:%M")


class Wiki(object):

    # PUBLIC STATIC METHODS

    @staticmethod
    def unordered_list_bullet(level=1):
        assert isinstance(level, int), level.__class__
        return "*" * level


class Item(object):
    def __init__(self, fid):

        self.list_key = list()
        self.map_key_value = dict()
        self.time = dt.timedelta(minutes=0)

        self.__initialize(fid)

    def __initialize(self, fid):

        mode = "init"

        key = None
        buff = ""

        pos = fid.tell()

        for line in iter(fid.readline, ""):
            stripped_line = line.strip()

            if len(stripped_line) == 0:
                continue

            if mode == "main":
                if stripped_line == "}":
                    self.__put_key_value(key, buff)
                    break

                token_list = stripped_line.split()

                if token_list[0].startswith("@"):
                    self.__put_key_value(key, buff)
                    buff = ""

                    if token_list[0].endswith(":"):
                        key = token_list[0][1:-1]
                        buff = " ".join(token_list[1:])
                    else:
                        key = token_list[0][1:]
                        buff = ItemList(fid)
                else:
                    assert isinstance(buff, str), (buff, buff.__class__)
                    buff += " " + stripped_line

            elif mode == "init":
                if stripped_line != "{":
                    fid.seek(pos, 0)
                    break

                mode = "main"

            else:
                assert False, ("FATAL!!", mode)

    def __put_key_value(self, key, buff):

        if key is None:
            return

        self.list_key.append(key)
        self.map_key_value[key] = buff

        if key == "time":
            token_list = buff.split()
            assert token_list[1] == "minutes" or token_list[1] == "minute", buff
            self.time = dt.timedelta(minutes=int(token_list[0]))

        if isinstance(buff, ItemList):
            self.time = buff.time

    def is_empty(self):
        return len(self.map_key_value) == 0

    def write_to_output(self, fid, level):
        assert isinstance(level, int), level.__class__

        str_bullet = Wiki.unordered_list_bullet(level)

        method = 1
        if method == 1:
            fid.write("%s %s (%s)\n" % (str_bullet, self.map_key_value["title"], timedelta_to_str(self.time)))
        elif method == 2:
            fid.write(
                "%s %s (%s): %s\n"
                % (str_bullet, self.map_key_value["title"], timedelta_to_str(self.time), self.map_key_value["summary"])
            )
        elif method == 3:
            fid.write("%s %s: %s\n" % (str_bullet, self.map_key_value["title"], self.map_key_value["summary"]))
        else:
            assert False, method


class ItemList(object):
    def __init__(self, fid):
        self.listItem = list()
        self.time = dt.timedelta(minutes=0)

        self.__initialize(fid)

    def __initialize(self, fid):
        while True:
            item = Item(fid)
            if item.is_empty():
                break
            self.listItem.append(item)
            self.time += item.time

    def __iter__(self):
        return self.listItem.__iter__()


class CourseParser(object):
    def __init__(self, fn):

        self.fn = fn
        self.itemList = None

        self.__parse()

    def __parse(self):

        print("parsing %s ..." % self.fn)
        fid = open(self.fn)
        self.itemList = ItemList(fid)
        fid.close()

    def __get_out_filename(self):

        return "%s.out" % os.path.splitext(self.fn)[0]

    def write_to_output(self, level):

        outfn = self.__get_out_filename()

        print("start writing output to %s ..." % outfn)

        fid = open(outfn, "w")

        for item in self.itemList:
            item.write_to_output(fid, level)

        fid.close()


if __name__ == "__main__":

    print(sys.argv)

    for fn in sys.argv[1:]:
        cp = CourseParser(fn)
        cp.write_to_output(level=3)
