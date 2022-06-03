import os
import subprocess
import shutil
import requests
import json
from os import listdir
from os.path import isfile, join
import time


def get_indiv_text(file):
    with open(file, 'r', encoding="utf-8") as f:
        text = f.read().replace('\n', ' ')
    return text


def termitup():
    url = 'https://termitup.oeg.fi.upm.es/extract_terminology'
    # path_ = "C:/Users/carlo/Documents/med-terminology/Files_SPACCC/"
    path_ = "./data/Files_SPACCC"
    # file_ = "S1135-76062007000300004-1.txt"

    files_ = [f for f in listdir(path_) if isfile(join(path_, f))]

    hed = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'charset': 'utf-8'
    }
    language = "es"

    start = time.process_time()

    terms = []
    cont = 0
    i = 0
    min_terms = 1
    # terms_amount = 2
    while_loop = len(files_)

    while i <= while_loop - 1:
        file_ = files_[i]
        corpus = get_indiv_text(path_ + file_)

        params = {"source_language": language, "corpus": corpus}
        r = requests.post(url, json=params, headers=hed)

        ter = json.loads(r.text)
        if len(ter) >= min_terms:
            terms.append(json.loads(r.text))
            cont += 1

        i += 1

    end = time.process_time()

    # r = []
    # for i in range(terms_amount):
    #     r.append(terms.pop(terms.index(max(terms, key=len))))

    with open(path_ + "../termitup_request/termitup_output.txt", 'w', encoding="utf-8") as f:
        f.write(str(terms))

    print(f"TIME: {end - start}")


def termsuit():
    # path_text = "C:/Users/carlo/Documents/med-terminology/Files_SPACCC/"
    path = "C:/Users/carlo/Documents/med-terminology/TERMSUITE/"
    # instruction = "-Xms256m -Xmx4g -cp termsuite-core-3.0.9.jar fr.univnantes.termsuite.tools.TerminologyExtractorCLI " \
    #               "-t ./TreeTagger/ " \
    #               "-c ./corpus/ " \
    #               "-l es -" \
    #               "-tsv ./output/output.tsv"
    init_mem = 256
    max_mem = 4
    mem_arguments = f"-Xms{init_mem}m -Xmx{max_mem}g"
    path_text = path + "corpus/"
    path_work_dir = path + "corpus_work/"
    treetagger = path + "TreeTagger/"
    path_output = path + "output/"
    lang = "es"
    jar_file = "termsuite-core-3.0.9.jar"
    task = "fr.univnantes.termsuite.tools.TerminologyExtractorCLI"

    files = [f for f in listdir(path_text) if isfile(join(path_text, f))]

    for file in files:
        new_dir = path_work_dir + file[:-4] + '/'
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        shutil.copyfile(path_text + file, new_dir + file)

        instruction = f"java {mem_arguments} -cp {path + jar_file} {task} " \
                      f"-t {treetagger} " \
                      f"-c {path_work_dir} " \
                      f"-l {lang} " \
                      f"--tsv {path_output + file[:-4]}.tsv "
        java = subprocess.call(instruction.split())

        shutil.rmtree(path_work_dir + file[:-4])


if __name__ == "__main__":
    termitup()
    # termsuit()
    pass
