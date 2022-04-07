package project.dataholder;

import java.time.LocalDate;
import java.util.List;

public class UserInput {
    public LocalDate startDate;
    public LocalDate endDate;
    public List<String> currencyCodes;

    public UserInput(LocalDate startDate, LocalDate endDate, List<String> currencyCodes) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.currencyCodes = currencyCodes;
    }

    @Override
    public String toString() {
        return "UserInput{" +
                "startDate=" + startDate +
                ", endDate=" + endDate +
                ", currencyCodes=" + currencyCodes +
                '}';
    }
}

