import re

import pandas as pd

from src.analizy.common.parse.Parser import getData

FORUM_DIRECTORY_NAME = "parenting.stackexchange.com"


def guessGenderOld(string: str):
    '''
    działa szukając regexem słów jak her/his daughter/son w ciele postu
        opcjonalne:
            dodać wyszukiwanie tażke w tytule

    :param string: body postu
    :return: K - jeśli tytuł sugeruje kobietę, M - jeśli tytuł sugeruje mężczyznę, None jeśli niewiadomo
    '''
    if re.search(r'(\W[hH]er\W )|(\W[Ss]he\W)|(\W[Dd]aughter\W)', string) and not re.search(
            r'(\W[Hh]is\W)|(\W[Hh]e\W)|(\W[Ss]on\W)', string):
        # jest dziewczynką
        return 'K'
    elif re.search(r'(\W[Hh]is\W)|(\W[Hh]e\W)|(\W[Ss]on\W)', string) and not re.search(
            r'(\W[hH]er\W )|(\W[Ss]he\W)|(\W[Dd]aughter\W)', string):
        # jest chłopcem

        return 'M'
    else:
        return None


def guessGender(string: str):
    '''
    działa szukając regexem słów jak her/his daughter/son w ciele postu
        opcjonalne:
            dodać wyszukiwanie tażke w tytule

    :param string: body postu
    :return: K - jeśli tytuł sugeruje kobietę, M - jeśli tytuł sugeruje mężczyznę, None jeśli niewiadomo
    '''
    if re.search(r'(\W[Dd]aughter\W)', string) and not re.search(
            r'(\W[Ss]on\W)', string):
        # jest dziewczynką
        return 'K'
    elif re.search(r'(\W[Ss]on\W)', string) and not re.search(
            r'(\W[Dd]aughter\W)', string):
        # jest chłopcem
        return 'M'
    elif re.search(r'(\W[hH]ers?\W )|(\W[Ss]he\W)', string) and not re.search(r'(\W[hH]i[sm]\W )|(\W[Hh]e\W)', string):
        return 'K'
    elif re.search(r'(\W[hH]i[sm]\W )|(\W[Hh]e\W)', string) and not re.search(r'(\W[hH]ers?\W )|(\W[Ss]he\W)', string):
        return 'M'
    else:
        return None


def addGender(dataFrame: pd.DataFrame):
    '''
    :param dataFrame: ramka danych z kolumną 'Body'
    :return: ramka danych z dodatkową kolumną 'plec'
    '''
    return dataFrame.assign(plec=lambda dataframe: dataframe['Body'].map(guessGender))


def summarizeGender(dataFrame: pd.DataFrame):
    # test czy sprawdzanie płci działa zadowalająco
    '''

    :param dataFrame: ramka danych z polem plec i Id
    :return: ramka pogrupowana po plec z liczba odpowiadajacych im wpisow
    '''
    return dataFrame.loc[:, ['Id', 'plec']].groupby(by='plec', dropna=False).count()


def addPostsToUsers(Users: pd.DataFrame, Posts: pd.DataFrame):
    '''
    filtruje Posty po plec jeśli nie ma plci to ich wyrzuca

    przypisuje Userom płeć dziecka
    :param Users: świeża ramka users
    :param Posts: ramka posts z dodaną płcią
    :return: ramka przypisująca userowi jego posty
    '''
    # Posts = Posts.loc[Posts['plec'].notna()]
    return Posts.merge(right=Users, how='inner', left_on='OwnerUserId', right_on='Id', suffixes=('_Posts', '_Users'))


def guessAge(Posts: pd.DataFrame):
    def findAgeByRegex(string: str):
        '''
        w tytule/ ciele posta może być napisany wiek jako 1.5Yo 4YO 4 years old 4 Years old itd.
        :param string: pole gdzie szukamy wieku
        :return: przewidywany wiek (float)
        '''
        possible = re.findall(r'(?:\d\.)?\d{1,2}\W?[Yy](?:[oO]|ears? old)', string)
        if len(possible) < 1:
            return None
        return min([int(re.findall(r'\d{1,2}', i)[0]) for i in possible])

    def guessByTags(string: str):
        '''
        w tagach są "infant","toddler","adult-child","newborn","pre-schooler","primary-schooler","adolescent" można próbować dać dzieciom wiek
        :param string: tagi posta
        :return: str: tag opisujący wiek dzieciaka
        '''
        if re.search(r'infant', string):
            return "infant"
        elif re.search(r'toddler', string):
            return "toddler"
        elif re.search(r'adult-child', string):
            return "adult-child"
        elif re.search(r'newborn', string):
            return "newborn"
        elif re.search(r'pre-schooler', string):
            return "pre-schooler"
        elif re.search(r'primary-schooler', string):
            return "primary-schooler"
        elif re.search(r'adolescent', string):
            return "adolescent"
        return None

    def guessAllBody(string: str):
        age = findAgeByRegex(string)
        if age is None:
            age = guessByTags(string)
        return age

    def guessAll(body: str, tags: str):
        tmp = guessAllBody(body)
        if tmp is None and type(tags) is str:
            tmp = guessByTags(tags)
        return tmp

    '''
    :param Posts: ramka danych z polem body lub Title
    :return: dodaje ramce danych przewidywany wiek dziecka
    '''
    Posts['wiekDzieciaka'] = Posts.apply(lambda x: guessAll(body=x['Body'], tags=x['Tags']), axis=1)
    return Posts


def ulepszDzieciaki(DzieciakiDF: pd.DataFrame):
    '''
    wybiera tylko dzieciaki z wiekiem i płcią
    :param DzieciakiDF: ramka danych z dzieciakami (zawierza kolumny plec i wiekDzieciaka)
    :return: ramka z dzieciakami co mają wiek i płeć
    '''
    DobreDzieciaki = DzieciakiDF.loc[DzieciakiDF['plec'].notnull()]
    DobreDzieciaki = DobreDzieciaki.loc[DobreDzieciaki['wiekDzieciaka'].notnull()]
    return DobreDzieciaki


def wiekNaGrupe(Dzieciaki: pd.DataFrame):
    '''
    newborn -> 0 infant -> 0-1 toddler-> 1-4 pre-schooler-> 4-5? primary-schooler->6-12 adolescent->13-18 adult-child->19-21
    :param Dzieciaki: ramka danych z polem wiekDzieciaka
    :return: ramka danych gdzie wiek zamieniony jest na grupę
    '''

    def zamien(obiekt):
        if obiekt is None:
            # do wygenerowania age_groups_withNA
            # return "None"
            return None
        if type(obiekt) is not str:
            if obiekt < 0.2:
                return "newborn"
            elif obiekt < 1:
                return "infant"
            elif obiekt < 4:
                return "toddler"
            elif obiekt < 5:
                return "pre-schooler"
            elif obiekt < 12:
                return "primary-schooler"
            elif obiekt < 18:
                return "adolescent"
            else:
                return "adult-child"
        else:
            return obiekt

    return Dzieciaki.assign(grupaWiekowa=lambda df: df['wiekDzieciaka'].map(zamien))


if __name__ == "__main__":
    UsersDF = getData(f"../../../resources/{FORUM_DIRECTORY_NAME}/Users.xml")
    PostsDF = getData(f"../../../resources/{FORUM_DIRECTORY_NAME}/Posts.xml")

    DzieciakiDF = addPostsToUsers(UsersDF, guessAge(addGender(PostsDF))).loc[:,
                  ['DisplayName', 'plec', 'wiekDzieciaka', 'CreationDate_Posts']]

    # stosunek płci dzieci
    df = DzieciakiDF["plec"].value_counts(dropna=False)
    df.name = "Płeć"
    df.to_csv(f"data/{FORUM_DIRECTORY_NAME}/gender_ratio.csv")

    # podział dzieci na grupy wiekowe
    df = wiekNaGrupe(ulepszDzieciaki(DzieciakiDF)).groupby(['grupaWiekowa', 'plec']).size().unstack(1)
    new_index = ["newborn", "infant", "toddler", "pre-schooler", "primary-schooler", "adolescent", "adult-child"]
    df = df.reindex(new_index)
    df.to_csv(f"data/{FORUM_DIRECTORY_NAME}/age_groups.csv")
    '''
    ten kod generuje age_groups_withNA
    trzeba odkomentować w zamien() linijke i zakomentować drugą
    df = wiekNaGrupe(DzieciakiDF).groupby(['grupaWiekowa']).size()
    new_index = ["newborn", "infant", "toddler", "pre-schooler", "primary-schooler", "adolescent", "adult-child"]
    df = df.reindex(new_index)
    df.to_csv(f"data/{FORUM_DIRECTORY_NAME}/age_groups_withNA.csv")
    '''
