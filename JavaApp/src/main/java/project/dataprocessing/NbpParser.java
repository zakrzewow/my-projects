package project.dataprocessing;

import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;

import java.io.IOException;
import java.lang.reflect.Type;
import java.time.Duration;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class NbpParser {

    private static final String goldCode = "gold";
    private static final String dateFormat = "yyyy-MM-dd";
    private static final int daysLimit = 367;

    public static LocalDate parseDate(String dateString) {
        return LocalDate.parse(dateString, DateTimeFormatter.ofPattern(dateFormat));
    }

    public static Rate getRate(String code, String date) {
        return getRate(code, parseDate(date));
    }

    public static Rate getRate(String code, LocalDate date) {
        RateCollection result = getRateCollection(code, date, date);
        if(result.items.size() > 0) {
            return result.items.get(0);
        } else {
            return null;
        }
    }

    public static RateCollection getRateCollection(String code, String startDate, String endDate) {
        return getRateCollection(code, parseDate(startDate), parseDate(endDate));
    }

    public static RateCollection getRateCollection(String code, LocalDate startDate, LocalDate endDate) {
        if(inDaysLimit(startDate, endDate)) {
            return new RateCollection(rateList(code, startDate, endDate), code);
        } else {
            // na wypadek, gdyby został przekroczony limit 367 dni na stronie NBP
            List<RateCollection> rateCollections = new ArrayList<>();
            while(true) {
                if(inDaysLimit(startDate, endDate)) {
                    rateCollections.add(getRateCollection(code, startDate, endDate));
                    break;
                } else {
                    rateCollections.add(getRateCollection(code, startDate, startDate.plusDays(daysLimit - 1)));
                    startDate = startDate.plusDays(daysLimit);
                }
            }
            return new RateCollection(rateCollections.toArray(RateCollection[]::new));
        }
    }

    public static RateCollection getRateCollectionByCodes(List<String> codes, LocalDate startDate, LocalDate endDate) {
        return new RateCollection(
                codes.stream()
                        .map(code -> NbpParser.getRateCollection(code, startDate, endDate))
                        .toArray(RateCollection[]::new)
        );
    }

    private static List<Rate> rateList(String code, LocalDate startDate, LocalDate endDate) {
        try {
            return getGson().fromJson(
                    isGoldCode(code) ? goldJsonString(startDate, endDate) : currencyJsonString(code, startDate, endDate),
                    new TypeToken<List<Rate>>(){}.getType()
            );
        } catch(IOException e) {
            e.printStackTrace();
            return new ArrayList<>();
        } catch(JsonParseException e) {
            return new ArrayList<>();
        }
    }

    private static boolean inDaysLimit(LocalDate startDate, LocalDate endDate) {
        return Duration.between(startDate.atStartOfDay(), endDate.atStartOfDay()).toDays() < daysLimit;
    }

    private static boolean isGoldCode(String code) {
        return code.equalsIgnoreCase(goldCode);
    }

    private static Gson getGson() {
        //tworzy obiekt Gson zdolny do parsowania daty
        class LocalDateDeserializer implements JsonDeserializer<LocalDate> {
            @Override
            public LocalDate deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
                return LocalDate.parse(jsonElement.getAsString(),
                        DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            }
        }

        GsonBuilder gsonBuilder = new GsonBuilder();
        gsonBuilder.registerTypeAdapter(LocalDate.class, new LocalDateDeserializer());
        return gsonBuilder.setPrettyPrinting().create();
    }

    private static String currencyJsonString(String code, LocalDate startDate, LocalDate endDate) throws IOException {
        return (new Gson().fromJson(getJsonFromUrl(currencyURL(code, startDate, endDate)), JsonObject.class).get("rates")).toString();
    }

    private static String goldJsonString(LocalDate startDate, LocalDate endDate) throws IOException {
        return getJsonFromUrl(goldURL(startDate, endDate));
    }

    private static String currencyURL(String code, LocalDate startDate, LocalDate endDate) {
        return "http://api.nbp.pl/api/exchangerates/rates/a/" + code.toLowerCase() + "/" + startDate.toString() + "/" + endDate.toString() + "/?format=json";
    }

    private static String goldURL(LocalDate startDate, LocalDate endDate) {
        return "http://api.nbp.pl/api/cenyzlota/" + startDate.toString() + "/" + endDate.toString() + "?format=json";
    }

    private static String getJsonFromUrl(String url) throws IOException {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url(url)
                .build();
        try (Response response = client.newCall(request).execute()) {
            ResponseBody body = response.body();
            return body == null ? "" : body.string();
        }
    }

}