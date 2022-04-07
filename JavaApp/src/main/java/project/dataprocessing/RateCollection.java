package project.dataprocessing;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

public class RateCollection {

    public List<Rate> items = new ArrayList<>();

    public RateCollection(List<Rate> items) {
        this.items = items;
    }

    public RateCollection(List<Rate> items, String code) {
        this(items);
        setCode(code);
    }

    public RateCollection(RateCollection... rateCollections) {
        for(RateCollection rateCollection : rateCollections)
            if(rateCollection != null)
                items.addAll(rateCollection.items);
    }

    @Override
    public String toString() {
        return "RateCollection(" + items.toString() + ")";
    }

    public String toFormat(String format) {
        switch(format.toUpperCase()) {
            case "JSON":
                return items.stream().map(item -> item.toFormat("JSON")).toList().toString();
            case "CSV":
                return "code,date,rate\n" +
                        items.stream().map(item -> item.toFormat("CSV")).collect(Collectors.joining("\n"));
        }

        return null;
    }

    private void setCode(String code) {
        items.forEach(item -> item.setCode(code));
    }

    public RateCollection selectByCode(String... codes) {
        return new RateCollection(items.stream().filter(item -> Arrays.asList(codes).contains(item.getCode())).toList());
    }

    public void sortByDate() {
        items.sort(Comparator.comparing(Rate::getDate));
    }

    public List<Double> getValues() {
        return items.stream().map(Rate::getValue).toList();
    }

    public List<LocalDate> getDates() {
        return items.stream().map(Rate::getDate).toList();
    }

}
