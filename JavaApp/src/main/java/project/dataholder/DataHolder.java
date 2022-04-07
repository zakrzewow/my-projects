package project.dataholder;

import project.dataprocessing.NbpParser;
import project.dataprocessing.RateCollection;

import java.util.HashMap;
import java.util.Map;

public class DataHolder {
    private static final Map<String, RateCollection> rates = new HashMap<>();
    private static UserInput userInput;

    public static void fetchRatesFromServer(UserInput userInput) {
        rates.clear();
        DataHolder.userInput = userInput;
        for (String currencyCode: userInput.currencyCodes) {
            RateCollection rate = NbpParser.getRateCollection(currencyCode, userInput.startDate, userInput.endDate);
            rates.put(currencyCode, rate);
        }
    }

    public static Map<String, RateCollection> getRates() {
        return rates;
    }

    public static UserInput getUserInput() {
        return userInput;
    }

    public static boolean isEmpty() {
        return rates.isEmpty();
    }
}
