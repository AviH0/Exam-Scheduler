from enum import Enum

MIN_DAYS_FROM_A_TO_B = 21


class YearSemester(Enum):
    SEM_A = 1
    SEM_B = 2


class MajorSemester(Enum):
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

    @staticmethod
    def get_year_semester(sem):
        if sem.value % 2 == 0:
            return YearSemester.SEM_A
        return YearSemester.SEM_B


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

    HOVA_HOVA = 10000
    HOVA_BHOVA = 100
    HOVA_BHIRA = 50
    BHOVA_BHOVA = 100
    BHOVA_BHIRA = 10
    BHIRA_BHIRA = 5
    NONE = 0

    @staticmethod
    def get_col_type(t1: CourseType, t2: CourseType):
        if t1 == CourseType.HOVA and t2 == CourseType.HOVA:
            return CollisionTypes.HOVA_HOVA

        if t1 == CourseType.BHIRAT_HOVA and t2 == CourseType.BHIRAT_HOVA:
            return CollisionTypes.BHOVA_BHOVA

        if t1 == CourseType.BHIRA and t2 == CourseType.BHIRA:
            return CollisionTypes.BHIRA_BHIRA

        if (t1 == CourseType.HOVA and t2 == CourseType.BHIRAT_HOVA) or \
                (t2 == CourseType.HOVA and t1 == CourseType.BHIRAT_HOVA):
            return CollisionTypes.HOVA_BHOVA

        if (t1 == CourseType.BHIRA and t2 == CourseType.BHIRAT_HOVA) or \
                (t2 == CourseType.BHIRA and t1 == CourseType.BHIRAT_HOVA):
            return CollisionTypes.BHOVA_BHIRA

        if (t1 == CourseType.HOVA and t2 == CourseType.BHIRA) or \
                (t2 == CourseType.HOVA and t1 == CourseType.BHIRA):
            return CollisionTypes.HOVA_BHIRA


class Major:
    """
    Class representing a major ("maslul"). A major object will hold all of the schedule of a major ("Maslul")
    """

    def __init__(self, major_name: str):
        self.major_name = major_name

        self._courses_in_sem = {MajorSemester.SEM1: {},
                                MajorSemester.SEM2: {},
                                MajorSemester.SEM3: {},
                                MajorSemester.SEM4: {},
                                MajorSemester.SEM5: {},
                                MajorSemester.SEM6: {},
                                MajorSemester.SEM7: {},
                                MajorSemester.SEM8: {}}

    def add_course(self, course, course_type: CourseType, sem: MajorSemester):
        self._courses_in_sem[sem][course] = course_type

    def get_sem_courses(self, sem: MajorSemester):
        return self._courses_in_sem[sem]

    def __eq__(self, other):
        return self.major_name == other.major_name

    def __hash__(self):
        return hash(self.major_name)

    def __repr__(self):
        return str(self.major_name)


class Course:
    """
    Class representing a course. The object of the class will also contain the majors ("maslulim") containing
    the course, including their type and sem in the maslul.
    """

    def __init__(self, course_num, course_name):
        self.number = course_num
        self.name = course_name
        self._majors_dict = {}
        self.__hash = hash(course_num)

    def add_major(self, major: Major, sem: MajorSemester, course_type: CourseType):
        if major in self._majors_dict:
            self._majors_dict[major].append((sem, course_type))
        else:
            self._majors_dict[major] = [(sem, course_type)]

    def get_majors(self):
        return self._majors_dict

    def __eq__(self, other):
        return self.number == other.number

    def __cmp__(self, other):
        if self.number < other.number:
            return -1
        if self.number == other.number:
            return 0
        return 1

    def __lt__(self, other):
        return self.number < other.number

    def __gt__(self, other):
        return self.number > other.number

    def __hash__(self):
        return self.__hash

    def __repr__(self):
        return self.number
