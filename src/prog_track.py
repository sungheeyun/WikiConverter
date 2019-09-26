#!/Users/sunyun/anaconda3/bin/python

import sys
import time
import utils

sys.path.append("/Users/sunyun/software/python")


class Member(object):

    DateFormat = "%m/%d/%y"

    # CONSTRUCTOR

    def __init__(self, firstName, lastName):
        assert isinstance(firstName, str), firstName.__class__
        assert isinstance(lastName, str), lastName.__class__

        self.firstName = firstName
        self.lastName = lastName
        self.platDatePNoteDict = dict()

    # GETTERS

    def get_data_set(self):

        dateSet = set()
        for platform, date in self.platDatePNoteDict:
            dateSet.add(date)

        return dateSet

    def get_fullname(self):
        return "%s %s" % (self.firstName, self.lastName)

    # PUTTERS

    def add_note(self, platform, date, note):
        assert isinstance(platform, str), platform.__class__
        assert isinstance(date, str), date.__class__
        assert isinstance(note, str), note.__class__

        assert platform == "Android" or platform == "iOS", platform

        date = time.strptime(date, Member.DateFormat)

        self.platDatePNoteDict[(platform, date)] = note

    def add_row_to_wiki_table(self, newWikiTable, dateList, platformL=["Android", "iOS"], nameFirst=True):
        self._add_row_to_wiki_table(newWikiTable, dateList, platformL, nameFirst)

    def _add_row_to_wiki_table(self, newWikiTable, dateList, platformL, nameFirst):
        assert isinstance(newWikiTable, utils.NewWikiTable), newWikiTable.__class__
        assert isinstance(dateList, list), dateList.__class__
        assert isinstance(platformL, list), platformL.__class__
        assert isinstance(nameFirst, bool), nameFirst.__class__

        res = dict()

        # res['Android'] = [ '' ] * len(dateList)
        # res['iOS'] = [ '' ] * len(dateList)
        for platform in platformL:
            res[platform] = [""] * len(dateList)

        for key, note in self.platDatePNoteDict.items():
            platform, date = key

            if platform in platformL:
                continue

            found = False
            for idx, dt in enumerate(dateList):
                if date == dt:
                    res[platform][idx] = note
                    found = True
                    break

            assert found, found

        # newWikiTable.addRow( [ self.get_fullname(), 'Android' ] + res['Android'] )
        # newWikiTable.addRow( [ self.get_fullname(), 'iOS' ] + res['iOS'] )
        for platform in platformL:
            if nameFirst:
                fl = [self.get_fullname(), platform]
            else:
                fl = [platform, self.get_fullname()]

            newWikiTable.addRow(fl + res[platform])


class Team(object):
    @staticmethod
    def date_to_str(date):
        assert isinstance(date, time.struct_time), date.__class__
        return time.strftime("%b %d", date)

    # CONSTRUCTOR

    def __init__(self, teamName):
        assert isinstance(teamName, str), teamName.__class__

        self.teamName = teamName
        self.nameMemberDict = dict()

    # GETTERS

    def get_date_list(self):

        dateSet = set()
        for key, member in self.nameMemberDict.items():
            dateSet.update(member.get_data_set())

        dateList = list(dateSet)
        dateList.sort(reverse=True)

        return dateList

    def get_member_list(self):

        memberList = list()
        for firstName, member in self.nameMemberDict.items():
            memberList.append(member)

        memberList.sort(key=lambda member: member.firstName)

        return memberList

    # PUTTERS

    def add_member(self, firstName, lastName):
        assert firstName not in self.nameMemberDict, (firstName, list(self.nameMemberDict.keys()))

        self.nameMemberDict[firstName] = Member(firstName, lastName)

    def add_data(self, firstName, platform, date, note):
        assert isinstance(firstName, str), firstName.__class__
        assert isinstance(platform, str), platform.__class__
        assert isinstance(date, str), date.__class__
        assert isinstance(note, str), note.__class__

        self.nameMemberDict[firstName].add_note(platform, date, note)

    # WRITERS

    def write_to_wiki_by_name(self, fn):

        memberList = self.get_member_list()
        dateList = self.get_date_list()

        newWikiTable = utils.NewWikiTable([100] * 2 + [150] * len(dateList), "")

        newWikiTable.addRow(["Engineer", "Platform"] + [Team.date_to_str(date) for date in dateList])

        for member in memberList:
            member.add_row_to_wiki_table(newWikiTable, dateList)

        spanD = dict()
        spanD[("odd", 0)] = (2, 1)
        spanD["exception"] = (0, "last")

        boldD = dict()
        boldD[0] = True

        print("writing to %s" % fn)
        with open(fn, "w") as fid:
            newWikiTable.write(fid, spanD=spanD, boldD=boldD)

    def write_to_wiki_by_platform(self, fn):

        memberList = self.get_member_list()
        dateList = self.get_date_list()

        newWikiTable = utils.NewWikiTable([100] * 2 + [150] * len(dateList), "")

        newWikiTable.addRow(["Platform", "Engineer"] + [Team.date_to_str(date) for date in dateList])

        for member in memberList:
            member.add_row_to_wiki_table(newWikiTable, dateList, ["Android"], False)

        for member in memberList:
            member.add_row_to_wiki_table(newWikiTable, dateList, ["iOS"], False)

        sizeMemberList = len(memberList)
        spanD = dict()
        spanD[(1, 0)] = (sizeMemberList, 1)
        spanD[(1 + sizeMemberList, 0)] = (sizeMemberList, 1)

        boldD = dict()
        boldD[0] = True

        print("writing to %s" % fn)
        with open(fn, "w") as fid:
            newWikiTable.write(fid, spanD=spanD, boldD=boldD)


if __name__ == "__main__":

    team = Team("MRE")

    team.add_member("Caroline", "McQuatt")
    team.add_member("Dmitry", "Serpakov")
    team.add_member("James", "Roland")
    team.add_member("Jan", "Duzinkiwicz")
    team.add_member("Lewis", "Elliot")
    team.add_member("Mirco", "Padovan")
    team.add_member("Mohamed", "Karnel")
    team.add_member("Sherif", "Elian")
    team.add_member("Sridhar", "Sundarraman")
    team.add_member("Sunghee", "Yun")

    team.add_data("Caroline", "Android", "11/2/17", "20% (3/5 modules)")
    team.add_data("Caroline", "Android", "11/16/17", "33%")
    team.add_data("Caroline", "Android", "1/5/18", "50%")
    team.add_data("Caroline", "Android", "1/18/18", "ready for exam this week")
    team.add_data("Caroline", "Android", "2/1/18", "ready for exam")
    team.add_data("Caroline", "Android", "2/19/18", "ready for exam")
    team.add_data("Caroline", "Android", "3/29/18", "ready for exam")
    team.add_data("Caroline", "Android", "4/12/18", "want to do Sprint (w/o certificate)")
    team.add_data("Caroline", "Android", "4/27/18", "starting Android Sprint on May 7th")
    team.add_data("Caroline", "Android", "5/10/18", "started Android Sprint")

    team.add_data("Dmitry", "Android", "11/2/17", "0%")
    team.add_data("Dmitry", "Android", "11/16/17", "0%")
    team.add_data("Dmitry", "Android", "1/5/18", "0%")
    team.add_data("Dmitry", "Android", "1/18/18", "planning to start this week")
    team.add_data("Dmitry", "iOS", "2/1/18", "40%")
    team.add_data("Dmitry", "iOS", "2/19/18", "40%")
    team.add_data("Dmitry", "iOS", "3/29/18", "40%")
    team.add_data("Dmitry", "iOS", "4/12/18", "40%")
    team.add_data("Dmitry", "iOS", "4/27/18", "40%")

    team.add_data("James", "iOS", "11/2/17", "0%")
    team.add_data("James", "iOS", "11/16/17", "0%")
    team.add_data("James", "iOS", "1/5/18", "0%")
    team.add_data("James", "iOS", "1/18/18", "0%")
    team.add_data("James", "iOS", "2/1/18", "0%")
    team.add_data("James", "iOS", "2/19/18", "0%")
    team.add_data("James", "iOS", "3/29/18", "0%")
    team.add_data("James", "iOS", "4/27/18", "0%")

    team.add_data("Jan", "Android", "11/2/17", "1.437%")
    team.add_data("Jan", "Android", "11/16/17", "1.437%")
    team.add_data("Jan", "Android", "1/5/18", "1.437%")
    team.add_data("Jan", "Android", "2/1/18", "on lesson 1.4")
    team.add_data("Jan", "Android", "2/19/18", "on lesson 1.4")
    team.add_data("Jan", "Android", "3/29/18", "on lesson 1.4")

    team.add_data("Lewis", "iOS", "11/2/17", "0%")
    team.add_data("Lewis", "iOS", "11/16/17", "0%")
    team.add_data("Lewis", "iOS", "2/1/18", "20%")
    team.add_data("Lewis", "iOS", "2/19/18", "20%")
    team.add_data("Lewis", "iOS", "3/29/18", "20%")
    team.add_data("Lewis", "iOS", "4/12/18", "20%")
    team.add_data("Lewis", "iOS", "4/27/18", "20%")

    team.add_data("Mirco", "Android", "11/2/17", "0%")
    team.add_data("Mirco", "Android", "11/16/17", "25%")
    team.add_data("Mirco", "Android", "1/5/18", "100% - ready for test")
    team.add_data("Mirco", "Android", "1/18/18", "planning on taking test next week")
    team.add_data("Mirco", "Android", "2/1/18", "100% - finished taking test")
    team.add_data("Mirco", "Android", "2/19/18", "finished Sprint on Android!")
    team.add_data("Mirco", "iOS", "3/29/18", "20%")
    team.add_data("Mirco", "iOS", "4/12/18", "20%")
    team.add_data("Mirco", "iOS", "4/27/18", "30%")

    team.add_data("Mohamed", "Android", "11/2/17", "20%")
    team.add_data("Mohamed", "Android", "11/16/17", "30-35%")
    team.add_data("Mohamed", "Android", "1/5/18", "50%")
    team.add_data("Mohamed", "Android", "1/18/18", "finished pdf.  practice before the exam")
    team.add_data("Mohamed", "Android", "2/1/18", "100% - planning to take certificate in Q1")
    team.add_data("Mohamed", "Android", "3/29/18", "Gotten certificate and doing Sprint")

    team.add_data("Sherif", "iOS", "11/2/17", "77.77%")
    team.add_data("Sherif", "iOS", "11/16/17", "95%")
    team.add_data("Sherif", "iOS", "1/5/18", "100% - ready for sprint (Feb)")
    team.add_data("Sherif", "iOS", "2/1/18", "100% - planning to start sprint on Feb. 5th")
    team.add_data("Sherif", "iOS", "2/19/18", "finished Sprint on iOS!")

    team.add_data("Sridhar", "Android", "11/2/17", "50% planning on taking test 11/31")
    team.add_data("Sridhar", "Android", "11/16/17", "50%")
    team.add_data("Sridhar", "Android", "1/5/18", "100% - ready for sprint (March)")
    team.add_data("Sridhar", "Android", "2/1/18", "100% - ready for sprint (March)")
    team.add_data("Sridhar", "Android", "3/29/18", "starting Sprint on Android")
    team.add_data("Sridhar", "Android", "4/27/18", "finished Sprint on Android")

    team.add_data("Sunghee", "Android", "11/2/17", "0%")
    team.add_data("Sunghee", "Android", "11/16/17", "0%")
    team.add_data("Sunghee", "Android", "1/5/18", "0%")
    team.add_data("Sunghee", "Android", "1/18/18", "5%")
    team.add_data("Sunghee", "Android", "2/1/18", "5%")
    team.add_data("Sunghee", "Android", "2/19/18", "5%")
    team.add_data("Sunghee", "Android", "3/29/18", "5%")
    team.add_data("Sunghee", "Android", "4/12/18", "5%")
    team.add_data("Sunghee", "Android", "4/27/18", "5%")

    team.add_data("Mirco", "iOS", "7/6/18", "50%")

    team.write_to_wiki_by_name("mt_by_name.wtb")
#    team.write_to_wiki_by_platform("mt_by_platform.wtb")
