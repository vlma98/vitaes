import CurriculumVitae, Models, datetime, time
import string, random, os
import subprocess, json
import timestring

def parse_date(str):
    print(str)
    return timestring.Date(str).date

def date_comparer(x):
    end_date=parse_date(x.end_date)
    start_date=parse_date(x.start_date)
    if end_date == None:
        end_date = datetime.date(2100, 10, 10)
    return (end_date, start_date)

def date_comparer_2(x):
    end_date=parse_date(x.end_date)
    start_date=parse_date(x.start_date)
    if end_date == None:
        end_date = datetime.date(2100, 10, 10)
    return (end_date, start_date)
    
class CvRenderBase:
    def render(cv: CurriculumVitae):
        raise NotImplementedError

class CvRenderTex(CvRenderBase):
    def render(cv: CurriculumVitae):
        texString = """\\documentclass[11pt,a4paper,sans]{moderncv} 
\\moderncvstyle{casual}
\\moderncvcolor{blue} 
\\usepackage{lipsum}
\\usepackage[scale=0.75]{geometry} 
"""
        if cv.header == None:
            return -1
        first_name = cv.header.name.split(' ')[0]
        family_name = ' '.join(cv.header.name.split(' ')[1:])
        texString += "\\firstname{" + first_name + "}\n"
        texString += "\\familyname{" + family_name + "}\n"
        texString += "\\title{Curriculum Vitae}\n"
        if cv.header.address != None:
            texString += "\\address{" + cv.header.address + "}{}\n"
        if cv.header.phone != None:
            texString += "\\phone{" + cv.header.phone + "}\n"
        if cv.header.email != None:
            texString += "\\email{" + cv.header.email + "}\n"
        if cv.header.homepage != None:
            texString += "\\homepage{" + cv.header.homepage + "}{" + cv.header.homepage + "} \n"
        elif cv.header.github != None:
            texString += "\\homepage{" + cv.header.github + "}{" + cv.header.github + "} \n"
        elif cv.header.linkedin != None:
            texString += "\\homepage{" + cv.header.linkedin + "}{" + cv.header.linkedin + "} \n"
        texString += "\\begin{document}\n\\makecvtitle\n"
        if Models.CvEducationalExperienceItem in cv.items:
            texString += "\\section{Education}\n"
            educationalExperience = cv.items[Models.CvEducationalExperienceItem]
            educationalExperience.sort(key = date_comparer, reverse = True)
            for elem in educationalExperience:
                texString += "\\cventry{" + parse_date(elem.start_date).strftime("%b/%y") + " "
                if elem.end_date == None:
                    texString += "now"
                elif parse_date(elem.start_date).strftime("%b/%y") != parse_date(elem.end_date).strftime("%b/%y"):
                    texString += parse_date(elem.end_date).strftime("%b/%y")
                texString += "}{" + elem.course + "}{" + elem.institution.name + "}{"
                if elem.location != None:
                    texString += str(elem.location)
                texString += "}{}{"
                if elem.description != None:
                    texString += elem.description
                texString += "}\n"
        if Models.CvWorkExperienceItem in cv.items:
            texString += "\\section{Work Experience}\n"
            workExperience = cv.items[Models.CvWorkExperienceItem]
            workExperience.sort(key = date_comparer, reverse = True)
            for elem in workExperience:
                texString += "\\cventry{" + parse_date(elem.start_date).strftime("%b/%y") + " "
                if elem.end_date == None:
                    texString += "now"
                else:
                    texString += parse_date(elem.end_date).strftime("%b/%y")
                texString += "}{" + elem.role + "}{" + elem.institution.name + "}{"
                if elem.location != None:
                    texString += str(elem.location)
                texString += "}{}{"
                if elem.description != None:
                    texString += elem.description
                texString += "}\n"
        if Models.CvAchievementProjectItem in cv.items:
            texString += "\\section{Achievements}\n"
            achievements = cv.items[Models.CvAchievementProjectItem]
            achievements.sort(key = date_comparer_2, reverse = True)
            for elem in achievements:
                texString += "\\cvitem{" + parse_date(elem.start_date).strftime("%d/%b/%Y") + "}{" + elem.name
                if elem.competitors > 0:
                    texString += "(Out of " + str(elem.competitors) + ")"
                texString += "}\n"
        if Models.CvImplementationProjectItem in cv.items:
            texString += "\\section{Projects}\n"
            projects = cv.items[Models.CvImplementationProjectItem]
            projects.sort(key = date_comparer_2, reverse = True)
            for elem in projects:
                start_date = parse_date(elem.start_date).strftime("%b/%Y")
                texString += "\\cventry{" + start_date
                if elem.end_date != None:
                    end_date = parse_date(elem.end_date).strftime("%b/%Y")
                    if end_date != start_date:
                        texString += " " + end_date
                texString += "}{" + elem.name + "}{" 
                if elem.language != None:
                    texString += elem.language
                texString += "}{}{}{"
                if elem.description != None:
                    texString += elem.description
                texString += "}\n"
        if Models.CvAcademicProjectItem in cv.items:
            texString += "\\section{Academic Experience}\n"
            projects = cv.items[Models.CvAcademicProjectItem]
            projects.sort(key = date_comparer_2, reverse = True)
            for elem in projects:
                start_date = parse_date(elem.start_date).strftime("%b/%Y")
                texString += "\\cventry{" + start_date
                if elem.end_date != None:
                    end_date = parse_date(elem.end_date).strftime("%b/%Y")
                    if end_date != start_date:
                        texString += " " + end_date
                texString += "}{" + elem.name + "}{" 
                if elem.institution != None:
                    texString += elem.institution.name
                texString += "}{}{}{"
                if elem.description != None:
                    texString += elem.description
                texString += "}\n"
        if Models.CvCourseProjectItem in cv.items:
            texString += "\\section{Courses}\n"
            courses = cv.items[Models.CvCourseProjectItem]
            courses.sort(key = date_comparer_2, reverse = True)
            for course in courses:
                if course.end_date != None:
                    texString += "\\cvitem{" + course.end_date.strftime("%b/%Y") + "}{" + course.name + "}\n"
                else:
                    texString += "\\cvitem{" + course.start_date.strftime("%b/%Y") + "}{" + course.name + "(In Progress)}\n"
        if Models.CvLanguageItem in cv.items:
            texString += "\\section{Languages}\n"
            languages = cv.items[Models.CvLanguageItem]
            for language in languages:
                texString += "\\cvitem{" + language.language + "}{" + language.level + "}\n"
        texString += "\\end{document}\n"
        return texString

class CvRenderTexToPdf(CvRenderBase):    
    def id_gen(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    def render(cv: CurriculumVitae, cvRender: CvRenderBase=CvRenderTex, baseFolder: str="cv_7", path: str=None):
        if path == None:
            path=CvRenderTexToPdf.id_gen()
        os.system("mkdir Output/" + path)
        if baseFolder != None:
            os.system("cp Templates/" + baseFolder + "/* Output/" + path + "/")
        os.system("touch Output/" + path + "/main.tex")
        cv = cvRender.render(cv)
        file = open("Output/" + path + "/main.tex","w") 
        file.write(cv)
        file.close()
        p = subprocess.Popen(["pdflatex","main.tex"], cwd="Output/" + path)
        p.wait()
        os.system("cp Output/" + path + "/main.pdf Output/" + path + ".pdf")
        os.system("rm -r Output/" + path + "/")
        return path

class CvRenderJsonRequest(CvRenderBase):
    def extract_item(x):
        dic = {}
        for varname in vars(x):
            var = eval('x.' + varname)
            if var is None or varname == "item_type":
                continue
            elif var.__class__.__name__[0:2] == "Cv":
                var = {var.__class__.__name__: CvRenderJsonRequest.extract_item(var)}
            elif var.__class__.__name__ == "date":
                var = var.strftime("%y-%m-%d")
            dic[varname] = var
        return dic
    def extract_list(raw_arr):
        arr = []
        for elem in raw_arr:
            arr.append(CvRenderJsonRequest.extract_item(elem))
        return arr
    def cv_to_dict(cv):
        dic = {}
        dic['CvHeaderItem'] = CvRenderJsonRequest.extract_item(cv.header)
        for item in cv.items:
            dic[item.__name__] = CvRenderJsonRequest.extract_list(cv.items[item])
        return dic
    def render(cv):
        return json.dumps(CvRenderJsonRequest.cv_to_dict(cv), indent=4)

    




        