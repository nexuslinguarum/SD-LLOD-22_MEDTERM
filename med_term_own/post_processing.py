import pandas as pd
import numpy as np


def get_common_words(path):
    with open(path + "common_words.txt", 'r', encoding="utf-8") as f:
        words = f.read()

    return words.split('\n')


def get_terms(path, doc):
    df = pd.read_csv(path + doc, encoding="latin-1", delimiter="\t", header=None, usecols=[1, 2], names=['terms', 'tags'])
    df = df.drop_duplicates().reset_index(drop=True)

    return df


def del_common_terms(df, common_terms):
    del_index = []
    del_terms = ""
    common_terms = [ele.lower() for ele in common_terms]

    for i in range(len(df)):
        if df.loc[[i]]['terms'].values[0].lower() in common_terms:
            del_index.append(i)
            del_terms += f"{df.loc[[i]]['terms'].values[0].lower()}\n"

    df = df.drop(del_index, axis=0).reset_index(drop=True)

    return df, del_terms


def post_process():
    pass


def main():
    save_path = "./post_processing_files/"
    data_path = "./data/"

    # path = 'C:/Users/carlo/Documents/med-terminology/termitup_request/'
    # save_path = path + "post_processing_files/"
    # data_path = path + "data/"
    doc = "Text2TCS_results_pos.txt"

    common_words = get_common_words(data_path)
    df = get_terms(data_path, doc)

    df, del_terms = del_common_terms(df, common_words)
    df.to_csv(save_path + "Text2TCS_filtered_common_terms.csv", encoding="utf-8", sep="\t")
    with open(save_path + "deleted_terms.txt", 'w', encoding="utf-8") as f:
        f.write(str(del_terms))


if __name__ == "__main__":
    main()
    pass
