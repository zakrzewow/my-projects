## Informacje
*****
Przetwarzanie danych z api.nbp.pl.

```java
import project.dataprocessing.*;
```

### Struktura danych
Każdy rekord (kurs waluty / cena złota w danym dniu) jest reprezentowany przez obiekt klasy `Rate`, np.:
```
Rate(code=gbp, date=2014-01-07, rate=5.0308)
```
`code` oznacza kod waluty używany w serwisie NBP (domyślnie pisany małymi literami), w przypadku złota jest to kod ustalony przez nas (w klasie NbpReader, ja ustawiłem na *gold*).

Kolekcję obiektów reprezentuje klasa `RateCollection`:

```
RateCollection([Rate(code=usd, date=2014-01-02, rate=3.0315), Rate(code=usd, date=2014-01-03, rate=3.0517), Rate(code=usd, date=2014-01-07, rate=3.0688), Rate(code=usd, date=2014-01-08, rate=3.0717)])
```

### Pobieranie danych

Do pobierania danych służy klasa ```NbpReader```. Możemy pobrać pojedyczny rekord:

```java
NbpParser.getRate("gold", "2019-02-05");
```
**Output:**
```
Rate(code=gold, date=2019-02-05, rate=157.82)
```
(jeżeli rekord nie istnieje, to zwróci null). Możemy również pobrać rekordy w określonym przedziale czasowym:

```java
NbpParser.getRateCollection("usd", "2015-01-01", "2015-01-08");
```
**Output:**
```
RateCollection([Rate(code=usd, date=2015-01-02, rate=3.5725), Rate(code=usd, date=2015-01-05, rate=3.5975), Rate(code=usd, date=2015-01-07, rate=3.6375), Rate(code=usd, date=2015-01-08, rate=3.6482)])
```

Co więcej, możemy zapisać kilka różnych walut w jednej kolekcji:
```java
RateCollection rateCollection = new RateCollection(
        NbpParser.getRateCollection("usd", "2013-01-01", "2016-12-31"),
        NbpParser.getRateCollection("gbp", "2013-01-01", "2016-12-31"),
        NbpParser.getRateCollection("gold", "2013-01-01", "2016-12-31")
    );
```

Możemy również posortować naszą kolekcję po dacie:
```java
rateCollection.sortByDate();
```

...i wybrać z niej tylko konkretną walutę/waluty:
```java
rateCollection.selectByCode("gold", "usd");
```
