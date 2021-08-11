from enum import Enum


class Semester(Enum):
    """
    Semester enum. There are 8 semesters max per major.
    """
    __order__ = 'SEM1 SEM2 SEM3 SEM4 SEM5 SEM6 SEM7 SEM8'
    SEM1 = 0
    SEM2 = 1
    SEM3 = 2
    SEM4 = 3
    SEM5 = 4
    SEM6 = 5
    SEM7 = 6
    SEM8 = 7


class CourseType(Enum):
    """
    Course type enum, there are 3 courses type - hova, bhirat hova and bhira
    """
    HOVA = 1
    BHIRAT_HOVA = 2
    BHIRA = 3


class CollisionTypes(Enum):
    """
    Type of possible collisions ("hint-nag-shu-yot") between courses, and their penalty
    """

    # TODO set more realistic penalties
    HOVA_HOVA = 10
    HOVA_BHOVA = 8
    HOVA_BHIRA = 8
    BHOVA_BHOVA = 3
    BHOVA_BHIRA = 2
    BHIRA_BHIRA = 2
    NONE = 0


class Major:
    """
    Class representing a major ("maslul"). A major object will hold all of the schedule of a major ("Maslul")
    """

    def __init__(self, major_name: str, major_num: int):
        self.major_name = major_name
        self.major_num = major_num

        self._courses_in_sem = {Semester.SEM1: {},
                                Semester.SEM2: {},
                                Semester.SEM3: {},
                                Semester.SEM4: {},
                                Semester.SEM5: {},
                                Semester.SEM6: {},
                                Semester.SEM7: {},
                                Semester.SEM8: {}}

    def add_course(self, course, type: CourseType, sem: Semester):
        self._courses_in_sem[sem][course] = type

    def get_sem_courses(self, sem: Semester):
        return self._courses_in_sem[sem]

    def __eq__(self, other):
        return self.major_name == other.major_name and self.major_num == other.major_num

    def __hash__(self):
        return hash(self.major_name)

    def __repr__(self):
        return str(self.major_num)


class Course:
    """
    Class representing a course. The object of the class will also contain the majors ("maslulim") containing
    the course, including their type and sem in the maslul.
    """

    def __init__(self, course_num, course_name):
        self.number = course_num
        self.name = course_name  # TODO do we have it...?
        self._majors_dict = {}

    def add_major(self, major: Major, sem: Semester, type: CourseType):
        self._majors_dict[major] = (sem, type)  # TODO a course can be bhira / hovat bhira in two different semesters...

    def get_common_majors(self, other):
        c1_majors = set(self._majors_dict.keys())
        c2_majors = set(other._majors_dict.keys())
        return c1_majors.intersection(c2_majors)

    def get_overlap_type_for_major(self, other, major):
        if self._majors_dict[major][0] != other._majors_dict[major][0]:
            return CollisionTypes.NONE

        this_type = self._majors_dict[major][1]
        other_type = other._majors_dict[major][1]

        if this_type == other_type:
            if this_type == CourseType.BHIRA:
                return CollisionTypes.BHIRA_BHIRA
            if this_type == CourseType.HOVA:
                return CollisionTypes.HOVA_HOVA
            if this_type == CourseType.BHIRAT_HOVA:
                return CollisionTypes.BHOVA_BHOVA

        if (this_type == CourseType.BHIRA and other_type == CourseType.HOVA) or \
            (other_type == CourseType.BHIRA and this_type == CourseType.HOVA):
            return CollisionTypes.HOVA_BHIRA

        if (this_type == CourseType.BHIRAT_HOVA and other_type == CourseType.HOVA) or \
            (other_type == CourseType.BHIRAT_HOVA and this_type == CourseType.HOVA):
            return CollisionTypes.HOVA_BHOVA

        if (this_type == CourseType.BHIRA and other_type == CourseType.BHIRAT_HOVA) or \
            (other_type == CourseType.BHIRA and this_type == CourseType.BHIRAT_HOVA):
            return CollisionTypes.BHOVA_BHIRA

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def __repr__(self):
        return self.number









