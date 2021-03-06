import datetime, time
import shutil
import string, random, os
import subprocess, json
import timestring
import traceback
from babel.dates import format_datetime
from Cheetah.Template import Template
from Logger import log_step

def id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def date_comparer(x):
    end_date=x.end_date
    start_date=x.start_date
    if end_date == None:
        end_date = datetime.datetime(2100, 10, 10, 1, 1, 1)
    return (end_date, start_date)

def date_comparer_2(x):
    end_date = ""
    start_date = x['start_date']
    if 'end_date' in x:
        end_date = x['end_date']
    else:
        end_date = datetime.datetime(2100, 10, 10, 1, 1, 1)
    return (end_date, start_date)
    
class CvRenderBase:
    def render(cv):
        raise NotImplementedError

class CvRenderToPdf(CvRenderBase):   
    def render(cv, cvRender: CvRenderBase, baseFolder: str, path: str=None, command: str="pdflatex", params={}, resources={}):
        if path == None:
            path=id_gen()
        os.system("mkdir Output/" + path)
        if baseFolder != None:
            os.system("cp -r Templates/" + baseFolder + "/* Output/" + path + "/")
        cvString = cvRender.render(cv, params=params, baseFolder=baseFolder, resources=resources)
        log_step(cv.header.email, cv.cv_hash, "TEX_FULLY_COMPILED")
        os.system("touch Output/" + path + "/main.tex")
        file = open("Output/" + path + "/main.tex","w", encoding="utf-8") 
        file.write(cvString)
        file.close()
        p = subprocess.Popen([command,"main.tex"], cwd="Output/" + path, stdout=subprocess.PIPE)
        p.wait()
        p_output = p.stdout.read().decode("utf-8", errors='ignore')
        log_step(cv.header.email, cv.cv_hash, "LATEX_CMD_EXECUTED", p_output)
        os.system("cp Output/" + path + "/main.pdf Output/" + path + ".pdf")
        os.system("rm -r Output/" + path + "/")
        return path

class CvRenderToTex(CvRenderBase):
    def render(cv, cvRender: CvRenderBase, baseFolder: str, path: str=None, params={}, resources={}):
        if path == None:
            path=id_gen()
        os.system("mkdir Output/" + path)
        if baseFolder != None:
            os.system("cp -r Templates/" + baseFolder + "/* Output/" + path + "/")
        cvString = cvRender.render(cv, params=params, baseFolder=baseFolder, resources=resources)
        log_step(cv.header.email, cv.cv_hash, "TEX_FULLY_COMPILED")
        os.system("touch Output/" + path + "/main.tex")
        file = open("Output/" + path + "/main.tex","w", encoding="utf-8") 
        file.write(cvString)
        file.close()
        shutil.make_archive("Output/" + path, "zip", "Output/" + path + "/")
        os.system("rm -r Output/" + path + "/")
        return path

class CvRenderToJson(CvRenderBase):
    def render(cv, cvRender: CvRenderBase=None, baseFolder: str=None, path: str=None, command: str="pdflatex", params={}, resources={}):
        cv_file_content = json.dumps(cv, indent=None, separators=(',', ':'))
        file = open("Output/" + path + ".json","w", encoding="utf-8")
        file.write(cv_file_content)
        file.close()
        log_step(cv["header"]["email"], path, "JSON_FILE_RENDERED", cv_file_content)
        return path
import sys
def text_clean(text):
    if text == None:
        return text
    text=str(text)
    extra = {
        "\\{": "{",
        "\\}": "}",
    }
    accents = {
        "\\`a": "à",
        "\\'a": "á",
        "\\~a": "ã",
        "\\^a": "â",
        '\\"a': "ä",
        "\\'e": "é",
        "\\^e": "ê",
        "\\`e": "è",
        "\\^i": "î",
        '\\"i': "ï",
        "\\'i": "í",
        "\\'o": "ó",
        "\\~o": "õ",
        "\\^o": "ô",
        '\\"o': "ö",
        "\\'u": "ú",
        '\\"u': "ü",
        "\\`A": "À",
        "\\'A": "Á",
        "\\~A": "Ã",
        "\\^A": "Â",
        '\\"A': "Ä",
        "\\'E": "É",
        "\\^E": "Ê",
        "\\`E": "È",
        "\\^I": "Î",
        '\\"I': "Ï",
        "\\'I": "Í",
        "\\'O": "Ó",
        "\\~O": "Õ",
        "\\^O": "Ô",
        '\\"O': "Ö",
        "\\'U": "Ú",
        '\\"U': "Ü",
        "\\c{c}": "ç",
        "\\c{C}": "Ç",
        "\\#": "#",
        "\\%": "%",
        "\\_": "_",
        "\\&": "&",
    }
    for x in extra.keys():
        text = text.replace(extra[x], x)
    for x in accents.keys():
        text = text.replace(accents[x], x)
    return text
class CvRenderCheetahTemplate(CvRenderBase):
    def add_dates(itemDict, key, baseDate: datetime):
        baseDate = timestring.Date(baseDate).date
        itemDict[key] = baseDate
        return itemDict
    def extract_item(cv, key):
        ret = []
        if key in cv.__dict__:
            for item in cv.__dict__[key]:
                itemDict = {}
                for var in vars(item):
                    if eval("item." + var) == None:
                        continue
                    if var == "item_type":
                        continue
                    if var == "location":
                        itemDict["country"] = text_clean(eval("item." + var).country)
                        itemDict["city"] = text_clean(eval("item." + var).city)
                        itemDict["state"] = text_clean(eval("item." + var).state)
                    elif var == "institution": 
                        itemDict[var] = text_clean(item.institution.name)
                    elif var[-4:] == "date":
                        itemDict = CvRenderCheetahTemplate.add_dates(itemDict, var, eval("item." + var))
                    elif type(eval("item." + var)) == str:
                        itemDict[var] = text_clean(eval("item." + var))
                    else:
                        itemDict[var] = text_clean(eval("item." + var))
                ret.append(itemDict)
        if ret != [] and 'start_date' in ret[0]:
            ret.sort(key = date_comparer_2, reverse = True)
        return ret
    def extract_skills(cv):
        skills = []
        aggSkills = {}
        if 'skill' in cv.__dict__ and cv.__dict__['skill'] != []:
            for skill in cv.__dict__['skill']:
                cleanName = text_clean(skill.skill_name)
                cleanLevel = text_clean(skill.skill_level)
                cleanType = text_clean(skill.skill_type)
                skills.append({
                    'name': cleanName,
                    'level': cleanLevel,
                    'type': cleanType,
                })
                if cleanType not in aggSkills:
                    aggSkills[cleanType] = []
                aggSkills[cleanType].append({
                    'name': cleanName,
                    'level': cleanLevel,
                })
        return {
            'plain': skills,
            'aggregated': aggSkills,
        }

    def break_into_items(description, header=None, bottom=None, itemPrefix="", itemSuffix="", itemSpacing=None):
        lines = description.split('\n')
        lines = list(filter(lambda line: len(line.strip()) > 0, lines))
        itemOnTop = [itemSpacing] if len(lines) > 0 and len(lines[0]) > 1 and lines[0][0] == '*' else []
        itemOnBottom = [itemSpacing] if len(lines) > 0 and len(lines[-1]) > 1 and lines[-1][0] == '*' else []
        lines.append('')
        depth = 0
        retLines = []
        for line in lines:
            lineDepth = 0
            while len(line) > lineDepth and line[lineDepth] == '*':
                lineDepth += 1
            while depth < lineDepth:
                depth += 1
                if header != None:
                    retLines.append(header)
            while depth > lineDepth:
                depth -= 1
                if bottom != None:
                    retLines.append(bottom)
            if depth > 0:
                retLines.append(itemPrefix + line[depth:] + itemSuffix)
            else: 
                retLines.append(line)
        if itemSpacing is not None:
            retLines = itemOnTop + retLines[:-1] + itemOnBottom + [retLines[-1]]
        return '\n'.join(retLines)

    def format_skill(skill_data):
        formated_skills = []
        for skill in skill_data:
            if 'level' in skill and skill['level'] is not None:
                formated_skills.append(skill['name'] + ' (' + skill['level'] + ')')
            else:
                formated_skills.append(skill['name'])
        return ', '.join(formated_skills)


    def render(cv, baseFolder: str, params={}, resources={}):
        file = open("Templates/" + baseFolder + "/main.tex", "r", encoding="utf-8")
        templateString = file.read()
        file.close()
        cvDict = {}
        headerVars = ["name", "address", "github", "linkedin", "email", "phone", "birthday", "homepage"]
        cvDict["firstname"] = text_clean(cv.header.name.split(' ')[0])
        cvDict["surname"] = text_clean(' '.join(cv.header.name.split(' ')[1:]))
        cvDict["lastname"] = text_clean(cv.header.name.split(' ')[-1])
        for var in headerVars:
            cvDict[var] = text_clean(eval("cv.header." + var))
        if cv.header.birthday != None:
            cvDict["birthday"] = timestring.Date(cv.header.birthday).date
        cvDict["work_array"] = CvRenderCheetahTemplate.extract_item(cv, 'work')
        cvDict["education_array"] = CvRenderCheetahTemplate.extract_item(cv, 'education')
        cvDict["academic_array"] = CvRenderCheetahTemplate.extract_item(cv, 'academic')
        cvDict["language_array"] = CvRenderCheetahTemplate.extract_item(cv, 'language')
        cvDict["project_array"] = CvRenderCheetahTemplate.extract_item(cv, 'project')
        cvDict["achievement_array"] = CvRenderCheetahTemplate.extract_item(cv, 'achievement')
        cvDict["skill_dict"] = CvRenderCheetahTemplate.extract_skills(cv)
        cvDict["params"] = params
        cvDict["break_into_items"] = CvRenderCheetahTemplate.break_into_items
        cvDict["format_skill"] = CvRenderCheetahTemplate.format_skill
        cvDict["format_datetime"] = format_datetime
        for key in resources:
          resources[key] = text_clean(resources[key])
        cvDict["resources"] = resources
        log_step(cv.header.email, cv.cv_hash, "GENERATING_TEX_FROM_CHEETAH")
        template = Template(templateString, cvDict)
        log_step(cv.header.email, cv.cv_hash, "GENERATED_TEX_FROM_CHEETAH")
        return str(template)
        