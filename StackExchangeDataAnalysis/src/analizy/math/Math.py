import json
import re

import pandas as pd

from src.analizy.common.parse.Parser import getData

FORUM_DIRECTORY_NAME = "math.stackexchange.com"


def guessCountry(location: str, statesCodeList, countryList):
    '''
    lokalizacja dzieli się na 2 główne kategorie:
        zawierającą jedynie kod stanu w USA
        zawierającą nazwę kraju

    algorytm opiera się na założeniu, że ludzie mieszkający poza USA napisaliby całą nazwę kraju a nie kod
    :param location: string zawierający lokalizację
    :return: string zawierający nazwę kraju
    '''

    if type(location) is str:
        data = location.split(',')[-1]

        if data in statesCodeList:
            return "United States"

        # bardzo podejrzane xd
        for country in countryList:
            if re.search(country, data, flags=re.IGNORECASE):
                return country
    return None


def assignCountry(UsersDF: pd.DataFrame, statesCodeList, countryList):
    '''
    na podstawie lokacji przypisuje kraj
    :param UsersDF: ramka danych z polem 'Location'
    :return: ramka danych z dodanym polem 'kraj'
    '''
    return UsersDF.assign(
        kraj=lambda DataFrame: DataFrame['Location'].map(lambda x: guessCountry(x, statesCodeList, countryList)))


def demoStatesCountries(countriesDF: pd.DataFrame, statesDF: pd.DataFrame):
    '''
    pokazuje, które kody dla kraju powtarzają się z kodami dla stanu
    :param countriesDF: ramka danych z krajami
    :param statesDF: ramka danych ze stanami
    :return: nic 
    '''
    print(countriesDF.merge(statesDF, how="inner", left_on="code", right_on="Code", suffixes=('_countries', '_states')))


def normalizedAnswerScores(PostsDF: pd.DataFrame, UsersDF: pd.DataFrame):
    '''
    bierze posty i urzytkowników już z 'kraj' zwraca medianę 'score' odpowiedzi dla każdego kraju
    :param PostsDF:
    :param UsersDF:
    :return:
    '''

    def filterAnwsers(PostsDF: pd.DataFrame):
        '''
        :param PostsDF: ramka z postami
        :return: ramka z odpowiedziami
        '''
        return PostsDF.loc[PostsDF['PostTypeId'] == "2"]

    def joinUsersPosts(Users: pd.DataFrame, Anwsers: pd.DataFrame):
        '''
        :param UsersDF: ramka z urzytkownikami z lokacją
        :param Anwsers: ramka odpowiedzi
        :return: ramka z przyporządkowanymi urzytkownikom odpowiedziami i kolumnami 'kraj', 'Score'
        '''
        return Users.merge(right=Anwsers, how="inner", left_on="Id", right_on="OwnerUserId",
                           suffixes=('_Users', '_Posts')).loc[:, ['kraj', 'Score']]

    def sumScore(UsersDF: pd.DataFrame, PostsDF: pd.DataFrame):
        return joinUsersPosts(UsersDF, filterAnwsers(PostsDF)).groupby('kraj').sum()

    def countAnwsers(UsersDF: pd.DataFrame, PostsDF: pd.DataFrame):
        return joinUsersPosts(UsersDF, filterAnwsers(PostsDF)).groupby('kraj').count()

    return (sumScore(UsersDF, PostsDF)['Score'] / countAnwsers(UsersDF, PostsDF)['Score']).sort_values(ascending=False)


##

def countCountryUsers(df: pd.DataFrame) -> pd.Series:
    """
    Grupuje i liczy użytkowników po kraju
    :param df: ramka danych Users z przypisanymi krajami
    :return: series zawierający informację o liczbie użytkowników dla każdego kraju
    """
    df = df.loc[df["kraj"].notnull(), ["Id", "kraj"]]
    df = df.groupby("kraj").size()
    df.index.name = "kraj"
    df = df.sort_values(ascending=False)
    return df


##

def countCountryPosts(Users: pd.DataFrame, Posts: pd.DataFrame) -> pd.Series:
    """
    Grupuje i liczy posty użytkowników po kraju
    :param Users: ramka danych Users z przypisanymi krajami
    :param Posts: ramka danych Posts
    :return: series zawierający informację o liczbie postów napisanych przez użytkowników z danego kraju
    """
    df = pd.merge(Users.loc[Users["kraj"].notnull(), ["Id", "kraj"]], Posts.loc[:, ["Id", "OwnerUserId"]],
                  left_on="Id", right_on="OwnerUserId", suffixes=("_users", "_posts"))
    df = df.groupby("kraj").size()
    return df


##

def postsToUsersRatio(usersCounted: pd.Series, postsCounted: pd.Series) -> pd.DataFrame:
    """
    Łączy liczbę użytkowników i liczbę postów dla każdego kraju, liczy stosunek użytkowników do postów
    :param usersCounted: wynik działania funkcji countCountryUsers
    :param postsCounted: wynik działania funkcji countCountryPosts
    :return: trzy-kolumnową ramkę danych: dla każdego występującego kraju liczbę uzytkowników, postów i stosunek
    """
    usersCounted = usersCounted.to_frame().reset_index()
    postsCounted = postsCounted.to_frame().reset_index()

    df = pd.merge(usersCounted, postsCounted, on="kraj")
    df = df.sort_values(by=["0_x"], ascending=False)
    df = df.set_index("kraj")
    df.columns = ["l. użytkowników", "l. postów"]
    df = df.assign(Ratio=(df["l. postów"] / df["l. użytkowników"]))
    return df


if __name__ == "__main__":
    UsersDF = getData(f"../../../resources/{FORUM_DIRECTORY_NAME}/Users.xml")
    PostsDF = getData(f"../../../resources/{FORUM_DIRECTORY_NAME}/Posts.xml")
    PostsDF['Score'] = pd.to_numeric(PostsDF['Score'])

    with open("../../../resources/keeguon_countries/countries.json") as file:
        countries = json.load(file)
    with open("../../../resources/state_codes/data.json") as file:
        states = json.load(file)

    countriesDF = pd.json_normalize(countries)
    statesDF = pd.json_normalize(states)
    statesCodeList = statesDF['Code'].to_list()
    countryList = countriesDF['name'].to_list()
    # pamięć jest cenna!
    del countries
    del states
    del countriesDF
    del statesDF

    # przypisanie kraju do użytkownika
    UsersDF = assignCountry(UsersDF, statesCodeList, countryList)

    # liczenie użytkowników na kraj
    usersCounted = countCountryUsers(UsersDF)
    usersCounted.to_csv(f"data/{FORUM_DIRECTORY_NAME}/users_counted.csv")

    # liczenie postów na kraj i ich stosunku do liczby użytkowników
    postsCounted = countCountryPosts(UsersDF, PostsDF)
    df = postsToUsersRatio(usersCounted, postsCounted)
    df.to_csv(f"data/{FORUM_DIRECTORY_NAME}/posts_to_users_ratio.csv")

    # liczneie unormalizowanego stosunku punktów do liczby odpowiedzi na kraj

    df = normalizedAnswerScores(PostsDF, UsersDF)
    df.to_csv(f"data/{FORUM_DIRECTORY_NAME}/normalized_answer_score.csv")
