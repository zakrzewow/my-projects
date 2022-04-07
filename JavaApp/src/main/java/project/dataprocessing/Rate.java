package project.dataprocessing;

import com.google.gson.annotations.SerializedName;

import java.time.LocalDate;

public class Rate {

    @SerializedName(value = "mid", alternate = "cena")
    private double rate;

    @SerializedName(value = "effectiveDate", alternate = "data")
    private LocalDate date;

    private String code;

    public Rate(String code, LocalDate date, double rate) {
        this.code = code.toLowerCase();
        this.date = date;
        this.rate = rate;
    }

    public Rate(String code, String date, double rate) {
        this(code, NbpParser.parseDate(date), rate);
    }

    @Override
    public String toString() {
        return "Rate(code=" + code + ", date=" + date.toString() + ", rate=" + rate + ")";
    }

    public String toFormat(String format) {
        switch(format.toUpperCase()) {
            case "JSON":
                return "{\"code\": \"" + code + "\", \"date\": \"" + date.toString() + "\", \"rate\": " + rate + "}";
            case "CSV":
                return code + "," + date + "," + rate;
        }
        return null;
    }

    public double getValue() {
        return rate;
    }

    public LocalDate getDate() {
        return date;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code.toLowerCase();
    }

}
