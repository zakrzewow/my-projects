import numpy as np
import pandas as pd

from src.analizy.common.parse.Parser import getData

FORUM_DIRECTORY_NAME = "ai.stackexchange.com"


##

def countPostsPerMonth(df: pd.DataFrame) -> pd.Series:
    """
    Liczy sumę postów w każdym miesiącu
    :param df: ramka danych Posts
    :return: series zawierający dla każdego miesiąca sumę postów
    """
    df = df.loc[:, ["CreationDate"]].resample("M", on="CreationDate")
    return df.count()


##

def countQuestionsAndAnswersPerMonth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Liczy sumę pytań i odpowiedzi w każdym miesiącu
    :param df: ramka danych Posts
    :return: ramka danych zawierająca dla każdego miesiąca sumę postów i odpowiedzi
    """
    df = df[pd.to_numeric(df["PostTypeId"]) <= 2]
    df = df.loc[:, ["CreationDate", "PostTypeId"]]
    df = df.groupby("PostTypeId").resample("M", on="CreationDate").count()
    df = df["PostTypeId"].unstack(0)
    df.rename(columns={'1': 'Pytania', '2': 'Odpowiedzi'}, inplace=True)
    return df


##

def countQuestionsWithAcceptedAnswer(df: pd.DataFrame) -> pd.Series:
    """
    Liczy posty posiadające zaakceptowaną odpowiedź i nie
    :param df: ramka danych Posts
    :return: series zawierający informację ile postów ma zaakceptowaną odpoweidź, a ile nie
    """
    df = df.loc[df["PostTypeId"] == "1", "AcceptedAnswerId"]
    df = pd.isna(df)
    df = df.value_counts()
    df.name = "Jest zaakceptowana odpowiedź?"
    df = df.rename(index={True: "Tak", False: "Nie"})
    return df


##

def getGreatSummary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tworzy wielkie podsumowanie ilości i częstotliwości pojawiania się postów na forum

    Pierwsza kolumna: która to jest odpowiedź: pierwsza, druga, trzecia-piąta, szósta-dziesiąta, kolejna
    Druga kolumna: ile pytań ma odpowiednio pierwszą, drugą, ...., odpowiedź; wartość procentowa: jaka część pytań ma
    i-tą odpowiedź, liczba tych i-tych odpowiedzi

    Kolejne pięc kolumn mówi nam, ile z tych i-tych odpowiedzi zostało udzielonych odpowiedno w czasie do godziny,
    jedną godziną a jednym dniem, dniem a tygodniem, tygodniem a miesiącem oraz później; wartość procentowa w stosunku
    do liczby i-tych odpowiedzi i liczba

    :param df: ramka danych Posts
    :return: wyżej opisana ramka danych, to przedstawienia w postaci tabeli za pomocą markdown
    """
    # oryginalna ramka
    postsDf = df.copy()

    # wybór odpowiedzi, dla każdej odpowiedzi znalezienie pytania, policzenie różnicy czasowej między pytaniem a odpowiedzą
    df = df.loc[df["PostTypeId"] == "2", ["Id", "ParentId", "CreationDate"]]
    df = pd.merge(df, postsDf.loc[:, ["Id", "CreationDate"]], left_on="ParentId",
                  right_on="Id", suffixes=("_answer", "_question"))
    df["TimeDelta"] = df["CreationDate_answer"] - df["CreationDate_question"]

    # funckja pomocnicza
    def cutIntoBins(value, borders, labels, unmatchedLabel):
        """
        Segreguje wartości do przedziałów z prawej strony domkniętych
        :param value: wartość do segregacji
        :param borders: prawe granice przedziałów, typ porównywalny z value
        :param labels: nazwy przedziałów
        :param unmatchedLabel: nazwa ostatniego przedziału
        :return: nazwa przedziału, do którego trafia value
        """
        assert len(borders) == len(labels)
        for i in range(len(borders)):
            if value <= borders[i]:
                return labels[i]
        return unmatchedLabel

    # pomocnicza ramka danych, pogrupowanie odpowiedzi po id pytania, by wiedzieć, jako która z kolei pojawiła się
    # dana odpowiedź
    tmp = postsDf
    tmp = postsDf.loc[tmp["PostTypeId"] == "2", ["Id", "CreationDate", "ParentId"]].groupby(["ParentId"])

    def getAnswerNumber(answerId: str, parentId: str):
        """
        :param answerId:
        :param parentId:
        :return: numer odpowiedz (czy jest to pierwsza, druga, i-ta odpowiedź na pytanie)
        """
        group = tmp.get_group(parentId)
        return np.where(group["Id"] == answerId)[0][0] + 1

    # Zamiana czasu powstania odpowiedzi na odpowiedznie określenie
    df = df.assign(TimeDeltaDesc=df['TimeDelta'].map(
        lambda x: cutIntoBins(x, [pd.Timedelta(hours=1), pd.Timedelta(days=1), pd.Timedelta(weeks=1),
                                  pd.Timedelta(weeks=4)],
                              ["Hour", "Day", "Week", "Month"], "Later...")
    ))
    # Zamiana numeru odpowiedzi na odpowiednią grupę
    df = df.assign(AnswerNumber=df.apply(lambda x: getAnswerNumber(x['Id_answer'], x['ParentId']), axis=1).map(
        lambda x: cutIntoBins(x, [1, 2, 5, 10], ["1", "2", "3-5", "6-10"], "11+")
    ))
    # grupowanie
    df = df.loc[:, ["AnswerNumber", "ParentId", "TimeDeltaDesc"]].groupby(["AnswerNumber", "TimeDeltaDesc"]).count()
    df = df.unstack(1)
    # dodanie kolumny - suma i-tych odpowiedzi
    df = df.assign(AnswerCount=df.apply(np.sum, axis=1))

    # porządkowanie, dodanie wartości procentowych
    df = df.fillna(0)
    df["ParentId"] = df["ParentId"].applymap(lambda x: str(int(x)))
    for index, row in df.iterrows():
        d = {}
        for i in ["Hour", "Day", "Week", "Month", "Later..."]:
            value = row[("ParentId", i)]
            df.at[index, ("ParentId", i)] = "{p:.0f}% ({v})".format(p=float(value) / row["AnswerCount"][0] * 100,
                                                                    v=value)

    # liczenie stosunku do wszystkich pytań
    total = postsDf.loc[postsDf["PostTypeId"] == "1", :].shape[0]
    df['AnswerCount'] = df['AnswerCount'].map(lambda x: "{p:.0f}% ({v})".format(p=x / total * 100, v=int(x)))

    # sortowanie wierszy, kolumn
    df = df.reindex(['1', '2', '3-5', '6-10', '11+'])
    df.columns = df.columns.droplevel()
    df.columns.name = "Która odpowiedź?"
    df.index.name = None
    df = df.rename(columns={"": "Total"})
    df = df.reindex(columns=['Total', 'Hour', 'Day', 'Week', 'Month', 'Later...'])

    return df


if __name__ == "__main__":
    PostsDF = getData(f'../../../resources/{FORUM_DIRECTORY_NAME}/Posts.xml')
    PostsDF["CreationDate"] = pd.to_datetime(PostsDF["CreationDate"])

    # utworzone pliki .csv są czytane podczas kompliowania prezentacji
    countPostsPerMonth(PostsDF).to_csv(f"data/{FORUM_DIRECTORY_NAME}/posts_per_month.csv")
    countQuestionsAndAnswersPerMonth(PostsDF).to_csv(f"data/{FORUM_DIRECTORY_NAME}/questions_and_answers_per_month.csv")
    countQuestionsWithAcceptedAnswer(PostsDF).to_csv(f"data/{FORUM_DIRECTORY_NAME}/questions_with_accepted_answer.csv")

    # wymaga pakietu tabulate
    tmp = getGreatSummary(PostsDF).to_markdown()
    with open(f"data/{FORUM_DIRECTORY_NAME}/greatSummatyTable.txt", "w") as f:
        f.write(tmp)

    # wygenerowaną tabelę należy przekopiować z pliku i wkleić do prezentacji
