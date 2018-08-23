from datetime import date


class CvLocation:
    def __init__(self, country: str, state: str = None, city: str = None):
        self.country = country
        self.state = state
        self.city = city

    def __str__(self):
        ans = self.country
        if self.state != None:
            ans += ', ' + self.state
        if self.city != None:
            ans += ', ' + self.city
        return ans


class CvInstitution:
    def __init__(self, name: str, location: CvLocation = None):
        self.name = name
        self.location = location


class CvItem:
    def __init__(self):
        self.item_type = self.__class__.__name__

    def __str__(self):
        x = "{ "
        for var in vars(self):
            if getattr(self, var) is not None:
                var_str = str(getattr(self, var))
                x += str(var) + ": " + var_str + ", "
        x += "}"
        return x


class CvLanguageItem(CvItem):
    def __init__(self, language: str, level: str = None):
        CvItem.__init__(self)
        self.language = language
        self.level = level


class CvExperienceItem(CvItem):
    def __init__(self,
                 institution: CvInstitution,
                 start_date: date,
                 location: CvLocation = None,
                 end_date: date = None,
                 description: str = None):
        CvItem.__init__(self)
        self.institution = institution
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description


class CvWorkExperienceItem(CvExperienceItem):
    def __init__(self, 
                 institution: CvInstitution,
                 start_date: date,
                 location: CvLocation = None,
                 end_date: date = None,
                 description: str = None,
                 role: str = None,
                 ):
        CvExperienceItem.__init__(self, institution=institution, location=location, start_date=start_date, end_date=end_date, description=description)
        self.role = role


class CvEducationalExperienceItem(CvExperienceItem):
    def __init__(self,
                 institution: CvInstitution,
                 start_date: date,
                 course: str,
                 location: CvLocation = None,
                 end_date: date = None,
                 description: str = None,
                 teacher:str = None,
                 ):       
        CvExperienceItem.__init__(self, institution=institution, location=location, start_date=start_date, end_date=end_date, description=description)
        self.course = course


class CvProjectItem(CvItem):
    def __init__(self,
                 name: str,
                 description: str = None,
                 location: CvLocation = None,
                 start_date: date = None,
                 end_date: date = None
                 ):
        CvItem.__init__(self)
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.location = location


class CvImplementationProjectItem(CvProjectItem):
    def __init__(self,
                 name: str,
                 description: str = None,
                 location: CvLocation = None,
                 language: str = None,
                 repository_link: str = None,
                 start_date: date = None,
                 end_date: date = None
                 ):
        CvProjectItem.__init__(self, name=name, description=description, location=location, start_date=start_date, end_date=end_date)
        self.language = language
        self.repository_link = repository_link


class CvAcademicProjectItem(CvProjectItem):
    def __init__(self,
                 name: str,
                 description: str,
                 institution: CvInstitution = None,
                 location: CvLocation = None,
                 article_link: str = None,
                 start_date: date = None,
                 end_date: date = None
                 ):
        CvProjectItem.__init__(self, name=name, description=description, location=location, start_date=start_date, end_date=end_date)
        self.article_link = article_link
        self.institution = institution


class CvCourseProjectItem(CvProjectItem):
    # Instable still
    def __init__(self,
                 name: str,
                 start_date: date,
                 description: str = None,
                 location: CvLocation = None,
                 institution: CvInstitution = None,
                 certification_link: str = None,
                 course_link: str = None,
                 end_date: date = None
                 ):
        CvProjectItem.__init__(self, name=name, description=description, location=location, start_date=start_date, end_date=end_date)
        self.certification_link = certification_link
        self.course_link = course_link


class CvAchievementProjectItem(CvProjectItem):
    def __init__(self,
                 name: str,
                 start_date: date,
                 description: str = None,
                 institution: CvInstitution = None,
                 location: CvLocation = None,
                 place: str = '',
                 competitors: int = 0,
                 end_date: date = None,
                 certification_link: str = None
                 ):
        CvProjectItem.__init__(self, name=name, description=description, location=location, start_date=start_date, end_date=end_date)
        self.place = place
        self.competitors = int(competitors)
        self.certification_link = certification_link


class CvHeaderItem(CvItem):
    def __init__(self,
                 name: str,
                 email: str = None,
                 phone: str = None,
                 linkedin: str = None,
                 github: str = None,
                 address: str = None,
                 birthday: date = None,
                 homepage: str = None
                 ):
        CvItem.__init__(self)
        assert(name is not None)
        self.name = name
        self.email = email
        self.phone = phone
        self.linkedin = linkedin
        self.github = github
        self.address = address
        self.birthday = birthday
        self.homepage = homepage
